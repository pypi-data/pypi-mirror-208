import logging
from typing import TYPE_CHECKING, Any, Literal, NoReturn, Optional

import pgtoolkit.conf
from pydantic import Field

from .. import exceptions, hookimpl, instances, postgresql, systemd, util
from ..models import interface, system
from . import impl, models
from .impl import available as available
from .impl import get_settings

if TYPE_CHECKING:
    import click

    from ..ctx import Context
    from ..settings import Settings, SystemdSettings
    from ..types import ConfigChanges

logger = logging.getLogger(__name__)


def register_if(settings: "Settings") -> bool:
    return available(settings) is not None


@hookimpl
def system_lookup(
    ctx: "Context", instance: system.BaseInstance
) -> Optional[models.Service]:
    settings = get_settings(ctx.settings)
    try:
        patroni = impl.config(instance.qualname, settings)
    except FileNotFoundError:
        return None
    return models.Service(
        cluster=patroni.scope,
        node=patroni.name,
        name=instance.qualname,
        settings=settings,
    )


@hookimpl
def interface_model() -> tuple[str, Any, Any]:
    return (
        models.ServiceManifest.__service__,
        Optional[models.ServiceManifest],
        Field(
            default=None,
            description="Configuration for the Patroni service, if enabled in site settings",
        ),
    )


@hookimpl
def standby_model(ctx: "Context", instance: system.Instance) -> Optional[NoReturn]:
    if system_lookup(ctx, instance) is None:
        return None
    raise ValueError("standby not supported with Patroni")


@hookimpl
def get(ctx: "Context", instance: system.Instance) -> Optional[models.ServiceManifest]:
    settings = get_settings(ctx.settings)
    if (s := system_lookup(ctx, instance)) is None:
        return None
    config = impl.config(instance.qualname, settings)
    cluster_members = impl.cluster_members(instance.qualname, settings)
    return models.ServiceManifest(
        cluster=s.cluster,
        node=s.node,
        postgresql_connect_host=config.postgresql.connect_address.host,
        restapi=config.restapi,
        cluster_members=cluster_members,
    )


SYSTEMD_SERVICE_NAME = "pglift-patroni@.service"


@hookimpl
def install_systemd_unit_template(
    settings: "Settings", systemd_settings: "SystemdSettings", header: str = ""
) -> None:
    logger.info("installing systemd template unit for Patroni")
    s = get_settings(settings)
    configpath = str(s.configpath).replace("{name}", "%i")
    content = systemd.template(SYSTEMD_SERVICE_NAME).format(
        executeas=systemd.executeas(settings),
        configpath=configpath,
        execpath=s.execpath,
    )
    systemd.install(
        SYSTEMD_SERVICE_NAME,
        util.with_header(content, header),
        systemd_settings.unit_path,
        logger=logger,
    )


@hookimpl
def uninstall_systemd_unit_template(
    settings: "Settings", systemd_settings: "SystemdSettings"
) -> None:
    logger.info("uninstalling systemd template unit for Patroni")
    systemd.uninstall(SYSTEMD_SERVICE_NAME, systemd_settings.unit_path, logger=logger)


@hookimpl
def initdb(
    ctx: "Context", manifest: interface.Instance, instance: system.BaseInstance
) -> Optional[Literal[True]]:
    """Initialize PostgreSQL database cluster through Patroni by configuring
    Patroni, then starting it (as the only way to get the actual instance
    created).
    """
    settings = get_settings(ctx.settings)
    try:
        service_manifest = manifest.service_manifest(models.ServiceManifest)
    except ValueError:
        return None
    configuration = instances.configuration(ctx, manifest, instance)
    with impl.setup(
        ctx,
        instance,
        manifest,
        service_manifest,
        settings,
        configuration,
        validate=True,
    ) as patroni:
        pass
    service = models.Service(
        cluster=patroni.scope,
        name=instance.qualname,
        node=patroni.name,
        settings=settings,
    )
    impl.init(ctx, instance, patroni, service)
    return True


