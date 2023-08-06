import logging
from typing import TYPE_CHECKING

from pgtoolkit.conf import Configuration

from pglift import util

from .. import hookimpl
from ..models import system

if TYPE_CHECKING:
    from ..pm import PluginManager
    from ..settings import RsyslogSettings, Settings


logger = logging.getLogger(__name__)


def register_if(settings: "Settings") -> bool:
    return settings.rsyslog is not None


def get_settings(settings: "Settings") -> "RsyslogSettings":
    assert settings.rsyslog is not None
    return settings.rsyslog


@hookimpl
def site_configure_install(settings: "Settings", pm: "PluginManager") -> None:
    logger.info("creating rsyslog config directory")
    s = get_settings(settings)
    s.configdir.mkdir(mode=0o750, exist_ok=True, parents=True)
    results = pm.hook.rsyslog_config(settings=settings)
    with (s.configdir / "rsyslog.conf").open("w") as f:
        logger.info("writing rsyslog config")
        f.write("\n".join(results))


@hookimpl
def site_configure_uninstall(settings: "Settings") -> None:
    logger.info("deleting rsyslog config directory")
    s = get_settings(settings)
    util.rmtree(s.configdir)


@hookimpl
def instance_settings(instance: "system.BaseInstance") -> Configuration:
    pgconfig = util.template("postgresql", "postgresql-rsyslog.conf").format(
        name=instance.name,
        version=instance.version,
    )
    config = Configuration()
    list(config.parse(pgconfig.splitlines()))
    return config
