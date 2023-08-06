import datetime
import logging
import shlex
import subprocess
from collections.abc import Sequence
from typing import Any, Optional

import psycopg.rows
from pgtoolkit import conf as pgconf
from psycopg import sql

from . import cmd, db, exceptions, hookimpl, types
from .ctx import Context
from .models import interface, system
from .postgresql.ctl import libpq_environ
from .task import task

logger = logging.getLogger(__name__)


def apply(
    ctx: Context,
    instance: "system.PostgreSQLInstance",
    database: interface.Database,
) -> interface.ApplyResult:
    """Apply state described by specified interface model as a PostgreSQL database.

    The instance should be running and not a standby.
    """
    if instance.standby:
        raise exceptions.InstanceReadOnlyError(instance)

    with db.connect(instance, ctx=ctx) as cnx:
        return _apply(cnx, database, instance, ctx)


def _apply(
    cnx: db.Connection,
    database: interface.Database,
    instance: "system.PostgreSQLInstance",
    ctx: Context,
) -> interface.ApplyResult:
    name = database.name
    if database.state == interface.PresenceState.absent:
        dropped = False
        if _exists(cnx, name):
            _drop(cnx, database)
            dropped = True
        return interface.ApplyResult(
            change_state=interface.ApplyChangeState.dropped if dropped else None
        )

    if not _exists(cnx, name):
        _create(cnx, database, instance, ctx)

        if database.clone_from:
            clone(ctx, instance, name, str(database.clone_from))

        return interface.ApplyResult(change_state=interface.ApplyChangeState.created)

    logger.info("altering '%s' database on instance %s", database.name, instance)
    with db.connect(instance, ctx=ctx, dbname=name) as db_cnx:
        actual = _get(db_cnx)
        alter(cnx, database)
        if database.schemas or database.extensions:
            if database.schemas:
                create_or_drop_schemas(db_cnx, database.schemas)
            if database.extensions:
                create_or_drop_extensions(db_cnx, database.extensions)
        changed = _get(db_cnx) != actual
    return interface.ApplyResult(
        change_state=(interface.ApplyChangeState.changed if changed else None)
    )


