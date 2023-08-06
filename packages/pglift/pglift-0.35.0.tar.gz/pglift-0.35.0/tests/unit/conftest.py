import pathlib
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Callable, Optional
from unittest.mock import MagicMock, patch

import pydantic
import pytest

from pglift import plugin_manager
from pglift.ctx import Context
from pglift.models import interface
from pglift.models.system import Instance
from pglift.pgbackrest import models as pgbackrest_models
from pglift.pm import PluginManager
from pglift.prometheus import impl as prometheus_mod
from pglift.prometheus import models as prometheus_models
from pglift.settings import Settings, SystemdSettings
from pglift.temboard import impl as temboard_mod
from pglift.temboard import models as temboard_models


def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        "--write-changes",
        action="store_true",
        default=False,
        help="Write-back changes to test data.",
    )


@pytest.fixture
def write_changes(request: Any) -> bool:
    value = request.config.option.write_changes
    assert isinstance(value, bool)
    return value


@pytest.fixture
def pg_version() -> str:
    return "15"


@pytest.fixture
def pgbackrest_execpath(tmp_path: Path) -> Path:
    execpath = tmp_path / "pgbackrest"
    execpath.touch(0o700)
    execpath.write_text("#!/bin/sh\nexit 1\n")
    return execpath


@pytest.fixture
def prometheus_execpath(tmp_path: Path) -> Path:
    execpath = tmp_path / "postgres_exporter"
    execpath.touch(0o700)
    execpath.write_text("#!/bin/sh\nexit 1\n")
    return execpath


@pytest.fixture
def temboard_execpath(tmp_path: Path) -> Path:
    execpath = tmp_path / "temboard-agent"
    execpath.touch(0o700)
    execpath.write_text("#!/bin/sh\nexit 1\n")
    return execpath


@pytest.fixture
def patroni_execpath(tmp_path: Path) -> Path:
    execpath = tmp_path / "patroni"
    execpath.touch(0o700)
    execpath.write_text(
        "\n".join(
            [
                "#!/bin/sh",
                'if [ "$1" = "--validate-config" ]',
                "then",
                "  echo 'test test test'",
                "fi",
                "exit 1",
            ]
        )
    )
    return execpath


@pytest.fixture
def systemctl(tmp_path: Path) -> Iterator[str]:
    p = str(tmp_path / "systemctl")
    with patch("pglift.settings.SystemdSettings.systemctl", create=True, new=p):
        yield p


@pytest.fixture
def systemd_settings(tmp_path: Path, systemctl: str) -> SystemdSettings:
    return SystemdSettings.parse_obj({"unit_path": str(tmp_path / "systemd")})


