import configparser
import logging
import shlex
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from pglift._compat import Self
from pglift.models.system import PostgreSQLInstance
from pglift.settings import PgBackRestSettings


@dataclass
class PgbackrestRepoHost:
    client_configpath: Path
    server_configpath: Path
    logpath: Path
    port: int
    path: Path
    client_cn: str
    server_cn: str
    ca_file: Path
    server_certfile: Path
    server_keyfile: Path

    logger: logging.Logger

    # Use low timeout values to avoid getting stuck long.
    archive_timeout: int = 1
    io_timeout: int = 1
    db_timeout: int = 1

    proc: Optional[subprocess.Popen[str]] = field(default=None, init=False)

    def __post_init__(self) -> None:
        cp = configparser.ConfigParser(strict=True)
        cp.add_section("global")
        cp["global"] = {
            "repo1-path": str(self.path),
            "repo1-retention-full": "2",
            "tls-server-address": "*",
            "tls-server-ca-file": str(self.ca_file),
            "tls-server-cert-file": str(self.server_certfile),
            "tls-server-key-file": str(self.server_keyfile),
            "tls-server-auth": f"{self.client_cn}=*",
            "tls-server-port": str(self.port),
            "log-level-console": "off",
            "log-level-file": "detail",
            "log-level-stderr": "info",
            "log-path": str(self.logpath),
        }
        with self.server_configpath.open("w") as f:
            cp.write(f)

        with self.edit_config() as cp:
            cp.add_section("global")
            cp["global"] = {
                "repo1-path": str(self.path),
                "repo1-retention-full": "2",
                "start-fast": "y",
                "archive-timeout": str(self.archive_timeout),
                "log-level-console": "off",
                "log-level-file": "detail",
                "log-level-stderr": "info",
                "log-path": str(self.logpath),
            }

    def cmd(self, *args: str) -> list[str]:
        """Build a pgbackrest client command."""
        return ["pgbackrest", "--config", str(self.client_configpath)] + list(args)

    def __enter__(self) -> Self:
        assert self.proc is None, "process already started"
        self.proc = subprocess.Popen(
            ["pgbackrest", "server", "--config", str(self.server_configpath)], text=True
        )
        self.proc.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        assert self.proc is not None, "process not started"
        self.proc.terminate()
        self.proc.__exit__(*args)
        self.proc = None

    @contextmanager
    def edit_config(self) -> Iterator[configparser.ConfigParser]:
        cp = configparser.ConfigParser(strict=True)
        if self.client_configpath.exists():
            with self.client_configpath.open() as f:
                cp.read_file(f)
        yield cp
        with self.client_configpath.open("w") as f:
            cp.write(f)

    def add_stanza(
        self, name: str, instance: PostgreSQLInstance, index: int = 1
    ) -> None:
        settings = instance._settings
        pgbackrest_settings = settings.pgbackrest
        assert pgbackrest_settings is not None
        host_config_path = pgbackrest_settings.configpath
        assert isinstance(
            pgbackrest_settings.repository, PgBackRestSettings.HostRepository
        )
        host_port = pgbackrest_settings.repository.port
        user = settings.postgresql.backuprole.name
        socket_path = settings.postgresql.socket_directory
        pg = f"pg{index}"
        with self.edit_config() as cp:
            if not cp.has_section(name):
                cp.add_section(name)
            cp[name].update(
                {
                    f"{pg}-host": self.client_cn,
                    f"{pg}-host-port": str(host_port),
                    f"{pg}-host-type": "tls",
                    f"{pg}-host-config-path": str(host_config_path),
                    f"{pg}-host-ca-file": str(self.ca_file),
                    f"{pg}-host-cert-file": str(self.server_certfile),
                    f"{pg}-host-key-file": str(self.server_keyfile),
                    f"{pg}-path": str(instance.datadir),
                    f"{pg}-port": str(instance.port),
                    f"{pg}-user": user,
                    f"{pg}-socket-path": str(socket_path),
                }
            )
        self.run(
            "server-ping",
            "--io-timeout",
            str(self.io_timeout),
            "--tls-server-address",
            self.client_cn,
            "--tls-server-port",
            str(host_port),
        )
        self.run("stanza-create", "--stanza", name, "--no-online")
        self.run("verify", "--stanza", name)
        self.run("repo-ls")
        self.check(name)

    def check(self, stanza: str) -> None:
        self.run(
            "check",
            "--stanza",
            stanza,
            "--no-archive-check",
            "--io-timeout",
            str(self.io_timeout),
            "--db-timeout",
            str(self.db_timeout),
        )

    def run(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run a pgbackrest client command from the repository."""
        cmd = self.cmd(*args)
        self.logger.debug("running: %s", shlex.join(cmd))
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as p:
            assert p.stderr is not None
            stderr = []
            for errline in p.stderr:
                self.logger.debug("%s: %s", args[0], errline.rstrip())
                stderr.append(errline)
            assert p.stdout is not None
            stdout = p.stdout.read()
        if p.returncode != 0:
            raise subprocess.CalledProcessError(p.returncode, p.args)
        return subprocess.CompletedProcess(
            p.args, p.returncode, stdout=stdout, stderr="".join(stderr)
        )
