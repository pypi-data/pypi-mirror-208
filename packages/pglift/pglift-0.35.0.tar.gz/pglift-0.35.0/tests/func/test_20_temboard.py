from collections.abc import Iterator
from pathlib import Path
from typing import Optional

import pytest
import requests
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from pglift import instances, postgresql, systemd
from pglift.ctx import Context
from pglift.models import interface, system
from pglift.systemd import service_manager
from pglift.temboard import impl as temboard
from pglift.temboard import instance_status, models
from pglift.types import Status

from ..certificates import CA
from . import http_get

DISCOVER_URL = "https://0.0.0.0:{}/discover"


@pytest.fixture(scope="session", autouse=True)
def _temboard_available(temboard_execpath: Optional[Path]) -> None:
    if not temboard_execpath:
        pytest.skip("temboard not available")


@retry(wait=wait_fixed(1), stop=stop_after_attempt(5), reraise=True)
def check_discover(
    instance: system.Instance, service: models.Service, ca_cert: Path
) -> None:
    port = service.port
    r = http_get(DISCOVER_URL.format(port), verify=str(ca_cert))
    r.raise_for_status()
    assert r.json()["postgres"]["port"] == instance.port


def test_configure(
    ctx: Context,
    temboard_password: str,
    instance_manifest: interface.Instance,
    instance: system.Instance,
    tmp_port_factory: Iterator[int],
    ca: CA,
) -> None:
    temboard_settings = temboard.get_settings(ctx.settings)
    configpath = Path(str(temboard_settings.configpath).format(name=instance.qualname))
    assert configpath.exists()
    lines = configpath.read_text().splitlines()
    assert "user = temboardagent" in lines
    assert f"port = {instance.port}" in lines
    assert f"password = {temboard_password}" in lines

    home_dir = Path(str(temboard_settings.home).format(name=instance.qualname))
    assert home_dir.exists()
    assert (
        temboard_settings.logpath / f"temboard_agent_{instance.qualname}.log"
    ).exists()

    service = instance.service(models.Service)
    check_discover(instance, service, ca.crt)


def test_start_stop(ctx: Context, instance: system.Instance, ca: CA) -> None:
    service = instance.service(models.Service)
    port = service.port
    if ctx.settings.service_manager == "systemd":
        assert systemd.is_enabled(
            ctx, service_manager.unit("temboard_agent", instance.qualname)
        )
        assert systemd.is_active(
            ctx, service_manager.unit("temboard_agent", instance.qualname)
        )
    check_discover(instance, service, ca.crt)

    assert instance_status(ctx, instance) == (Status.running, "temBoard")

    with instances.stopped(ctx, instance):
        if ctx.settings.service_manager == "systemd":
            assert not systemd.is_active(
                ctx, service_manager.unit("temboard_agent", instance.qualname)
            )
        with pytest.raises(requests.ConnectionError):
            requests.get(DISCOVER_URL.format(port), verify=False)
        assert instance_status(ctx, instance) == (Status.not_running, "temBoard")


def test_standby(
    ctx: Context,
    temboard_password: str,
    standby_instance: system.Instance,
    ca: CA,
) -> None:
    temboard_settings = temboard.get_settings(ctx.settings)
    service = standby_instance.service(models.Service)
    assert service.password and service.password.get_secret_value() == temboard_password
    configpath = Path(
        str(temboard_settings.configpath).format(name=standby_instance.qualname)
    )
    assert configpath.exists()
    assert postgresql.is_running(standby_instance)

    if ctx.settings.service_manager == "systemd":
        assert systemd.is_active(
            ctx,
            service_manager.unit("temboard_agent", standby_instance.qualname),
        )
    check_discover(standby_instance, service, ca.crt)