@pytest.fixture
def settings(
    tmp_path: Path,
    patroni_execpath: Path,
    pgbackrest_execpath: Path,
    prometheus_execpath: Path,
    temboard_execpath: Path,
    systemd_settings: SystemdSettings,
) -> Settings:
    passfile = tmp_path / "pgass"
    passfile.touch()
    signing_key = tmp_path / "signing-public.pem"
    signing_key.touch()
    ssl_cert_file = tmp_path / "temboard-agent.pem"
    ssl_cert_file.touch()
    ssl_key_file = tmp_path / "temboard-agent.key"
    ssl_key_file.touch()
    ssl_ca_cert_file = tmp_path / "mycacert.pem"
    ssl_ca_cert_file.touch()

    def pg_bindir(path: Path, version: int) -> Path:
        """Make a bindir with minimal versions of pg_* executables.

        - pg_ctl should work for --version and status
        - pg_checksums returns 0, as it's invoked upon instances._get()
        - psql exists, but always fails
        - pg_isready returns 1
        """
        path.mkdir(parents=True)
        pg_ctl = path / "pg_ctl"
        pg_ctl.touch(mode=0o700)
        pg_ctl.write_text(
            "\n".join(
                [
                    "#!/bin/sh",
                    "case $1 in",
                    "  --version)",
                    f"     echo 'pg_ctl (PostgreSQL) {version}.1'",
                    "     exit 0",
                    "     ;;",
                    "  status)",
                    "     exit 3",  # not running
                    "     ;;",
                    "  *)",
                    '     echo "unexpected invocation pg_ctl $1" >&2',
                    "     exit 1",
                    "     ;;",
                    "esac",
                ]
            )
        )

        pg_checksums = path / "pg_checksums"
        pg_checksums.touch(mode=0o700)
        pg_checksums.write_text("#!/bin/sh\nexit 0")

        pg_controldata = path / "pg_controldata"
        pg_controldata.touch(mode=0o700)
        pg_controldata.write_text(
            "\n".join(
                [
                    "#!/bin/sh",
                    'echo "Data page checksum version:           1"',
                    "exit 0",
                ]
            )
        )

        psql = path / "psql"
        psql.touch(mode=0o700)
        psql.write_text(
            "\n".join(
                ["#!/bin/sh", 'echo "unexpected psql $* invocation" >&2', "exit 1"]
            )
        )

        pg_isready = path / "pg_isready"
        pg_isready.touch(mode=0o700)
        pg_isready.write_text("#!/bin/sh\nexit 1")

        return path

    pg13_bindir = pg_bindir(tmp_path / "pgsql-13" / "bin", 13)
    pg_bindir(tmp_path / "postgresql" / "15" / "bin", 15)
    base_bindir = str(tmp_path / "postgresql" / "{version}" / "bin")
    obj = {
        "prefix": str(tmp_path),
        "run_prefix": str(tmp_path / "run"),
        "postgresql": {
            "auth": {
                "local": "peer",
                "host": "password",
                "passfile": str(passfile),
            },
            "bindir": base_bindir,
            "default_version": "15",
            "versions": [
                {"version": "13", "bindir": str(pg13_bindir)},
            ],
        },
        "systemd": systemd_settings,
        "service_manager": None,
        "scheduler": None,
        "patroni": {
            "execpath": patroni_execpath,
            "etcd": {
                "hosts": ["etcd1:123", "etcd2:456"],
            },
            "restapi": {
                "verify_client": "optional",
            },
        },
        "pgbackrest": {
            "execpath": pgbackrest_execpath,
            "repository": {"path": tmp_path / "backups"},
        },
        "prometheus": {"execpath": prometheus_execpath},
        "logrotate": {},
        "rsyslog": {},
        "temboard": {
            "execpath": temboard_execpath,
            "ui_url": "https://0.0.0.0:8888",
            "signing_key": str(signing_key),
            "certificate": {
                "ca_cert": str(ssl_ca_cert_file),
                "cert": str(ssl_cert_file),
                "key": str(ssl_key_file),
            },
        },
        "powa": {},
        "cli": {
            "log_format": "%(levelname)-4s %(message)s",
        },
    }
    settings = Settings.parse_obj(obj)
    assert {v.version for v in settings.postgresql.versions} == {"13", "15"}
    return settings


@pytest.fixture
def ctx(settings: Settings) -> Context:
    return Context(settings=settings)


@pytest.fixture
def pm(settings: Settings) -> PluginManager:
    return plugin_manager(settings)


@pytest.fixture
def nohook(pm: PluginManager) -> Iterator[None]:
    unregistered = pm.unregister_all()
    yield
    for plugin in unregistered:
        pm.register(plugin)


@pytest.fixture
def composite_instance_model(pm: PluginManager) -> type[interface.Instance]:
    return interface.Instance.composite(pm)


@pytest.fixture
def composite_role_model(pm: PluginManager) -> type[interface.Role]:
    return interface.Role.composite(pm)


@pytest.fixture
def instance_manifest(
    composite_instance_model: type[interface.Instance], pg_version: str
) -> interface.Instance:
    return composite_instance_model(
        name="test",
        version=pg_version,
        surole_password=pydantic.SecretStr("p0st.g're$"),
        replrole_password=pydantic.SecretStr("repl1&c"),
        settings={"shared_preload_libraries": "passwordcheck"},
        pgbackrest={"stanza": "test-stanza"},
    )


