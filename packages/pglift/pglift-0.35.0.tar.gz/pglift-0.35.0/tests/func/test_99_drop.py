import pathlib
from typing import Optional

import pytest
import requests
from pgtoolkit.conf import Configuration

import pglift.pgbackrest.base as pgbackrest
import pglift.pgbackrest.models as pgbackrest_models
import pglift.prometheus.impl as prometheus
import pglift.prometheus.models as prometheus_models
from pglift import exceptions, systemd
from pglift.ctx import Context
from pglift.models import interface, system
from pglift.settings import PgBackRestSettings, Settings
from pglift.systemd import scheduler, service_manager

from .pgbackrest import PgbackrestRepoHost


@pytest.mark.standby
def test_standby_pgbackrest_teardown(
    instance: system.Instance,
    standby_instance: system.Instance,
    standby_instance_dropped: Configuration,
) -> None:
    pgbackrest_settings = pgbackrest.available(standby_instance._settings)
    if not pgbackrest_settings:
        pytest.skip("pgbackrest not available")
    assert not pgbackrest.enabled(standby_instance, pgbackrest_settings)
    assert (
        pgbackrest.system_lookup(standby_instance.datadir, pgbackrest_settings) is None
    )
    standby_svc = standby_instance.service(pgbackrest_models.Service)  # still in memory
    config = standby_svc.path.read_text()
    assert f"pg{standby_svc.index}-path" not in config
    assert str(standby_instance.datadir) not in config

    svc = instance.service(pgbackrest_models.Service)
    assert svc.path == standby_svc.path
    assert f"pg{svc.index}-path" in config
    assert str(instance.datadir) in config


def test_upgrade_pgbackrest_teardown(
    to_be_upgraded_instance: system.Instance,
    upgraded_instance: system.Instance,
    to_be_upgraded_instance_dropped: Configuration,
    upgraded_instance_dropped: Configuration,
) -> None:
    pgbackrest_settings = pgbackrest.available(to_be_upgraded_instance._settings)
    if not pgbackrest_settings:
        pytest.skip("pgbackrest not available")
    assert pgbackrest.available(upgraded_instance._settings) == pgbackrest_settings

    assert not pgbackrest.enabled(to_be_upgraded_instance, pgbackrest_settings)
    assert (
        pgbackrest.system_lookup(to_be_upgraded_instance.datadir, pgbackrest_settings)
        is None
    )
    svc = to_be_upgraded_instance.service(pgbackrest_models.Service)  # still in memory
    assert not svc.path.exists()

    assert not pgbackrest.enabled(upgraded_instance, pgbackrest_settings)
    assert (
        pgbackrest.system_lookup(upgraded_instance.datadir, pgbackrest_settings) is None
    )
    svc = upgraded_instance.service(pgbackrest_models.Service)  # still in memory
    assert not svc.path.exists()


@pytest.mark.standby
def test_pgbackrest_teardown(
    instance: system.Instance,
    standby_instance_dropped: Configuration,
    instance_dropped: Configuration,
    pgbackrest_repo_host: Optional[PgbackrestRepoHost],
) -> None:
    pgbackrest_settings = pgbackrest.available(instance._settings)
    if not pgbackrest_settings:
        pytest.skip("pgbackrest not available")
    stanza = f"mystanza-{instance.name}"
    path_repository: Optional[PgBackRestSettings.PathRepository] = None
    if pgbackrest_repo_host is None:
        assert isinstance(
            pgbackrest_settings.repository, PgBackRestSettings.PathRepository
        )
        path_repository = pgbackrest_settings.repository
    if path_repository:
        assert (
            next(
                (path_repository.path / "archive").glob(f"{stanza}*"),
                None,
            )
            is None
        )
        assert (
            next(
                (path_repository.path / "backup").glob(f"{stanza}*"),
                None,
            )
            is None
        )
    assert not (pgbackrest_settings.configpath / "conf.d" / f"{stanza}.conf").exists()
    # global directories and files are preserved
    assert (pgbackrest_settings.configpath / "pgbackrest.conf").exists()
    assert (pgbackrest_settings.configpath / "conf.d").exists()
    if path_repository:
        assert path_repository.path.exists()
    assert pgbackrest_settings.spoolpath.exists()
    assert pgbackrest_settings.lockpath.exists()
    assert pgbackrest_settings.logpath.exists()
    assert next(pgbackrest_settings.logpath.glob(f"{stanza}*.log"), None) is None


def test_pgpass(
    settings: Settings,
    passfile: pathlib.Path,
    instance_manifest: interface.Instance,
    to_be_upgraded_instance_dropped: Configuration,
    upgraded_instance_dropped: Configuration,
    instance_dropped: Configuration,
) -> None:
    assert not passfile.exists()


@pytest.mark.usefixtures("require_systemd_scheduler")
def test_systemd_backup_job(
    ctx: Context, instance: system.Instance, instance_dropped: Configuration
) -> None:
    unit = scheduler.unit("backup", instance.qualname)
    assert not systemd.is_active(ctx, unit)
    assert not systemd.is_enabled(ctx, unit)


def test_prometheus_teardown(
    ctx: Context,
    instance: system.Instance,
    instance_dropped: Configuration,
) -> None:
    prometheus_settings = prometheus.available(ctx.settings)
    if not prometheus_settings:
        pytest.skip("prometheus not available")
    configpath = pathlib.Path(
        str(prometheus_settings.configpath).format(name=instance.qualname)
    )
    queriespath = pathlib.Path(
        str(prometheus_settings.queriespath).format(name=instance.qualname)
    )
    assert not configpath.exists()
    assert not queriespath.exists()
    if ctx.settings.service_manager == "systemd":
        assert not systemd.is_enabled(
            ctx, service_manager.unit("postgres_exporter", instance.qualname)
        )
        service = instance.service(prometheus_models.Service)
        port = service.port
        with pytest.raises(requests.ConnectionError):
            requests.get(f"http://0.0.0.0:{port}/metrics")


def test_databases_teardown(
    instance: system.Instance,
    instance_dropped: Configuration,
) -> None:
    assert not instance.dumps_directory.exists()


def test_instance(
    ctx: Context, instance: system.Instance, instance_dropped: Configuration
) -> None:
    with pytest.raises(exceptions.InstanceNotFound, match=str(instance)):
        instance.exists()