@task("cloning '{name}' database in instance {instance} from {clone_from}")
def clone(
    ctx: Context, instance: "system.PostgreSQLInstance", name: str, clone_from: str
) -> None:
    def log_cmd(cmd_args: list[str]) -> None:
        base, conninfo = cmd_args[:-1], cmd_args[-1]
        logger.debug(shlex.join(base + [db.obfuscate_conninfo(conninfo)]))

    pg_dump = instance.bindir / "pg_dump"
    dump_cmd = [str(pg_dump), clone_from]
    user = instance._settings.postgresql.surole.name
    psql_cmd = [
        str(instance.bindir / "psql"),
        db.dsn(instance, dbname=name, user=user),
    ]
    env = libpq_environ(instance, user)
    with subprocess.Popen(  # nosec
        dump_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ) as dump:
        log_cmd(dump_cmd)
        psql = subprocess.Popen(  # nosec B603
            psql_cmd,
            stdin=dump.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        log_cmd(psql_cmd)
        pg_dump_stderr = []
        assert dump.stderr
        for errline in dump.stderr:
            logger.debug("%s: %s", pg_dump, errline.rstrip())
            pg_dump_stderr.append(errline)
        psql_stdout, psql_stderr = psql.communicate()

    if dump.returncode:
        raise exceptions.CommandError(
            dump.returncode, dump_cmd, stderr="".join(pg_dump_stderr)
        )
    if psql.returncode:
        raise exceptions.CommandError(
            psql.returncode, psql_cmd, psql_stdout, psql_stderr
        )


@clone.revert(None)
def revert_clone(
    ctx: Context, instance: "system.PostgreSQLInstance", name: str, clone_from: str
) -> None:
    drop(ctx, instance, interface.DatabaseDropped(name=name))


def get(
    ctx: Context, instance: "system.PostgreSQLInstance", name: str
) -> interface.Database:
    """Return the database object with specified name.

    :raises ~pglift.exceptions.DatabaseNotFound: if no database with specified
        'name' exists.
    """
    if not exists(ctx, instance, name):
        raise exceptions.DatabaseNotFound(name)
    with db.connect(instance, ctx=ctx, dbname=name) as cnx:
        return _get(cnx)


def _get(cnx: db.Connection) -> interface.Database:
    row = cnx.execute(db.query("database_inspect")).fetchone()
    assert row is not None
    settings = row.pop("settings")
    if settings is None:
        row["settings"] = None
    else:
        row["settings"] = {}
        for s in settings:
            k, v = s.split("=", 1)
            row["settings"][k.strip()] = pgconf.parse_value(v.strip())
    row["schemas"] = schemas(cnx)
    row["extensions"] = extensions(cnx)
    return interface.Database.parse_obj(row)


def ls(
    ctx: Context, instance: "system.PostgreSQLInstance", dbnames: Sequence[str] = ()
) -> list[interface.DetailedDatabase]:
    """List databases in instance.

    :param dbnames: restrict operation on databases with a name in this list.
    """
    with db.connect(instance, ctx=ctx) as cnx:
        return _list(cnx, dbnames)


def _list(
    cnx: db.Connection, dbnames: Sequence[str] = ()
) -> list[interface.DetailedDatabase]:
    where_clause: sql.Composable
    where_clause = sql.SQL("")
    if dbnames:
        where_clause = sql.SQL("AND d.datname IN ({})").format(
            sql.SQL(", ").join(map(sql.Literal, dbnames))
        )
    with cnx.cursor(
        row_factory=psycopg.rows.class_row(interface.DetailedDatabase)
    ) as cur:
        cur.execute(db.query("database_list", where_clause=where_clause))
        return cur.fetchall()


def drop(
    ctx: Context,
    instance: "system.PostgreSQLInstance",
    database: interface.DatabaseDropped,
) -> None:
    """Drop a database from a primary instance.

    :raises ~pglift.exceptions.DatabaseNotFound: if no database with specified
        'name' exists.
    """
    if instance.standby:
        raise exceptions.InstanceReadOnlyError(instance)
    with db.connect(instance, ctx=ctx) as cnx:
        if not _exists(cnx, database.name):
            raise exceptions.DatabaseNotFound(database.name)
        _drop(cnx, database)


def _drop(cnx: db.Connection, database: interface.DatabaseDropped) -> None:
    logger.info("dropping '%s' database", database.name)
    options = ""
    if database.force_drop:
        if cnx.info.server_version < 130000:
            raise exceptions.UnsupportedError(
                "Force drop option can't be used with PostgreSQL < 13"
            )
        options = "WITH (FORCE)"

    cnx.execute(
        db.query(
            "database_drop",
            database=sql.Identifier(database.name),
            options=sql.SQL(options),
        )
    )


def exists(ctx: Context, instance: "system.PostgreSQLInstance", name: str) -> bool:
    """Return True if named database exists in 'instance'.

    The instance should be running.
    """
    with db.connect(instance, ctx=ctx) as cnx:
        return _exists(cnx, name)


def _exists(cnx: db.Connection, name: str) -> bool:
    cur = cnx.execute(db.query("database_exists"), {"database": name})
    return cur.rowcount == 1


def options_and_args(
    database: interface.Database,
) -> tuple[sql.Composable, dict[str, Any]]:
    """Return the "options" part of CREATE DATABASE or ALTER DATABASE SQL
    commands based on 'database' model along with query arguments.
    """
    opts = []
    args: dict[str, Any] = {}
    if database.owner is not None:
        opts.append(sql.SQL("OWNER {}").format(sql.Identifier(database.owner)))
    return sql.SQL(" ").join(opts), args


def create(
    ctx: Context,
    instance: "system.PostgreSQLInstance",
    database: interface.Database,
) -> None:
    """Create 'database' in 'instance'.

    The instance should be a running primary and the database should not exist already.
    """
    if instance.standby:
        raise exceptions.InstanceReadOnlyError(instance)
    with db.connect(instance, ctx=ctx) as cnx:
        _create(cnx, database, instance, ctx)


def _create(
    cnx: db.Connection,
    database: interface.Database,
    instance: system.PostgreSQLInstance,
    ctx: Context,
) -> None:
    logger.info("creating '%s' database", database.name)
    options, args = options_and_args(database)
    cnx.execute(
        db.query(
            "database_create",
            database=sql.Identifier(database.name),
            options=options,
        ),
        args,
    )
    if database.settings is not None:
        alter(cnx, database)

    if database.schemas or database.extensions:
        with db.connect(instance, ctx=ctx, dbname=database.name) as cnx:
            if database.schemas:
                create_or_drop_schemas(cnx, database.schemas)
            if database.extensions:
                create_or_drop_extensions(cnx, database.extensions)


def alter(cnx: db.Connection, database: interface.Database) -> None:
    owner: sql.Composable
    if database.owner is None:
        owner = sql.SQL("CURRENT_USER")
    else:
        owner = sql.Identifier(database.owner)
    options = sql.SQL("OWNER TO {}").format(owner)
    cnx.execute(
        db.query(
            "database_alter",
            database=sql.Identifier(database.name),
            options=options,
        ),
    )

    if database.settings is not None:
        if not database.settings:
            # Empty input means reset all.
            cnx.execute(
                db.query(
                    "database_alter",
                    database=sql.Identifier(database.name),
                    options=sql.SQL("RESET ALL"),
                )
            )
        else:
            with cnx.transaction():
                for k, v in database.settings.items():
                    if v is None:
                        options = sql.SQL("RESET {}").format(sql.Identifier(k))
                    else:
                        options = sql.SQL("SET {} TO {}").format(
                            sql.Identifier(k), sql.Literal(v)
                        )
                    cnx.execute(
                        db.query(
                            "database_alter",
                            database=sql.Identifier(database.name),
                            options=options,
                        )
                    )


def encoding(cnx: db.Connection) -> str:
    """Return the encoding of connected database."""
    row = cnx.execute(db.query("database_encoding")).fetchone()
    assert row is not None
    value = row["encoding"]
    return str(value)


def run(
    ctx: Context,
    instance: "system.PostgreSQLInstance",
    sql_command: str,
    *,
    dbnames: Sequence[str] = (),
    exclude_dbnames: Sequence[str] = (),
    notice_handler: types.NoticeHandler = db.default_notice_handler,
) -> dict[str, list[dict[str, Any]]]:
    """Execute a SQL command on databases of `instance`.

    :param dbnames: restrict operation on databases with a name in this list.
    :param exclude_dbnames: exclude databases with a name in this list from
        the operation.
    :param notice_handler: a function to handle notice.

    :returns: a dict mapping database names to query results, if any.

    :raises psycopg.ProgrammingError: in case of unprocessable query.
    """
    result = {}
    for database in ls(ctx, instance):
        if (
            dbnames and database.name not in dbnames
        ) or database.name in exclude_dbnames:
            continue
        with db.connect(instance, ctx=ctx, dbname=database.name) as cnx:
            cnx.add_notice_handler(notice_handler)
            logger.info(
                'running "%s" on %s database of %s',
                sql_command,
                database.name,
                instance,
            )
            cur = cnx.execute(sql_command)
            if cur.statusmessage:
                logger.info(cur.statusmessage)
            if cur.description is not None:
                result[database.name] = cur.fetchall()
    return result


def dump(ctx: Context, instance: "system.PostgreSQLInstance", dbname: str) -> None:
    """dump a database of `instance` (logical backup)."""
    logger.info("backing up database '%s' on instance %s", dbname, instance)
    if not exists(ctx, instance, dbname):
        raise exceptions.DatabaseNotFound(dbname)
    postgresql_settings = ctx.settings.postgresql

    conninfo = db.dsn(instance, dbname=dbname, user=ctx.settings.postgresql.surole.name)

    date = (
        datetime.datetime.now(datetime.timezone.utc)
        .astimezone()
        .isoformat(timespec="seconds")
    )
    dumps_directory = instance.dumps_directory
    cmds = [
        [
            c.format(
                bindir=instance.bindir,
                path=dumps_directory,
                conninfo=conninfo,
                dbname=dbname,
                date=date,
            )
            for c in cmd_args
        ]
        for cmd_args in postgresql_settings.dump_commands
    ]
    env = libpq_environ(instance, postgresql_settings.surole.name)
    for cmd_args in cmds:
        cmd.run(cmd_args, check=True, env=env)

    manifest = dumps_directory / f"{dbname}_{date}.manifest"
    manifest.touch()
    manifest.write_text(
        "\n".join(
            [
                "# File created by pglift to keep track of database dumps",
                f"# database: {dbname}",
                f"# date: {date}",
            ]
        )
    )


def list_dumps(
    ctx: Context, instance: "system.PostgreSQLInstance", dbnames: Sequence[str] = ()
) -> list[interface.DatabaseDump]:
    dumps = (
        x.stem.rsplit("_", 1)
        for x in sorted(instance.dumps_directory.glob("*.manifest"))
        if x.is_file()
    )
    return [
        interface.DatabaseDump.build(dbname=dbname, date=date)
        for dbname, date in dumps
        if not dbnames or dbname in dbnames
    ]


def restore(
    ctx: Context,
    instance: "system.PostgreSQLInstance",
    dump_id: str,
    targetdbname: Optional[str] = None,
) -> None:
    """Restore a database dump in `instance`."""
    postgresql_settings = ctx.settings.postgresql

    conninfo = db.dsn(
        instance,
        dbname=targetdbname or "postgres",
        user=ctx.settings.postgresql.surole.name,
    )

    for dump in list_dumps(ctx, instance):
        if dump.id == dump_id:
            break
    else:
        raise exceptions.DatabaseDumpNotFound(name=f"{dump_id}")

    msg = "restoring dump for '%s' on instance %s"
    msg_variables = [dump.dbname, instance]
    if targetdbname:
        msg += " into '%s'"
        msg_variables.append(targetdbname)
    logger.info(msg, *msg_variables)

    def format_cmd(value: str) -> str:
        assert dump is not None
        return value.format(
            bindir=instance.bindir,
            path=instance.dumps_directory,
            conninfo=conninfo,
            dbname=dump.dbname,
            date=dump.date.isoformat(),
            createoption="-C" if targetdbname is None else "",
        )

    env = libpq_environ(instance, postgresql_settings.surole.name)
    for cmd_args in postgresql_settings.restore_commands:
        parts = [format_cmd(part) for part in cmd_args if format_cmd(part)]
        cmd.run(parts, check=True, env=env)


@hookimpl
def instance_configure(
    ctx: "Context", manifest: "interface.Instance", creating: bool
) -> None:
    if creating:
        instance = system.BaseInstance.get(manifest.name, manifest.version, ctx)
        instance.dumps_directory.mkdir(parents=True, exist_ok=True)


@hookimpl
def instance_drop(ctx: "Context", instance: "system.Instance") -> None:
    dumps_directory = instance.dumps_directory
    if not dumps_directory.exists():
        return
    has_dumps = next(dumps_directory.iterdir(), None) is not None
    if not has_dumps or ctx.confirm(
        f"Confirm deletion of database dump(s) for instance {instance}?",
        True,
    ):
        ctx.rmtree(dumps_directory)


def schemas(cnx: db.Connection) -> list[interface.Schema]:
    """Return list of schemas of database."""
    with cnx.cursor(row_factory=psycopg.rows.class_row(interface.Schema)) as cur:
        cur.execute(db.query("list_schemas"))
        return cur.fetchall()


def create_or_drop_schemas(
    cnx: db.Connection, schemas_: Sequence[interface.Schema]
) -> None:
    """Create or drop schemas in/from database."""
    existing = {s.name for s in schemas(cnx)}
    absent = interface.PresenceState.absent
    for schema in schemas_:
        if schema.state is absent and schema.name in existing:
            logger.info("dropping schema '%s'", schema.name)
            cnx.execute(
                db.query("drop_schema", schema=psycopg.sql.Identifier(schema.name))
            )
        elif schema.state is not absent and schema.name not in existing:
            logger.info("creating schema '%s'", schema.name)
            cnx.execute(
                db.query("create_schema", schema=psycopg.sql.Identifier(schema.name))
            )


def extensions(cnx: db.Connection) -> list[interface.Extension]:
    """Return list of extensions created in connected database using CREATE EXTENSION"""

    with cnx.cursor(row_factory=psycopg.rows.class_row(interface.Extension)) as cur:
        cur.execute(db.query("list_extensions"))
        return cur.fetchall()


def create_extension(cnx: db.Connection, extension: interface.Extension) -> None:
    msg, args = "creating extension '%(name)s'", {"name": extension.name}
    query = sql.SQL("CREATE EXTENSION IF NOT EXISTS {}").format(
        sql.Identifier(extension.name)
    )
    if extension.schema_:
        query += sql.SQL(" SCHEMA {}").format(sql.Identifier(extension.schema_))
        msg += " in schema '%(schema)s'"
        args["schema"] = extension.schema_
    if extension.version:
        query += sql.SQL(" VERSION {}").format(sql.Identifier(extension.version))
        msg += " with version %(version)s"
        args["version"] = extension.version
    query += sql.SQL(" CASCADE")
    logger.info(msg, args)
    cnx.execute(query)


def alter_extension_schema(cnx: db.Connection, name: str, schema: str) -> None:
    opts = sql.SQL("SET SCHEMA {}").format(sql.Identifier(schema))
    logger.info("setting '%s' extension schema to '%s'", name, schema)
    cnx.execute(
        db.query("alter_extension", extension=psycopg.sql.Identifier(name), opts=opts)
    )


def alter_extension_version(cnx: db.Connection, name: str, version: str) -> None:
    opts = sql.SQL("UPDATE TO {}").format(sql.Identifier(version))
    logger.info("updating '%s' extension version to '%s'", name, version)
    cnx.execute(
        db.query("alter_extension", extension=psycopg.sql.Identifier(name), opts=opts)
    )


def drop_extension(cnx: db.Connection, name: str) -> None:
    logger.info("dropping extension '%s'", name)
    cnx.execute(db.query("drop_extension", extension=psycopg.sql.Identifier(name)))


def create_or_drop_extensions(
    cnx: db.Connection, extensions_: Sequence[interface.Extension]
) -> None:
    """Create or drop extensions from database."""

    absent = interface.PresenceState.absent
    installed = {e.name: e for e in extensions(cnx)}

    r = cnx.execute("SELECT current_schema()").fetchone()
    assert r is not None
    current_schema = r["current_schema"]

    for extension in extensions_:
        try:
            installed_extension = installed[extension.name]
        except KeyError:
            if extension.state is not absent:
                create_extension(cnx, extension)
        else:
            if extension.state is absent:
                drop_extension(cnx, extension.name)
            else:
                new_schema = extension.schema_ or current_schema
                if new_schema != installed_extension.schema_:
                    alter_extension_schema(cnx, extension.name, new_schema)

                r = cnx.execute(
                    db.query("extension_default_version"),
                    {"extension_name": extension.name},
                ).fetchone()
                assert r
                default_version = str(r["default_version"])
                new_version = extension.version or default_version
                if new_version != installed_extension.version:
                    alter_extension_version(cnx, extension.name, new_version)
