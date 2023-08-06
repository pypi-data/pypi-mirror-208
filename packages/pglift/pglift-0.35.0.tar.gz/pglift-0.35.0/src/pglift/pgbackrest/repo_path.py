import configparser
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from pgtoolkit import conf as pgconf

from .. import cmd, exceptions, hookimpl, postgresql, util
from ..models import interface, system
from ..settings import PgBackRestSettings, Settings
from ..task import task
from ..types import BackupType, CompletedProcess
from . import base, models
from . import register_if as base_register_if
from . import role
from .base import get_settings

if TYPE_CHECKING:
    import click

    from ..ctx import Context

PathRepository = PgBackRestSettings.PathRepository
logger = logging.getLogger(__name__)


def register_if(settings: Settings) -> bool:
    if not base_register_if(settings):
        return False
    s = get_settings(settings)
    return isinstance(s.repository, PathRepository)


@hookimpl
def site_configure_install(settings: Settings) -> None:
    s = get_settings(settings)
    logger.info("installing base pgbackrest configuration")
    global_configpath = base.base_configpath(s)
    global_configpath.parent.mkdir(parents=True, exist_ok=True)
    config = base_config(s)
    with global_configpath.open("w") as f:
        config.write(f)
    base.create_include_directory(s)
    logger.info("creating pgbackrest repository path")
    repository_settings(s).path.mkdir(exist_ok=True, parents=True)


@hookimpl
def site_configure_uninstall(settings: Settings, ctx: "Context") -> None:
    s = get_settings(settings)
    base.delete_include_directory(s)
    logger.info("uninstalling base pgbackrest configuration")
    base.base_configpath(s).unlink(missing_ok=True)
    util.rmdir(s.configpath)
    rs = repository_settings(s)
    if ctx.confirm(f"Delete pgbackrest repository path {rs.path}?", False):
        logger.info("deleting pgbackrest repository path")
        util.rmtree(rs.path)


@hookimpl
def instance_configure(
    ctx: "Context",
    manifest: interface.Instance,
    config: pgconf.Configuration,
    creating: bool,
    upgrading_from: Optional[system.Instance],
) -> None:
    instance = system.PostgreSQLInstance.system_lookup(
        ctx, (manifest.name, manifest.version)
    )
    settings = get_settings(ctx.settings)
    service_manifest = manifest.service_manifest(models.ServiceManifest)
    service = base.service(instance, service_manifest, settings, upgrading_from)

    if creating and upgrading_from is None and base.enabled(instance, settings):
        if not ctx.confirm(
            f"Stanza '{service.stanza}' already bound to another instance, continue by overwriting it?",
            False,
        ):
            raise exceptions.Cancelled("pgbackrest repository already exists")
        revert_init(service, settings, instance.datadir)
        base.revert_setup(ctx, service, settings, config, instance.datadir)

    base.setup(ctx, service, settings, config, instance.datadir)

    if upgrading_from is not None:
        upgrade(service, settings)
    else:
        init(service, settings, instance.datadir)

    if creating and postgresql.is_running(instance):
        password = None
        backup_role = role(ctx.settings, manifest)
        assert backup_role is not None
        if backup_role.password is not None:
            password = backup_role.password.get_secret_value()
        base.check(ctx, instance, service, settings, password)


@hookimpl
def instance_drop(ctx: "Context", instance: system.Instance) -> None:
    try:
        service = instance.service(models.Service)
    except ValueError:
        return
    settings = get_settings(ctx.settings)
    if not (nb_backups := len(base.backup_info(service, settings)["backup"])) or (
        can_delete_stanza(service, settings, instance.datadir)
        and ctx.confirm(
            f"Confirm deletion of {nb_backups} backup(s) for stanza {service.stanza}?",
            True,
        )
    ):
        delete_stanza(service, settings, instance.datadir)
    base.revert_setup(ctx, service, settings, instance.config(), instance.datadir)


@hookimpl
def instance_cli(group: "click.Group") -> None:
    from .cli import instance_backup

    group.add_command(instance_backup)


def repository_settings(settings: PgBackRestSettings) -> PathRepository:
    assert isinstance(settings.repository, PathRepository)
    return settings.repository


def base_config(settings: "PgBackRestSettings") -> configparser.ConfigParser:
    cp = base.parser()
    cp.read_string(
        util.template("pgbackrest", "pgbackrest.conf").format(**dict(settings))
    )
    s = repository_settings(settings)
    cp["global"]["repo1-path"] = str(s.path)
    for opt, value in s.retention:
        cp["global"][f"repo1-retention-{opt}"] = str(value)
    return cp


@task("creating pgBackRest stanza {service.stanza}")
def init(
    service: models.Service,
    settings: "PgBackRestSettings",
    datadir: Path,
) -> None:
    cmd.run(
        base.make_cmd(service.stanza, settings, "stanza-create", "--no-online"),
        check=True,
    )


@init.revert("deleting pgBackRest stanza {service.stanza}")
def revert_init(
    service: models.Service,
    settings: "PgBackRestSettings",
    datadir: Path,
) -> None:
    if not can_delete_stanza(service, settings, datadir):
        logger.debug(
            "not deleting stanza %s, still used by another instance", service.stanza
        )
        return
    delete_stanza(service, settings, datadir)


def can_delete_stanza(
    service: models.Service, settings: "PgBackRestSettings", datadir: Path
) -> bool:
    for idx, path in base.stanza_pgpaths(service.path, service.stanza):
        if (idx, path) != (service.index, datadir):
            return False
    return True


def delete_stanza(
    service: models.Service, settings: "PgBackRestSettings", datadir: Path
) -> None:
    stanza = service.stanza
    cmd.run(base.make_cmd(stanza, settings, "stop"), check=True)
    cmd.run(
        base.make_cmd(
            stanza, settings, "stanza-delete", "--pg1-path", str(datadir), "--force"
        ),
        check=True,
    )


def upgrade(service: models.Service, settings: "PgBackRestSettings") -> None:
    """Upgrade stanza"""
    stanza = service.stanza
    logger.info("upgrading pgBackRest stanza %s", stanza)
    cmd.run(
        base.make_cmd(stanza, settings, "stanza-upgrade", "--no-online"), check=True
    )


def backup_command(
    instance: "system.Instance",
    settings: "PgBackRestSettings",
    *,
    type: BackupType = BackupType.default(),
    start_fast: bool = True,
    backup_standby: bool = False,
) -> list[str]:
    """Return the full pgbackrest command to perform a backup for ``instance``.

    :param type: backup type (one of 'full', 'incr', 'diff').

    Ref.: https://pgbackrest.org/command.html#command-backup
    """
    args = [f"--type={type.name}", "backup"]
    if start_fast:
        args.insert(-1, "--start-fast")
    if backup_standby:
        args.insert(-1, "--backup-standby")
    s = instance.service(models.Service)
    return base.make_cmd(s.stanza, settings, *args)


def backup(
    ctx: "Context",
    instance: "system.Instance",
    settings: "PgBackRestSettings",
    *,
    type: BackupType = BackupType.default(),
) -> CompletedProcess:
    """Perform a backup of ``instance``.

    :param type: backup type (one of 'full', 'incr', 'diff').

    Ref.: https://pgbackrest.org/command.html#command-backup
    """
    logger.info("backing up instance %s with pgBackRest", instance)
    cmd_args = backup_command(
        instance, settings, type=type, backup_standby=instance.standby is not None
    )
    postgresql_settings = ctx.settings.postgresql
    env = postgresql.ctl.libpq_environ(instance, postgresql_settings.backuprole.name)
    return cmd.run(cmd_args, check=True, env=env)