def _instance(
    name: str, version: str, postgresql_conf: str, settings: Settings
) -> Instance:
    # Services are looked-up in reverse order of plugin registration.
    services: list[Any] = []

    assert settings.temboard is not None
    temboard_port = 2345
    temboard = temboard_models.Service(
        name=f"{version}-{name}",
        settings=settings.temboard,
        port=temboard_port,
        password=pydantic.SecretStr("dorade"),
    )
    services.append(temboard)

    assert settings.prometheus is not None
    prometheus_port = 9817
    prometheus = prometheus_models.Service(
        name=f"{version}-{name}",
        settings=settings.prometheus,
        port=prometheus_port,
        password=pydantic.SecretStr("truite"),
    )
    services.append(prometheus)

    assert settings.pgbackrest is not None
    pgbackrest = pgbackrest_models.Service(
        stanza=f"{name}-stanza",
        path=settings.pgbackrest.configpath / "conf.d" / f"{name}-stanza.conf",
    )
    services.append(pgbackrest)

    instance = Instance(
        name=name,
        version=version,
        settings=settings,
        services=services,
    )
    assert not instance.datadir.exists()
    instance.datadir.mkdir(parents=True)
    (instance.datadir / "PG_VERSION").write_text(instance.version)
    (instance.datadir / "postgresql.conf").write_text(postgresql_conf)
    (instance.datadir / "pg_hba.conf").write_text(
        "# pg_hba.conf\nlocal all postgres peer\n"
    )
    (instance.datadir / "pg_ident.conf").write_text("# pg_ident.conf\nmymap test dba\n")

    prometheus_config = prometheus_mod._configpath(
        instance.qualname, settings.prometheus
    )
    assert not prometheus_config.exists()
    prometheus_config.parent.mkdir(parents=True, exist_ok=True)
    prometheus_config.write_text(
        f"DATA_SOURCE_NAME=dbname=postgres port={instance.port} host={settings.postgresql.socket_directory} user=monitoring sslmode=disable password=truite\n"
        f"PG_EXPORTER_WEB_LISTEN_ADDRESS=:{prometheus.port}"
    )

    temboard_config = temboard_mod._configpath(instance.qualname, settings.temboard)
    assert not temboard_config.exists()
    temboard_config.parent.mkdir(parents=True, exist_ok=True)
    temboard_config.write_text(
        "\n".join(
            [
                "[temboard]",
                f"port = {temboard.port}",
                "ui_url = https://0.0.0.0:8888",
                "[postgresql]",
                f"port = {instance.port}",
                f"host = {settings.postgresql.socket_directory}",
                "user = temboardagent",
                "password = dorade",
            ]
        )
    )

    stanza_config = pgbackrest.path
    assert not stanza_config.exists()
    stanza_config.parent.mkdir(parents=True, exist_ok=True)
    stanza_config.write_text(
        "\n".join(
            [
                f"[{pgbackrest.stanza}]",
                f"pg1-path = {instance.datadir}",
                f"pg1-port = {instance.port}",
                "pg1-user = backup",
            ]
        )
    )

    assert settings.logrotate
    settings.logrotate.configdir.mkdir(parents=True, exist_ok=True)
    assert settings.rsyslog
    settings.rsyslog.configdir.mkdir(parents=True, exist_ok=True)
    return instance


@pytest.fixture
def postgresql_conf() -> str:
    return "\n".join(
        [
            "port = 999",
            "unix_socket_directories = /socks",
            "# backslash_quote = 'safe_encoding'",
        ]
    )


@pytest.fixture
def instance(pg_version: str, postgresql_conf: str, settings: Settings) -> Instance:
    return _instance("test", pg_version, postgresql_conf, settings)


@pytest.fixture
def instance2(pg_version: str, postgresql_conf: str, settings: Settings) -> Instance:
    return _instance("test2", pg_version, postgresql_conf, settings)


@pytest.fixture
def standby_instance(
    pg_version: str, postgresql_conf: str, settings: Settings
) -> Instance:
    instance = _instance("standby", pg_version, postgresql_conf, settings)
    assert int(pg_version) >= 12
    (instance.datadir / "standby.signal").write_text("")
    (instance.datadir / "postgresql.auto.conf").write_text(
        "primary_conninfo = 'host=/tmp port=4242 user=pg'\n"
        "primary_slot_name = aslot\n"
    )
    return instance


@pytest.fixture
def meminfo(tmp_path: Path) -> Path:
    fpath = tmp_path / "meminfo"
    fpath.write_text(
        "\n".join(
            [
                "MemTotal:        6022056 kB",
                "MemFree:         3226640 kB",
                "MemAvailable:    4235060 kB",
                "Buffers:          206512 kB",
            ]
        )
    )
    return fpath


@pytest.fixture(scope="package")
def site_config(
    site_config: Callable[..., Optional[str]]
) -> Iterator[Callable[..., Optional[str]]]:
    def test_site_config(*args: str) -> Optional[str]:
        """Lookup for configuration files in local data director first."""
        datadir = pathlib.Path(__file__).parent / "data"
        fpath = datadir.joinpath(*args)
        if fpath.exists():
            return fpath.read_text()
        return site_config(*args)

    with patch("pglift.util.site_config", new=test_site_config) as fn:
        yield fn


@pytest.fixture(scope="function", autouse=True)
def run_as_non_root() -> Iterator[MagicMock]:
    with patch("pglift.settings.is_root", autospec=True, return_value=False) as m:
        yield m
