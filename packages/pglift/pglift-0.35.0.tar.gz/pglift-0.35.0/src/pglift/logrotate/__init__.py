import logging
from pathlib import Path
from typing import TYPE_CHECKING

from pglift import util

from .. import hookimpl
from ..models.system import Instance, PostgreSQLInstance

if TYPE_CHECKING:
    from ..ctx import Context
    from ..pm import PluginManager
    from ..settings import LogRotateSettings, Settings

logger = logging.getLogger(__name__)


def register_if(settings: "Settings") -> bool:
    return settings.logrotate is not None


def get_settings(settings: "Settings") -> "LogRotateSettings":
    assert settings.logrotate is not None
    return settings.logrotate


@hookimpl
def site_configure_install(settings: "Settings", pm: "PluginManager") -> None:
    logger.info("creating logrotate config directory")
    s = get_settings(settings)
    s.configdir.mkdir(mode=0o750, exist_ok=True, parents=True)
    results = pm.hook.logrotate_config(settings=settings)
    with (s.configdir / "logrotate.conf").open("w") as f:
        logger.info("writing logrotate config")
        f.write("\n".join(results))


@hookimpl
def site_configure_uninstall(settings: "Settings") -> None:
    logger.info("deleting logrotate config directory")
    s = get_settings(settings)
    util.rmtree(s.configdir)


def instance_configpath(
    settings: "LogRotateSettings", instance: PostgreSQLInstance
) -> Path:
    return settings.configdir / f"{instance.qualname}.conf"


@hookimpl
def instance_drop(ctx: "Context", instance: Instance) -> None:
    settings = get_settings(ctx.settings)
    instance_configpath(settings, instance).unlink(missing_ok=True)
