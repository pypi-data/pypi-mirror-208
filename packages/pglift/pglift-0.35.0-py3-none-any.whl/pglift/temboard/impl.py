import configparser
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import pydantic
from pgtoolkit import conf as pgconf

from .. import exceptions
from .. import service as service_mod
from ..models import interface, system
from ..task import task
from .models import Service, ServiceManifest, service_name

if TYPE_CHECKING:
    from ..ctx import Context
    from ..settings import Settings, TemboardSettings


logger = logging.getLogger(__name__)


def available(settings: "Settings") -> Optional["TemboardSettings"]:
    return settings.temboard


def get_settings(settings: "Settings") -> "TemboardSettings":
    """Return settings for temboard

    Same as `available` but assert that settings are not None.
    Should be used in a context where settings for the plugin are surely
    set (for example in hookimpl).
    """
    assert settings.temboard is not None
    return settings.temboard


def enabled(qualname: str, settings: "TemboardSettings") -> bool:
    return _configpath(qualname, settings).exists()


def _args(execpath: Path, configpath: Path) -> list[str]:
    return [str(execpath), "--config", str(configpath)]


def _configpath(qualname: str, settings: "TemboardSettings") -> Path:
    return Path(str(settings.configpath).format(name=qualname))


def _homedir(qualname: str, settings: "TemboardSettings") -> Path:
    return Path(str(settings.home).format(name=qualname))


def _pidfile(qualname: str, settings: "TemboardSettings") -> Path:
    return Path(str(settings.pid_file).format(name=qualname))


def _logfile(qualname: str, settings: "TemboardSettings") -> Path:
    return settings.logpath / f"temboard_agent_{qualname}.log"


def config_var(configpath: Path, *, name: str, section: str) -> str:
    """Return temboardagent configuration value for given 'name' in 'section'."""
    if not configpath.exists():
        raise exceptions.FileNotFoundError(
            f"temboard agent configuration file {configpath} not found"
        )
    cp = configparser.ConfigParser()
    cp.read(configpath)
    for s, items in cp.items():
        if s != section:
            continue
        try:
            return items[name]
        except KeyError:
            pass
    raise exceptions.ConfigurationError(
        configpath, f"{name} not found in {section} section"
    )


def port(qualname: str, settings: "TemboardSettings") -> int:
    configpath = _configpath(qualname, settings)
    return int(config_var(configpath, name="port", section="temboard"))


def password(qualname: str, settings: "TemboardSettings") -> Optional[str]:
    configpath = _configpath(qualname, settings)
    try:
        return config_var(configpath, name="password", section="postgresql")
    except exceptions.ConfigurationError:
        return None


def system_lookup(
    ctx: "Context", name: str, settings: "TemboardSettings"
) -> Optional[Service]:
    try:
        p_ = port(name, settings)
        passwd_ = password(name, settings)
    except exceptions.FileNotFoundError as exc:
        logger.debug("failed to read temboard-agent port %s: %s", name, exc)
        return None
    else:
        password_ = None
        if passwd_ is not None:
            password_ = pydantic.SecretStr(passwd_)
        return Service(name=name, settings=settings, port=p_, password=password_)


@task("setting up temboardAgent")
def setup(
    ctx: "Context",
    manifest: "interface.Instance",
    settings: "TemboardSettings",
    instance_config: pgconf.Configuration,
) -> None:
    """Setup temboardAgent"""
    service_manifest = manifest.service_manifest(ServiceManifest)

    instance = system.PostgreSQLInstance.system_lookup(
        ctx, (manifest.name, manifest.version)
    )

    configpath = _configpath(instance.qualname, settings)

    password_: Optional[str] = None
    if not configpath.exists():
        if service_manifest.password:
            password_ = service_manifest.password.get_secret_value()
    else:
        # Get the password from config file
        password_ = password(instance.qualname, settings)

    cp = configparser.ConfigParser()
    cp["temboard"] = {
        "port": str(service_manifest.port),
        "plugins": json.dumps(settings.plugins),
        "ssl_ca_cert_file": str(settings.certificate.ca_cert),
        "ssl_cert_file": str(settings.certificate.cert),
        "ssl_key_file": str(settings.certificate.key),
        "home": str(_homedir(instance.qualname, settings)),
        "ui_url": settings.ui_url,
        "signing_public_key": str(settings.signing_key),
    }

    cp["postgresql"] = {
        "user": settings.role,
        "instance": instance.qualname,
    }
    if "port" in instance_config:
        cp["postgresql"]["port"] = str(instance_config["port"])
    if "unix_socket_directories" in instance_config:
        pghost = instance_config.unix_socket_directories.split(",")[0]  # type: ignore[union-attr]
        cp["postgresql"]["host"] = pghost
    if password_:
        cp["postgresql"]["password"] = password_
    cp["logging"] = {"method": settings.logmethod, "level": settings.loglevel}
    if settings.logmethod == settings.LogMethod.file:
        cp["logging"]["destination"] = str(_logfile(instance.qualname, settings))

    homedir = _homedir(instance.qualname, settings)
    homedir.mkdir(mode=0o700, exist_ok=True, parents=True)

    pidfile = _pidfile(instance.qualname, settings)
    pidfile.parent.mkdir(mode=0o700, exist_ok=True, parents=True)

    configpath.parent.mkdir(mode=0o700, exist_ok=True, parents=True)
    cp_actual = configparser.ConfigParser()
    if configpath.exists():
        cp_actual.read(configpath)
    needs_restart = False
    if cp != cp_actual:
        needs_restart = configpath.exists()
        with configpath.open("w") as configfile:
            cp.write(configfile)

    ctx.hook.enable_service(ctx=ctx, service=service_name, name=instance.qualname)
    if needs_restart:
        service = Service(
            name=instance.qualname,
            settings=settings,
            port=service_manifest.port,
            password=None,
        )
        restart(ctx, service)


@setup.revert("deconfiguring temboard agent")
def revert_setup(
    ctx: "Context",
    manifest: "interface.Instance",
    settings: "TemboardSettings",
    instance_config: pgconf.Configuration,
) -> None:
    """Un-setup temboard"""
    instance = system.BaseInstance.get(manifest.name, manifest.version, ctx)
    _configpath(instance.qualname, settings).unlink(missing_ok=True)
    _pidfile(instance.qualname, settings).unlink(missing_ok=True)
    _logfile(instance.qualname, settings).unlink(missing_ok=True)
    homedir = _homedir(instance.qualname, settings)
    if homedir.exists():
        ctx.rmtree(homedir)
    ctx.hook.disable_service(
        ctx=ctx, service=service_name, name=instance.qualname, now=True
    )


def start(ctx: "Context", service: Service, *, foreground: bool = False) -> None:
    logger.info("starting temboard-agent %s", service.name)
    service_mod.start(ctx, service, foreground=foreground)


def stop(ctx: "Context", service: Service) -> None:
    logger.info("stopping temboard-agent %s", service.name)
    service_mod.stop(ctx, service)


def restart(ctx: "Context", service: Service) -> None:
    logger.info("restarting temboard-agent %s", service.name)
    service_mod.restart(ctx, service)
