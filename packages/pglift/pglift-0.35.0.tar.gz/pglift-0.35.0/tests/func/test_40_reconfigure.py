import urllib.parse
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import psutil
import pytest

from pglift import instances, postgresql, roles, systemd
from pglift.ctx import Context
from pglift.models import interface, system
from pglift.pgbackrest import base as pgbackrest
from pglift.prometheus import impl as prometheus
from pglift.settings import PostgreSQLSettings
from pglift.systemd import service_manager
from pglift.temboard import impl as temboard

from . import AuthType, config_dict, connect, passfile_entries, role_in_pgpass


def get_last_start(ctx: Context, unit: str, pidfile: Path) -> float:
    if ctx.settings.service_manager == "systemd":
        _, value = systemd.get_property(
            ctx, unit, "ActiveEnterTimestampMonotonic"
        ).split("=", 1)
        return float(value.strip())
    else:
        with pidfile.open() as f:
            return psutil.Process(int(f.readline().strip())).create_time()


@dataclass
class Recorder:
    service: Any

    def record(self) -> None:
        pass

    def assert_restarted(self) -> None:
        pytest.skip(f"{self.service.service_name} is not available")


@dataclass
class RestartRecorder(Recorder):
    instance: system.Instance
    records: list[float] = field(default_factory=list)

    def record(self) -> None:
        ctx = Context(settings=self.instance._settings)
        settings = self.service.get_settings(ctx.settings)
        record = get_last_start(
            ctx,
            service_manager.unit(self.service.service_name, self.instance.qualname),
            self.service._pidfile(self.instance.qualname, settings),
        )
        self.records.append(record)

    def assert_restarted(self) -> None:
        assert self.records[-2] != self.records[-1]


@pytest.fixture(scope="module")
def prometheus_restart_recorder(
    instance: system.Instance,
    prometheus_execpath: Optional[Path],
) -> Recorder:
    if prometheus_execpath:
        return RestartRecorder(prometheus, instance)
    return Recorder(prometheus)


@pytest.fixture(scope="module")
def temboard_restart_recorder(
    instance: system.Instance,
    temboard_execpath: Optional[Path],
) -> Recorder:
    if temboard_execpath:
        return RestartRecorder(temboard, instance)
    return Recorder(temboard)


@pytest.fixture(scope="module")
def newport(tmp_port_factory: Iterator[int]) -> int:
    return next(tmp_port_factory)


role1, role2, role3 = (
    interface.Role(name="r1", password="1", pgpass=True),
    interface.Role(name="r2", password="2", pgpass=True),
    interface.Role(name="r3", pgpass=False),
)


@pytest.fixture(scope="module")
def passfile_roles(
    instance: system.Instance,
    instance_manifest: interface.Instance,
    postgresql_auth: AuthType,
    postgresql_settings: PostgreSQLSettings,
) -> None:
    if postgresql_auth == AuthType.pgpass:
        ctx = Context(settings=instance._settings)
        surole = instance_manifest.surole(ctx.settings)
        assert ctx.settings.postgresql.surole.pgpass
        assert postgresql.is_running(instance)
        roles.apply(ctx, instance, role1)
        roles.apply(ctx, instance, role2)
        roles.apply(ctx, instance, role3)
        port = instance.port
        passfile = postgresql_settings.auth.passfile
        assert passfile is not None
        assert role_in_pgpass(passfile, role1, port=port)
        assert role_in_pgpass(passfile, role2, port=port)
        assert not role_in_pgpass(passfile, role3)
        assert role_in_pgpass(passfile, surole, port=port)


@pytest.fixture(scope="module")
def reconfigured(
    instance: system.Instance,
    instance_manifest: interface.Instance,
    prometheus_restart_recorder: Recorder,
    temboard_restart_recorder: Recorder,
    passfile_roles: None,
    newport: int,
) -> Iterator[system.Instance]:
    ctx = Context(settings=instance._settings)
    update = {
        "port": newport,
        "restart_on_changes": True,
        "settings": {"lc_numeric": ""},
    }
    prometheus_restart_recorder.record()
    temboard_restart_recorder.record()

    changes = instances.configure(ctx, instance_manifest._copy_validate(update))
    prometheus_restart_recorder.record()
    temboard_restart_recorder.record()

    yield instance

    restored_changes = instances.configure(ctx, instance_manifest)
    changes.clear()
    changes.update(restored_changes)


def test_pgpass(
    ctx: Context,
    passfile: Path,
    reconfigured: system.Instance,
    surole_password: str,
    pgbackrest_password: str,
    pgbackrest_available: bool,
    newport: int,
) -> None:
    backuprole = ctx.settings.postgresql.backuprole.name
    assert f"*:{newport}:*:postgres:{surole_password}" in passfile_entries(passfile)
    if pgbackrest_available:
        assert f"*:{newport}:*:{backuprole}:{pgbackrest_password}" in passfile_entries(
            passfile, role=backuprole
        )


def test_get_locale(reconfigured: system.Instance) -> None:
    with connect(reconfigured) as conn:
        assert instances.get_locale(conn) is None


def test_passfile(
    ctx: Context,
    reconfigured: system.Instance,
    instance_manifest: interface.Instance,
    passfile: Path,
    newport: int,
) -> None:
    surole = instance_manifest.surole(ctx.settings)
    oldport = instance_manifest.port
    assert not role_in_pgpass(passfile, role1, port=oldport)
    assert role_in_pgpass(passfile, role1, port=newport)
    assert not role_in_pgpass(passfile, role2, port=oldport)
    assert role_in_pgpass(passfile, role2, port=newport)
    assert not role_in_pgpass(passfile, role3)
    assert not role_in_pgpass(passfile, surole, port=oldport)
    assert role_in_pgpass(passfile, surole, port=newport)


def test_pgbackrest(
    ctx: Context,
    reconfigured: system.Instance,
    pgbackrest_available: bool,
    newport: int,
) -> None:
    if not pgbackrest_available:
        pytest.skip("pgbackrest is not available")
    stanza = f"mystanza-{reconfigured.name}"
    pgbackrest_settings = pgbackrest.get_settings(ctx.settings)
    stanza_configpath = pgbackrest_settings.configpath / "conf.d" / f"{stanza}.conf"
    config_after = stanza_configpath.read_text()
    assert f"pg1-port = {newport}" in config_after.splitlines()


def test_prometheus(
    ctx: Context,
    reconfigured: system.Instance,
    prometheus_password: str,
    prometheus_restart_recorder: Recorder,
    prometheus_execpath: Optional[Path],
    newport: int,
) -> None:
    prometheus_restart_recorder.assert_restarted()
    name = reconfigured.qualname
    prometheus_settings = prometheus.get_settings(ctx.settings)
    configpath = Path(str(prometheus_settings.configpath).format(name=name))
    new_prometheus_config = config_dict(configpath)
    dsn = new_prometheus_config["DATA_SOURCE_NAME"]
    assert f"{urllib.parse.quote(prometheus_password)}@:{newport}" in dsn


def test_temboard(
    ctx: Context,
    reconfigured: system.Instance,
    temboard_execpath: Optional[Path],
    temboard_restart_recorder: Recorder,
    newport: int,
) -> None:
    temboard_restart_recorder.assert_restarted()
    temboard_settings = temboard.get_settings(ctx.settings)
    configpath = Path(
        str(temboard_settings.configpath).format(name=reconfigured.qualname)
    )
    lines = configpath.read_text().splitlines()
    assert f"port = {newport}" in lines
