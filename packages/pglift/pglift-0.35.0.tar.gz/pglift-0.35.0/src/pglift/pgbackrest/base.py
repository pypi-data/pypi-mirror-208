import configparser
import datetime
import json
import logging
import os
import re
from collections.abc import Iterator
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from dateutil.tz import gettz
from pgtoolkit import conf as pgconf

from .. import cmd, exceptions, util
from ..models import interface
from ..postgresql.ctl import libpq_environ
from ..task import task
from .models import Service, ServiceManifest

if TYPE_CHECKING:
    from ..ctx import Context
    from ..models import system
    from ..settings import PgBackRestSettings, Settings

logger = logging.getLogger(__name__)


def available(settings: "Settings") -> Optional["PgBackRestSettings"]:
    return settings.pgbackrest


def get_settings(settings: "Settings") -> "PgBackRestSettings":
    """Return settings for pgbackrest

    Same as `available` but assert that settings are not None.
    Should be used in a context where settings for the plugin are surely
    set (for example in hookimpl).
    """
    assert settings.pgbackrest is not None
    return settings.pgbackrest


def enabled(
    instance: "system.PostgreSQLInstance", settings: "PgBackRestSettings"
) -> bool:
    return system_lookup(instance.datadir, settings) is not None


def base_configpath(settings: "PgBackRestSettings") -> Path:
    return settings.configpath / "pgbackrest.conf"


def config_directory(settings: "PgBackRestSettings") -> Path:
    return settings.configpath / "conf.d"


def create_include_directory(settings: "PgBackRestSettings") -> None:
    logger.info("creating pgbackrest include directory")
    config_directory(settings).mkdir(mode=0o750, exist_ok=True, parents=True)


def delete_include_directory(settings: "PgBackRestSettings") -> None:
    logger.info("deleting pgbackrest include directory")
    util.rmdir(config_directory(settings))


def make_cmd(stanza: str, settings: "PgBackRestSettings", *args: str) -> list[str]:
    return [
        str(settings.execpath),
        f"--config-path={settings.configpath}",
        "--log-level-stderr=info",
        f"--stanza={stanza}",
    ] + list(args)


parser = partial(configparser.ConfigParser, strict=True)

pgpath_rgx = re.compile(r"pg(\d+)-path")


def next_index(cp: configparser.ConfigParser, stanza: str) -> int:
    """Return the next index of pgN- options in parser.

    >>> cp = parser()
    >>> next_index(cp, "st")
    Traceback (most recent call last):
        ...
    configparser.NoSectionError: No section: 'st'
    >>> cp.add_section("st")
    >>> next_index(cp, "st")
    1
    >>> cp["st"]["pg1-path"] = "/pgsql/main"
    >>> next_index(cp, "st")
    2
    """
    idxs = {0}
    for opt in cp.options(stanza):
        if m := pgpath_rgx.match(opt):
            idxs.add(int(m.group(1)))
    return max(idxs) + 1


def system_lookup(datadir: Path, settings: "PgBackRestSettings") -> Optional[Service]:
    d = config_directory(settings)
    for p in d.glob("*.conf"):
        cp = parser()
        with p.open() as f:
            cp.read_file(f)
        for stanza in cp.sections():
            for key, value in cp.items(stanza):
                if (m := pgpath_rgx.match(key)) and value == str(datadir):
                    return Service(stanza=stanza, path=p, index=int(m.group(1)))
    return None


def stanza_pgpaths(path: Path, stanza: str) -> Iterator[tuple[int, Path]]:
    cp = parser()
    with path.open() as f:
        cp.read_file(f)
    for key, value in cp.items(stanza):
        if m := pgpath_rgx.match(key):
            yield int(m.group(1)), Path(value)


