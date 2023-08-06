import logging
import pathlib
import re
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from pgtoolkit.conf import parse as parse_pgconf
from pydantic.utils import deep_update

from pglift import exceptions, instances, postgresql
from pglift.ctx import Context
from pglift.models import interface, system
from pglift.postgresql import (
    ctl,
    install_systemd_unit_template,
    site_configure_install,
    site_configure_uninstall,
    uninstall_systemd_unit_template,
)
from pglift.settings import Settings, SystemdSettings
from pglift.types import ConfigChanges, Status


def test_site_configure(settings: Settings) -> None:
    assert not settings.postgresql.logpath.exists()
    site_configure_install(settings)
    assert settings.postgresql.logpath.exists()
    site_configure_uninstall(settings)
    assert not settings.postgresql.logpath.exists()


def test_initdb_dirty(
    pg_version: str, settings: Settings, ctx: Context, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = interface.Instance(name="dirty", version=pg_version)
    i = system.BaseInstance("dirty", pg_version, settings)
    i.datadir.mkdir(parents=True)
    (i.datadir / "dirty").touch()
    calls = []
    with pytest.raises(exceptions.CommandError):
        with monkeypatch.context() as m:
            m.setattr("pglift.systemd.enable", lambda *a: calls.append(a))
            postgresql.initdb(ctx, manifest, i)
    assert not i.waldir.exists()
    if ctx.settings.service_manager == "systemd":
        assert not calls


@pytest.mark.parametrize("data_checksums", [True, False])
def test_initdb_force_data_checksums(
    ctx: Context, pg_version: str, data_checksums: bool
) -> None:
    settings = ctx.settings
    assert settings.postgresql.initdb.data_checksums is None
    manifest = interface.Instance(
        name="checksums", version=pg_version, data_checksums=data_checksums
    )
    initdb_options = manifest.initdb_options(settings.postgresql.initdb)
    assert bool(initdb_options.data_checksums) == data_checksums
    instance = system.BaseInstance.get(manifest.name, manifest.version, ctx)

    def fake_init(*a: Any, **kw: Any) -> None:
        instance.datadir.mkdir(parents=True)
        (instance.datadir / "postgresql.conf").touch()

    with patch("pgtoolkit.ctl.PGCtl.init", side_effect=fake_init) as init:
        postgresql.initdb(ctx, manifest, instance)
    expected = {
        "waldir": str(instance.waldir),
        "username": "postgres",
        "encoding": "UTF8",
        "auth_local": "peer",
        "auth_host": "password",
        "locale": "C",
    }
    if data_checksums:
        init.assert_called_once_with(instance.datadir, data_checksums=True, **expected)
    else:
        init.assert_called_once_with(instance.datadir, **expected)


def test_postgresql_service_name(ctx: Context, instance: system.Instance) -> None:
    assert ctx.hook.postgresql_service_name(ctx=ctx, instance=instance) == "postgresql"


def test_postgresql_editable_conf(ctx: Context, instance: system.Instance) -> None:
    assert ctx.hook.postgresql_editable_conf(ctx=ctx, instance=instance) == "\n".join(
        [
            "port = 999",
            "unix_socket_directories = /socks",
            "# backslash_quote = 'safe_encoding'",
        ]
    )


@pytest.mark.usefixtures("nohook")
def test_configuration_precedence(
    pg_version: str,
    ctx: Context,
    instance: system.Instance,
    instance_manifest: interface.Instance,
) -> None:
    """Settings defined in manifest take precedence over postgresql.conf site template."""
    template = "\n".join(
        [
            "bonjour = 'hello, {name}'",
            "max_connections = 101",
            "port=9876",
            "unix_socket_directories = /tmp, /var/run/postgresql",
        ]
    )

    m = interface.Instance(
        name="foo", version=pg_version, settings={"max_connections": 100, "ssl": True}
    )
    configuration = instances.configuration(ctx, m, instance, template=template)
    assert configuration.as_dict() == {
        "bonjour": "hello, foo",
        "lc_messages": "C",
        "lc_monetary": "C",
        "lc_numeric": "C",
        "lc_time": "C",
        "max_connections": 100,
        "port": 9876,
        "ssl": True,
        "unix_socket_directories": "/tmp, /var/run/postgresql",
    }

    m = m._copy_validate({"port": 1234})
    configuration = instances.configuration(ctx, m, instance, template=template)
    assert configuration.as_dict() == {
        "bonjour": "hello, foo",
        "lc_messages": "C",
        "lc_monetary": "C",
        "lc_numeric": "C",
        "lc_time": "C",
        "max_connections": 100,
        "port": 1234,
        "ssl": True,
        "unix_socket_directories": "/tmp, /var/run/postgresql",
    }


@pytest.mark.usefixtures("nohook")
def test_configuration_configure_postgresql(
    ctx: Context, instance: system.Instance, instance_manifest: interface.Instance
) -> None:
    def configuration_changes(m: interface.Instance) -> ConfigChanges:
        configuration = instances.configuration(ctx, m, instance)
        return postgresql.configure_postgresql(
            configuration=configuration, instance=instance
        )

    configdir = instance.datadir
    postgresql_conf = configdir / "postgresql.conf"
    with postgresql_conf.open("w") as f:
        f.write("bonjour_name = 'overridden'\n")

    changes = configuration_changes(
        instance_manifest._copy_validate(
            {
                "settings": dict(
                    instance_manifest.settings,
                    max_connections=100,
                    shared_buffers="10 %",
                    effective_cache_size="5MB",
                ),
                "port": 5433,
            }
        )
    )
    old_shared_buffers, new_shared_buffers = changes.pop("shared_buffers")
    assert old_shared_buffers is None
    assert new_shared_buffers is not None and new_shared_buffers != "10 %"
    assert changes == {
        "bonjour_name": ("overridden", None),
        "cluster_name": (None, "test"),
        "effective_cache_size": (None, "5MB"),
        "lc_messages": (None, "C"),
        "lc_monetary": (None, "C"),
        "lc_numeric": (None, "C"),
        "lc_time": (None, "C"),
        "log_filename": (None, f"{instance.qualname}-%Y-%m-%d_%H%M%S.log"),
        "log_destination": (None, "stderr"),
        "logging_collector": (None, True),
        "max_connections": (None, 100),
        "port": (None, 5433),
        "shared_preload_libraries": (None, "passwordcheck"),
        "unix_socket_directories": (
            None,
            str(ctx.settings.postgresql.socket_directory),
        ),
        "log_directory": (
            None,
            str(ctx.settings.postgresql.logpath),
        ),
    }

    postgresql_conf = configdir / "postgresql.conf"
    content = postgresql_conf.read_text()
    lines = content.splitlines()
    assert "port = 5433" in lines
    assert "cluster_name = 'test'" in lines
    assert re.search(r"shared_buffers = '\d+ [kMGT]?B'", content)
    assert "effective_cache_size" in content
    assert (
        f"unix_socket_directories = '{ctx.settings.prefix}/run/postgresql'" in content
    )

    with postgresql_conf.open() as f:
        config = parse_pgconf(f)
    assert config.port == 5433
    assert config.entries["bonjour_name"].commented
    assert config.cluster_name == "test"

    changes = configuration_changes(
        instance_manifest._copy_validate(
            {
                "settings": dict(
                    instance_manifest.settings,
                    listen_address="*",
                    log_directory="pglogs",
                ),
                "port": 5432,
            }
        )
    )
    old_effective_cache_size, new_effective_cache_size = changes.pop(
        "effective_cache_size"
    )
    assert old_effective_cache_size == "5MB"
    assert new_effective_cache_size != old_effective_cache_size
    old_shared_buffers1, new_shared_buffers1 = changes.pop("shared_buffers")
    assert old_shared_buffers1 == new_shared_buffers
    assert new_shared_buffers1 != old_shared_buffers1
    assert changes == {
        "listen_address": (None, "*"),
        "max_connections": (100, None),
        "port": (5433, None),
        "log_directory": (str(ctx.settings.postgresql.logpath), "pglogs"),
    }

    # Same configuration, no change.
    mtime_before = postgresql_conf.stat().st_mtime
    changes = configuration_changes(
        instance_manifest._copy_validate(
            {
                "settings": dict(
                    instance_manifest.settings,
                    listen_address="*",
                    log_directory="pglogs",
                ),
            }
        )
    )
    assert changes == {}
    mtime_after = postgresql_conf.stat().st_mtime
    assert mtime_before == mtime_after


def test_configure_auth(
    ctx: Context, instance_manifest: interface.Instance, instance: system.Instance
) -> None:
    hba = instance.datadir / "pg_hba.conf"
    ident = instance.datadir / "pg_ident.conf"
    orig_hba = hba.read_text()
    orig_ident = ident.read_text()
    ctx.hook.configure_auth(
        settings=ctx.settings, instance=instance, manifest=instance_manifest
    )
    assert hba.read_text() != orig_hba
    assert ident.read_text() != orig_ident


def test_is_ready(instance: system.Instance) -> None:
    assert not ctl.is_ready(instance)


def test_check_status(instance: system.Instance) -> None:
    with pytest.raises(exceptions.InstanceStateError, match="instance is not_running"):
        postgresql.check_status(instance, Status.running)
    postgresql.check_status(instance, Status.not_running)


def test_start_foreground(ctx: Context, instance: system.Instance) -> None:
    with patch("os.execv") as execv:
        postgresql.start_postgresql(ctx, instance, foreground=True, wait=False)
    postgres = instance.bindir / "postgres"
    execv.assert_called_once_with(
        str(postgres), f"{postgres} -D {instance.datadir}".split()
    )


def test_libpq_environ(settings: Settings, instance: system.Instance) -> None:
    postgres_settings = settings.postgresql
    assert ctl.libpq_environ(instance, postgres_settings.surole.name, base={}) == {
        "PGPASSFILE": str(postgres_settings.auth.passfile)
    }
    assert ctl.libpq_environ(
        instance,
        postgres_settings.surole.name,
        base={"PGPASSFILE": "/var/lib/pgsql/pgpass"},
    ) == {"PGPASSFILE": "/var/lib/pgsql/pgpass"}


def test_libpq_environ_password_command(
    settings: Settings, pg_version: str, tmp_path: Path
) -> None:
    s = deep_update(
        settings.dict(),
        {
            "postgresql": {
                "surole": {"name": "bob"},
                "auth": {
                    "password_command": [
                        sys.executable,
                        "-c",
                        "import sys; print(f'{{sys.argv[1]}}-secret')",
                        "{instance}",
                        "--blah",
                    ],
                    "passfile": str(tmp_path / "pgpass"),
                },
            }
        },
    )
    settings = Settings.parse_obj(s)
    instance = system.BaseInstance("xyz", pg_version, settings=settings)
    assert ctl.libpq_environ(instance, "bob", base={}) == {
        "PGPASSFILE": str(tmp_path / "pgpass"),
        "PGPASSWORD": f"{pg_version}/xyz-secret",
    }


def test_install_systemd_unit_template(
    settings: Settings,
    systemd_settings: SystemdSettings,
) -> None:
    install_systemd_unit_template(
        settings,
        systemd_settings,
        env="SETTINGS=@settings.json",
        header="# Postgres managed by pglift",
    )
    unit = systemd_settings.unit_path / "pglift-postgresql@.service"
    assert unit.exists()
    lines = unit.read_text().splitlines()
    assert lines[0] == "# Postgres managed by pglift"
    assert "Environment=SETTINGS=@settings.json" in lines
    for line in lines:
        if line.startswith("ExecStart"):
            execstart = line.split("=", 1)[-1]
            assert execstart == f"{sys.executable} -m pglift postgres %i"
            break
    else:
        raise AssertionError("ExecStart line not found")
    uninstall_systemd_unit_template(systemd_settings)
    assert not unit.exists()


def test_logs(
    instance: system.Instance, tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
) -> None:
    with pytest.raises(
        exceptions.FileNotFoundError,
        match=r"file 'current_logfiles' for instance \d{2}/test not found",
    ):
        next(ctl.logs(instance))

    current_logfiles = instance.datadir / "current_logfiles"
    current_logfiles.write_text("csvlog log/postgresql.csv\n")
    with pytest.raises(ValueError, match="no record matching 'stderr'"):
        next(ctl.logs(instance, timeout=0.1))

    with (instance.datadir / "postgresql.conf").open("a") as f:
        f.write("\nlog_destination = stderr, csvlog, jsonlog\n")

    stderr_logpath = tmp_path / "postgresql-1.log"
    current_logfiles.write_text(
        f"stderr {stderr_logpath}\n"
        f"csvlog {tmp_path / 'postgresql-1.csv'}\n"
        f"jsonlog {tmp_path / 'postgresql-1.json'}\n"
    )
    with pytest.raises(exceptions.SystemError, match="failed to read"):
        next(ctl.logs(instance, timeout=0.1))

    logger = ctl.logs(instance, timeout=0.1)
    stderr_logpath.write_text("line1\nline2\n")
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="pglift.postgresql.ctl"):
        assert [next(logger) for _ in range(2)] == ["line1\n", "line2\n"]
    assert caplog.messages == [
        f"reading logs of instance '{instance}' from {stderr_logpath}"
    ]

    with pytest.raises(TimeoutError):
        next(logger)

    logger = ctl.logs(instance)
    assert [next(logger) for _ in range(2)] == ["line1\n", "line2\n"]

    stderr_logpath = tmp_path / "postgresql-2.log"
    current_logfiles.write_text(f"stderr {stderr_logpath}\n")
    stderr_logpath.write_text("line3\nline4\n")

    caplog.clear()
    with caplog.at_level(logging.INFO, logger="pglift.postgresql.ctl"):
        assert [next(logger) for _ in range(2)] == ["line3\n", "line4\n"]
    assert caplog.messages == [
        f"reading logs of instance '{instance}' from {stderr_logpath}"
    ]


def test_replication_lag(
    instance: system.Instance, standby_instance: system.Instance
) -> None:
    with pytest.raises(TypeError, match="not a standby"):
        postgresql.replication_lag(instance)
