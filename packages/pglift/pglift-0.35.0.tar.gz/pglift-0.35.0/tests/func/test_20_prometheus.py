import logging
import urllib.parse
from collections.abc import Iterator
from pathlib import Path
from typing import Optional

import pytest
import requests

from pglift import exceptions, instances, postgresql, systemd
from pglift.ctx import Context
from pglift.models import interface, system
from pglift.prometheus import impl as prometheus
from pglift.prometheus import instance_status, models
from pglift.prometheus.models import Service
from pglift.settings import Settings
from pglift.systemd import service_manager
from pglift.types import Status

from . import config_dict, http_get
from .conftest import DatabaseFactory, RoleFactory

METRICS_URL = "http://0.0.0.0:{}/metrics"


@pytest.fixture(scope="session", autouse=True)
def _prometheus_available(prometheus_execpath: Optional[Path]) -> None:
    if not prometheus_execpath:
        pytest.skip("prometheus is not available")


def test_configure(
    ctx: Context,
    prometheus_password: str,
    instance: system.Instance,
    instance_manifest: interface.Instance,
    tmp_port_factory: Iterator[int],
) -> None:
    service = instance.service(models.Service)
    assert (
        service.password and service.password.get_secret_value() == prometheus_password
    )
    name = instance.qualname
    prometheus_settings = prometheus.get_settings(ctx.settings)
    configpath = Path(str(prometheus_settings.configpath).format(name=name))
    assert configpath.exists()

    prometheus_config = config_dict(configpath)
    dsn = prometheus_config["DATA_SOURCE_NAME"]
    assert "postgresql://prometheus" in dsn
    assert f"{urllib.parse.quote(prometheus_password)}@:{instance.port}" in dsn
    port = service.port
    assert prometheus_config["PG_EXPORTER_WEB_LISTEN_ADDRESS"] == f":{port}"

    queriespath = Path(str(prometheus_settings.queriespath).format(name=name))
    assert queriespath.exists()


@pytest.fixture
def postgres_exporter(
    ctx: Context,
    prometheus_password: str,
    instance_manifest: interface.Instance,
    instance: system.Instance,
    tmp_port_factory: Iterator[int],
    role_factory: RoleFactory,
) -> Iterator[Service]:
    """Setup a postgres_exporter service for 'instance' using another port."""
    port = next(tmp_port_factory)
    name = "123-fo-o"
    role = interface.Role(name="prometheus_tests", password=prometheus_password)
    unix_socket_directories = instance.config()["unix_socket_directories"]
    assert isinstance(unix_socket_directories, str), unix_socket_directories
    host = unix_socket_directories.split(",", 1)[0]
    dsn = f"host={host} dbname=postgres port={instance.port} user={role.name} sslmode=disable"
    prometheus_settings = prometheus.get_settings(ctx.settings)
    service = prometheus.setup(
        ctx, name, prometheus_settings, dsn=dsn, password=prometheus_password, port=port
    )
    configpath = Path(str(prometheus_settings.configpath).format(name=name))
    assert configpath.exists()
    queriespath = Path(str(prometheus_settings.queriespath).format(name=name))
    assert queriespath.exists()

    role_factory(
        role.name, f"LOGIN PASSWORD '{prometheus_password}' IN ROLE pg_monitor"
    )

    yield service

    prometheus.revert_setup(ctx, name, prometheus_settings)
    assert not configpath.exists()
    assert not queriespath.exists()


def test_setup(
    settings: Settings, instance: system.Instance, postgres_exporter: Service
) -> None:
    prometheus_settings = prometheus.get_settings(settings)
    configpath = Path(
        str(prometheus_settings.configpath).format(name=postgres_exporter.name)
    )
    prometheus_config = config_dict(configpath)
    assert f":{instance.port}" in prometheus_config["DATA_SOURCE_NAME"]
    assert (
        prometheus_config["PG_EXPORTER_WEB_LISTEN_ADDRESS"]
        == f":{postgres_exporter.port}"
    )


def test_start_stop(
    ctx: Context, instance: system.Instance, database_factory: DatabaseFactory
) -> None:
    service = instance.service(models.Service)
    port = service.port

    if ctx.settings.service_manager == "systemd":
        assert systemd.is_enabled(
            ctx, service_manager.unit("postgres_exporter", instance.qualname)
        )

    database_factory("newdb")

    if ctx.settings.service_manager == "systemd":
        assert systemd.is_active(
            ctx, service_manager.unit("postgres_exporter", instance.qualname)
        )
    r = http_get(METRICS_URL.format(port))
    r.raise_for_status()
    assert r.ok
    output = r.text
    assert "pg_up 1" in output.splitlines()

    assert instance_status(ctx, instance) == (Status.running, "prometheus")

    with instances.stopped(ctx, instance):
        if ctx.settings.service_manager == "systemd":
            assert not systemd.is_active(
                ctx, service_manager.unit("postgres_exporter", instance.qualname)
            )
        with pytest.raises(requests.ConnectionError):
            requests.get(METRICS_URL.format(port))

        assert instance_status(ctx, instance) == (Status.not_running, "prometheus")