def service(
    instance: "system.BaseInstance",
    manifest: ServiceManifest,
    settings: "PgBackRestSettings",
    upgrading_from: Optional["system.Instance"],
) -> Service:
    """Retrieve a Service object.

    In case of an upgrade, if a service exists on original 'upgrading_from'
    instance, return it.

    Otherwise, lookup for a service bound to 'instance' and return it if
    found.

    Fall back to building a new service object from scratch.
    """
    if upgrading_from:
        if s := system_lookup(upgrading_from.datadir, settings):
            return s
    if s := system_lookup(instance.datadir, settings):
        if manifest.stanza != s.stanza:
            raise exceptions.InstanceStateError(
                f"instance {instance} is already bound to pgbackrest stanza '{s.stanza}' (path={s.path})"
            )
        return s
    stanza = manifest.stanza
    index = 1
    path = config_directory(settings) / f"{stanza}.conf"
    # Use the next pgN index when the path exists but configured instance is
    # not attached to its stanza. This would typically happen for standby
    # instances, when created on the same host as the primary.
    if path.exists():
        cp = parser()
        with path.open() as f:
            cp.read_file(f)
        index = next_index(cp, stanza)
    return Service(stanza=stanza, path=path, index=index)


def backup_info(
    service: Service,
    settings: "PgBackRestSettings",
    *,
    backup_set: Optional[str] = None,
) -> dict[str, Any]:
    """Call pgbackrest info command to obtain information about backups.

    Ref.: https://pgbackrest.org/command.html#command-info
    """
    args = []
    if backup_set is not None:
        args.append(f"--set={backup_set}")
    args.extend(["--output=json", "info"])
    r = cmd.run(make_cmd(service.stanza, settings, *args), check=True)
    infos = json.loads(r.stdout)
    try:
        return next(i for i in infos if i["name"] == service.stanza)
    except StopIteration:
        return {}


@task("setting up pgBackRest")
def setup(
    ctx: "Context",
    service: Service,
    settings: "PgBackRestSettings",
    instance_config: pgconf.Configuration,
    datadir: Path,
) -> None:
    """Setup pgBackRest"""
    base_config_path = base_configpath(settings)
    if not base_config_path.exists():
        raise exceptions.SystemError(
            f"Missing base config file {base_config_path} for pgbackrest. "
            "Did you forget to run 'pglift site-configure'?"
        )
    stanza = service.stanza
    stanza_confpath = service.path
    pg = f"pg{service.index}"
    cp = parser()
    if stanza_confpath.exists():
        with stanza_confpath.open() as f:
            cp.read_file(f)

    # Always use string values so that this would match with actual config (on
    # disk) that's parsed later on.
    config = {
        stanza: {
            f"{pg}-path": str(datadir),
            f"{pg}-port": str(instance_config.get("port", 5432)),
            f"{pg}-user": ctx.settings.postgresql.backuprole.name,
        },
    }
    if unix_socket_directories := instance_config.get("unix_socket_directories"):
        config[stanza][f"{pg}-socket-path"] = str(unix_socket_directories)
    cp.read_dict(config)
    with stanza_confpath.open("w") as configfile:
        cp.write(configfile)


def postgresql_configuration(
    stanza: str, settings: "PgBackRestSettings", datadir: Path
) -> pgconf.Configuration:
    pgconfig = util.template("postgresql", "pgbackrest.conf").format(
        execpath=settings.execpath,
        configpath=settings.configpath,
        stanza=stanza,
        datadir=datadir,
    )
    config = pgconf.Configuration()
    list(config.parse(pgconfig.splitlines()))
    return config


@setup.revert("deconfiguring pgBackRest")
def revert_setup(
    ctx: "Context",
    service: Service,
    settings: "PgBackRestSettings",
    instance_config: pgconf.Configuration,
    datadir: Path,
) -> None:
    """Un-setup pgBackRest.

    Remove options from 'stanza' section referencing instance's datadir, then
    possibly remove the configuration file if empty, and finally remove
    stanza's log files.
    """
    stanza = service.stanza
    stanza_confpath = service.path
    if stanza_confpath.exists():
        cp = parser()
        with stanza_confpath.open() as f:
            cp.read_file(f)
        for opt in cp.options(stanza):
            if opt.startswith(f"pg{service.index}-"):
                cp.remove_option(stanza, opt)
        with stanza_confpath.open("w") as f:
            cp.write(f)
        if not cp.options(stanza):
            stanza_confpath.unlink(missing_ok=True)
    if not stanza_confpath.exists():
        for logf in settings.logpath.glob(f"{stanza}-*.log"):
            logf.unlink(missing_ok=True)