@hookimpl
def configure_postgresql(
    ctx: "Context",
    manifest: interface.Instance,
    configuration: pgtoolkit.conf.Configuration,
    instance: system.BaseInstance,
) -> Optional["ConfigChanges"]:
    """Build and validate Patroni configuration, and return changes to PostgreSQL configuration."""
    settings = get_settings(ctx.settings)
    try:
        service = manifest.service_manifest(models.ServiceManifest)
    except ValueError:
        return None
    with impl.setup(
        ctx, instance, manifest, service, settings, configuration
    ) as patroni:
        changes = impl.postgresql_changes(instance.qualname, patroni, settings)
    if changes:
        impl.reload(ctx, instance, settings)
    return changes


@hookimpl
def configure_auth(manifest: "interface.Instance") -> Optional[Literal[False]]:
    # In 'patroni' is defined in 'manifest', this is a no-op, since pg_hba.conf
    # and pg_ident.conf are installed through Patroni configuration.
    try:
        manifest.service_manifest(models.ServiceManifest)
    except ValueError:
        return None
    return False


@hookimpl
def postgresql_editable_conf(
    ctx: "Context", instance: "system.PostgreSQLInstance"
) -> Optional[str]:
    settings = get_settings(ctx.settings)
    try:
        patroni = impl.config(instance.qualname, settings)
    except FileNotFoundError:
        return None
    conf = pgtoolkit.conf.Configuration()
    with conf.edit() as entries:
        for k, v in patroni.postgresql.parameters.items():
            entries.add(k, v)
    return "".join(conf.lines)


@hookimpl
def start_postgresql(
    ctx: "Context", instance: "system.PostgreSQLInstance", foreground: bool, wait: bool
) -> Optional[Literal[True]]:
    """Start PostgreSQL with Patroni."""
    if (service := system_lookup(ctx, instance)) is None:
        return None
    impl.start(ctx, service, foreground=foreground)
    if wait:
        postgresql.wait_ready(instance)
    return True


@hookimpl
def stop_postgresql(
    ctx: "Context", instance: "system.PostgreSQLInstance", deleting: bool
) -> Optional[Literal[True]]:
    """Stop PostgreSQL through Patroni.

    If 'deleting', do nothing as this will be handled upon by Patroni
    deconfiguration.
    """
    if not deleting:
        if (service := system_lookup(ctx, instance)) is None:
            return None
        impl.stop(ctx, service)
    return True


@hookimpl
def restart_postgresql(
    ctx: "Context", instance: "system.Instance"
) -> Optional[Literal[True]]:
    """Restart PostgreSQL with Patroni."""
    settings = get_settings(ctx.settings)
    if system_lookup(ctx, instance) is None:
        return None
    impl.restart(ctx, instance, settings)
    return True


@hookimpl
def reload_postgresql(
    ctx: "Context", instance: system.Instance
) -> Optional[Literal[True]]:
    settings = get_settings(ctx.settings)
    if system_lookup(ctx, instance) is None:
        return None
    impl.reload(ctx, instance, settings)
    return True


@hookimpl
def promote_postgresql(
    ctx: "Context", instance: system.PostgreSQLInstance
) -> Optional[NoReturn]:
    if system_lookup(ctx, instance) is None:
        return None
    raise exceptions.UnsupportedError(
        "unsupported operation: instance managed by Patroni"
    )


@hookimpl
def postgresql_service_name(
    ctx: "Context", instance: system.BaseInstance
) -> Optional[str]:
    if system_lookup(ctx, instance) is None:
        return None
    return "patroni"


@hookimpl
def instance_drop(ctx: "Context", instance: "system.Instance") -> None:
    """Uninstall Patroni from an instance being dropped."""
    if system_lookup(ctx, instance) is None:
        return
    service = instance.service(models.Service)
    impl.delete(ctx, service)


@hookimpl
def instance_env(ctx: "Context", instance: "system.Instance") -> dict[str, str]:
    settings = get_settings(ctx.settings)
    if (s := system_lookup(ctx, instance)) is None:
        return {}
    configpath = impl._configpath(instance.qualname, settings)
    assert configpath.exists()
    return {
        "PATRONI_NAME": s.node,
        "PATRONI_SCOPE": s.cluster,
        "PATRONICTL_CONFIG_FILE": str(configpath),
    }


@hookimpl
def cli() -> "click.Group":
    from .cli import cli as patroni

    return patroni


@hookimpl
def logrotate_config(settings: "Settings") -> str:
    s = get_settings(settings)
    return util.template("patroni", "logrotate.conf").format(logpath=s.logpath)