def test_standby(
    ctx: Context, prometheus_password: str, standby_instance: system.Instance
) -> None:
    name = standby_instance.qualname
    service = standby_instance.service(models.Service)
    port = service.port
    assert (
        service.password and service.password.get_secret_value() == prometheus_password
    )
    standby_prometheus_settings = prometheus.get_settings(ctx.settings)
    configpath = Path(str(standby_prometheus_settings.configpath).format(name=name))
    assert configpath.exists()

    assert postgresql.is_running(standby_instance)

    if ctx.settings.service_manager == "systemd":
        assert systemd.is_active(ctx, service_manager.unit("postgres_exporter", name))
    r = http_get(METRICS_URL.format(port))
    r.raise_for_status()
    assert r.ok
    output = r.text
    assert "pg_up 1" in output.splitlines()


def test_upgrade(prometheus_password: str, upgraded_instance: system.Instance) -> None:
    service = upgraded_instance.service(models.Service)
    assert service.password
    name = upgraded_instance.qualname
    configpath = Path(str(service.settings.configpath).format(name=name))
    prometheus_config = config_dict(configpath)
    dsn = prometheus_config["DATA_SOURCE_NAME"]
    assert f"{urllib.parse.quote(prometheus_password)}@:{upgraded_instance.port}" in dsn


def test_start_stop_nonlocal(
    ctx: Context, instance: system.Instance, postgres_exporter: Service
) -> None:
    if ctx.settings.service_manager == "systemd":
        assert systemd.is_enabled(
            ctx, service_manager.unit("postgres_exporter", postgres_exporter.name)
        )

    assert postgresql.is_running(instance)
    prometheus.start(ctx, postgres_exporter)
    try:
        if ctx.settings.service_manager == "systemd":
            assert systemd.is_active(
                ctx,
                service_manager.unit("postgres_exporter", postgres_exporter.name),
            )
        r = http_get(METRICS_URL.format(postgres_exporter.port))
        r.raise_for_status()
        assert r.ok
        output = r.text
        assert "pg_up 1" in output.splitlines()
    finally:
        prometheus.stop(ctx, postgres_exporter)

    if ctx.settings.service_manager == "systemd":
        assert not systemd.is_active(
            ctx, service_manager.unit("postgres_exporter", postgres_exporter.name)
        )
    with pytest.raises(requests.ConnectionError):
        requests.get(METRICS_URL.format(postgres_exporter.port))


def test_apply(ctx: Context, tmp_port_factory: Iterator[int]) -> None:
    port = next(tmp_port_factory)
    m = models.PostgresExporter(name="test", dsn="dbname=test", port=port)
    prometheus_settings = prometheus.get_settings(ctx.settings)
    r = prometheus.apply(ctx, m, prometheus_settings)
    assert r.change_state == interface.ApplyChangeState.created

    configpath = Path(str(prometheus_settings.configpath).format(name="test"))
    assert configpath.exists()
    queriespath = Path(str(prometheus_settings.queriespath).format(name="test"))
    assert queriespath.exists()

    prometheus_config = config_dict(configpath)
    assert prometheus_config["PG_EXPORTER_WEB_LISTEN_ADDRESS"] == f":{port}"

    port1 = next(tmp_port_factory)
    r = prometheus.apply(ctx, m.copy(update={"port": port1}), prometheus_settings)
    assert r.change_state == interface.ApplyChangeState.changed
    prometheus_config = config_dict(configpath)
    assert prometheus_config["PG_EXPORTER_WEB_LISTEN_ADDRESS"] == f":{port1}"

    r = prometheus.apply(
        ctx,
        models.PostgresExporter(name="test", dsn="", port=port, state="absent"),
        prometheus_settings,
    )
    assert r.change_state == interface.ApplyChangeState.dropped
    assert not configpath.exists()
    assert not queriespath.exists()


def test_drop_exists(
    ctx: Context, tmp_port_factory: Iterator[int], caplog: pytest.LogCaptureFixture
) -> None:
    port = next(tmp_port_factory)
    prometheus_settings = prometheus.get_settings(ctx.settings)
    prometheus.setup(ctx, "dropme", prometheus_settings, port=port)
    assert prometheus.port("dropme", prometheus_settings) == port
    prometheus.drop(ctx, "dropme")
    with pytest.raises(exceptions.FileNotFoundError, match="postgres_exporter config"):
        prometheus.port("dropme", prometheus_settings)
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="pglift"):
        prometheus.drop(ctx, "dropme")
    assert caplog.records[0].message == "no postgres_exporter service 'dropme' found"