def check(
    ctx: "Context",
    instance: "system.PostgreSQLInstance",
    service: Service,
    settings: "PgBackRestSettings",
    password: Optional[str],
) -> None:
    env = os.environ.copy()
    if password is not None:
        env["PGPASSWORD"] = password
    postgresql_settings = ctx.settings.postgresql
    env = libpq_environ(instance, postgresql_settings.backuprole.name, base=env)
    cmd.run(make_cmd(service.stanza, settings, "check"), check=True, env=env)


def iter_backups(
    instance: "system.Instance", settings: "PgBackRestSettings"
) -> Iterator[interface.InstanceBackup]:
    """Yield information about backups on an instance."""
    service = instance.service(Service)
    backups = backup_info(service, settings)["backup"]

    def started_at(entry: Any) -> float:
        return entry["timestamp"]["start"]  # type: ignore[no-any-return]

    for backup in sorted(backups, key=started_at, reverse=True):
        info_set = backup_info(service, settings, backup_set=backup["label"])
        databases = [db["name"] for db in info_set["backup"][0]["database-ref"]]
        dtstart = datetime.datetime.fromtimestamp(backup["timestamp"]["start"])
        dtstop = datetime.datetime.fromtimestamp(backup["timestamp"]["stop"])
        yield interface.InstanceBackup(
            label=backup["label"],
            size=backup["info"]["size"],
            repo_size=backup["info"]["repository"]["size"],
            date_start=dtstart.replace(tzinfo=gettz()),
            date_stop=dtstop.replace(tzinfo=gettz()),
            type=backup["type"],
            databases=databases,
        )


def restore_command(
    instance: "system.Instance",
    settings: "PgBackRestSettings",
    *,
    date: Optional[datetime.datetime] = None,
    backup_set: Optional[str] = None,
) -> list[str]:
    """Return the pgbackrest restore for ``instance``.

    Ref.: https://pgbackrest.org/command.html#command-restore
    """
    args = [
        # The delta option allows pgBackRest to handle instance data/wal
        # directories itself, without the need to clean them up beforehand.
        "--delta",
        "--link-all",
    ]
    if date is not None and backup_set is not None:
        raise exceptions.UnsupportedError(
            "date and backup_set are not expected to be both specified"
        )
    elif date is not None:
        target = date.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        args += ["--target-action=promote", "--type=time", f"--target={target}"]
    elif backup_set is not None:
        args += ["--target-action=promote", "--type=immediate", f"--set={backup_set}"]
    args.append("restore")
    s = instance.service(Service)
    return make_cmd(s.stanza, settings, *args)


def restore(
    ctx: "Context",
    instance: "system.Instance",
    settings: "PgBackRestSettings",
    *,
    label: Optional[str] = None,
    date: Optional[datetime.datetime] = None,
) -> None:
    """Restore an instance, possibly only including specified databases.

    The instance must not be running.

    Ref.: https://pgbackrest.org/command.html#command-restore
    """
    logger.info("restoring instance %s with pgBackRest", instance)
    if instance.standby:
        raise exceptions.InstanceReadOnlyError(instance)

    cmd_args = restore_command(instance, settings, date=date, backup_set=label)
    cmd.run(cmd_args, check=True)


def env_for(service: "Service", settings: "PgBackRestSettings") -> dict[str, str]:
    return {
        "PGBACKREST_CONFIG_PATH": str(settings.configpath),
        "PGBACKREST_STANZA": service.stanza,
    }
