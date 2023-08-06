import datetime
import fnmatch
import logging
from functools import partial

import psycopg
import pytest
from tenacity import Retrying
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from pglift import databases, exceptions, postgresql
from pglift.ctx import Context
from pglift.models import interface, system
from pglift.settings import PostgreSQLVersion

from . import connect, execute
from .conftest import DatabaseFactory, RoleFactory


@pytest.fixture(scope="module", autouse=True)
def _postgresql_running(instance: system.Instance) -> None:
    if not postgresql.is_running(instance):
        pytest.fail("instance is not running")


def test_exists(
    ctx: Context, instance: system.Instance, database_factory: DatabaseFactory
) -> None:
    assert not databases.exists(ctx, instance, "absent")
    database_factory("present")
    assert databases.exists(ctx, instance, "present")


def test_create(
    ctx: Context, instance: system.Instance, role_factory: RoleFactory
) -> None:
    database = interface.Database(name="db1")
    assert not databases.exists(ctx, instance, database.name)
    databases.create(ctx, instance, database)
    try:
        assert databases.get(ctx, instance, database.name) == database.copy(
            update={"owner": "postgres", "schemas": [{"name": "public"}]}
        )
    finally:
        # Drop database in order to avoid side effects in other tests.
        databases.drop(ctx, instance, interface.DatabaseDropped(name="db1"))

    role_factory("dba1")
    database = interface.Database(name="db2", owner="dba1")
    databases.create(ctx, instance, database)
    try:
        assert databases.get(ctx, instance, database.name) == database.copy(
            update={"schemas": [{"name": "public"}]}
        )
    finally:
        # Drop database in order to allow the role to be dropped in fixture.
        databases.drop(ctx, instance, interface.DatabaseDropped(name=database.name))


def test_apply(
    ctx: Context,
    instance: system.Instance,
    database_factory: DatabaseFactory,
    role_factory: RoleFactory,
) -> None:
    r = execute(
        instance,
        "SELECT default_version FROM pg_available_extensions WHERE name='hstore'",
    )
    assert r is not None
    default_version = r[0]["default_version"]
    database = interface.Database(
        name="db2",
        settings={"work_mem": "1MB"},
        extensions=[{"name": "hstore", "version": default_version}],
        schemas=[{"name": "myapp"}, {"name": "my_schema"}],
    )
    assert not databases.exists(ctx, instance, database.name)

    assert (
        databases.apply(ctx, instance, database).change_state
        == interface.ApplyChangeState.created
    )

    db = databases.get(ctx, instance, database.name)
    assert db.settings == {"work_mem": "1MB"}

    assert db.schemas == [
        interface.Schema(name="my_schema"),
        interface.Schema(name="myapp"),
        interface.Schema(name="public"),
    ]

    assert db.extensions == [
        interface.Extension(name="hstore", schema="public", version=default_version),
    ]

    assert databases.apply(ctx, instance, database).change_state is None  # no-op

    database = interface.Database(
        owner="postgres",
        name="db2",
        settings={"work_mem": "1MB"},
        schemas=[
            interface.Schema(name="my_schema"),
            interface.Schema(name="myapp"),
            interface.Schema(name="public"),
        ],
        extensions=[
            {"name": "hstore", "schema": "my_schema", "version": default_version},
        ],
    )
    assert (
        databases.apply(ctx, instance, database).change_state
        == interface.ApplyChangeState.changed
    )
    assert databases.get(ctx, instance, "db2") == database

    database = interface.Database(name="db2", state="absent")
    assert databases.exists(ctx, instance, database.name)
    assert (
        databases.apply(ctx, instance, database).change_state
        == interface.ApplyChangeState.dropped
    )
    assert not databases.exists(ctx, instance, database.name)


def test_apply_change_owner(
    ctx: Context,
    instance: system.Instance,
    database_factory: DatabaseFactory,
    role_factory: RoleFactory,
) -> None:
    database_factory("apply")
    database = interface.Database(name="apply")
    assert databases.apply(ctx, instance, database).change_state is None  # no-op
    assert databases.get(ctx, instance, "apply").owner == "postgres"

    role_factory("dbapply")
    database = interface.Database(
        name="apply", owner="dbapply", schemas=[interface.Schema(name="public")]
    )
    assert (
        databases.apply(ctx, instance, database).change_state
        == interface.ApplyChangeState.changed
    )
    try:
        assert databases.get(ctx, instance, "apply") == database
    finally:
        databases.drop(ctx, instance, interface.DatabaseDropped(name="apply"))


def test_apply_update_schemas(
    ctx: Context,
    instance: system.Instance,
    database_factory: DatabaseFactory,
) -> None:
    database_factory("db3")
    execute(instance, "CREATE SCHEMA my_schema", fetch=False, dbname="db3")

    assert databases.get(ctx, instance, "db3").schemas == [
        interface.Schema(name="my_schema"),
        interface.Schema(name="public"),
    ]

    database = interface.Database(
        name="db3",
        schemas=[
            interface.Schema(name="my_schema", state="absent"),
            interface.Schema(name="public"),
        ],
    )
    assert (
        databases.apply(ctx, instance, database).change_state
        == interface.ApplyChangeState.changed
    )

    assert databases.get(ctx, instance, "db3").schemas == [
        interface.Schema(name="public")
    ]


def test_apply_update_extensions(
    ctx: Context,
    instance: system.Instance,
    database_factory: DatabaseFactory,
) -> None:
    database_factory("db4")
    execute(instance, "CREATE SCHEMA my_schema", fetch=False, dbname="db4")
    execute(instance, "CREATE SCHEMA second_schema", fetch=False, dbname="db4")
    execute(
        instance,
        "CREATE EXTENSION unaccent WITH SCHEMA my_schema",
        fetch=False,
        dbname="db4",
    )
    execute(
        instance,
        "CREATE EXTENSION hstore WITH VERSION '1.4'",
        fetch=False,
        dbname="db4",
    )
    r = execute(
        instance,
        "SELECT name, default_version FROM pg_available_extensions",
    )
    assert r is not None
    unaccent_version = next(e for e in r if e["name"] == "unaccent")["default_version"]
    pgss_version = next(e for e in r if e["name"] == "pg_stat_statements")[
        "default_version"
    ]
    hstore_version = next(e for e in r if e["name"] == "hstore")["default_version"]

    assert databases.get(ctx, instance, "db4").extensions == [
        interface.Extension(name="hstore", schema="public", version="1.4"),
        interface.Extension(
            name="unaccent", schema="my_schema", version=unaccent_version
        ),
    ]

    database = interface.Database(
        name="db4",
        extensions=[
            {"name": "pg_stat_statements", "schema": "my_schema"},
            {"name": "unaccent"},
            {"name": "hstore"},
        ],
    )
    assert (
        databases.apply(ctx, instance, database).change_state
        == interface.ApplyChangeState.changed
    )
    assert databases.get(ctx, instance, "db4").extensions == [
        interface.Extension(name="hstore", schema="public", version=hstore_version),
        interface.Extension(
            name="pg_stat_statements", schema="my_schema", version=pgss_version
        ),
        interface.Extension(name="unaccent", schema="public", version=unaccent_version),
    ]

    database = interface.Database(
        name="db4",
        extensions=[
            {"name": "hstore", "state": "absent"},
            {"name": "pg_stat_statements", "state": "absent"},
            {"name": "unaccent", "state": "absent"},
        ],
    )
    assert (
        databases.apply(ctx, instance, database).change_state
        == interface.ApplyChangeState.changed
    )
    assert databases.get(ctx, instance, "db4").extensions == []


@pytest.fixture
def clonable_database(
    ctx: Context,
    role_factory: RoleFactory,
    database_factory: DatabaseFactory,
    instance: system.Instance,
) -> str:
    role_factory("cloner", "LOGIN")
    database_factory("db1", owner="cloner")
    databases.run(
        ctx, instance, "CREATE TABLE persons AS (SELECT 'bob' AS name)", dbnames=["db1"]
    )
    databases.run(ctx, instance, "ALTER TABLE persons OWNER TO cloner", dbnames=["db1"])
    return f"postgresql://cloner@127.0.0.1:{instance.port}/db1"


def test_clone_from(
    ctx: Context, clonable_database: str, instance: system.Instance
) -> None:
    database = interface.Database(name="cloned_db", clone_from=clonable_database)
    assert not databases.exists(ctx, instance, database.name)
    try:
        assert (
            databases.apply(ctx, instance, database).change_state
            == interface.ApplyChangeState.created
        )
        result = execute(instance, "SELECT * FROM persons", dbname="cloned_db")
        assert result == [{"name": "bob"}]
    finally:
        databases.drop(ctx, instance, interface.DatabaseDropped(name="cloned_db"))

    # DSN which target is a non existing database
    clone_uri = f"postgresql://postgres@127.0.0.1:{instance.port}/nosuchdb"
    with pytest.raises(exceptions.CommandError) as cm:
        databases.clone(ctx, instance, "cloned", clone_uri)
    assert cm.value.cmd[0] == str(instance.bindir / "pg_dump")
    assert not databases.exists(ctx, instance, "cloned")

    # DSN which target is a non existing user
    clone_uri = f"postgresql://nosuchuser@127.0.0.1:{instance.port}/postgres"
    with pytest.raises(exceptions.CommandError) as cm:
        databases.clone(ctx, instance, "cloned", clone_uri)
    assert cm.value.cmd[0] == str(instance.bindir / "pg_dump")
    assert not databases.exists(ctx, instance, "cloned")

    # Target database does not exist
    with pytest.raises(exceptions.CommandError) as cm:
        databases.clone(ctx, instance, "nosuchdb", clonable_database)
    assert cm.value.cmd[0] == str(instance.bindir / "psql")
    assert not databases.exists(ctx, instance, "nosuchdb")


def test_get(
    ctx: Context, instance: system.Instance, database_factory: DatabaseFactory
) -> None:
    with pytest.raises(exceptions.DatabaseNotFound, match="absent"):
        databases.get(ctx, instance, "absent")

    database_factory("describeme")
    execute(instance, "ALTER DATABASE describeme SET work_mem TO '3MB'", fetch=False)
    execute(instance, "CREATE SCHEMA my_schema", fetch=False, dbname="describeme")
    execute(
        instance,
        "CREATE EXTENSION unaccent WITH SCHEMA my_schema",
        fetch=False,
        dbname="describeme",
    )
    database = databases.get(ctx, instance, "describeme")
    assert database.name == "describeme"
    assert database.settings == {"work_mem": "3MB"}
    assert database.schemas == [
        interface.Schema(name="my_schema"),
        interface.Schema(name="public"),
    ]
    r = execute(
        instance,
        "SELECT default_version FROM pg_available_extensions WHERE name='unaccent'",
    )
    assert r is not None
    default_version = r[0]["default_version"]
    assert database.extensions == [
        interface.Extension(
            name="unaccent", schema="my_schema", version=default_version
        )
    ]


def test_encoding(instance: system.Instance) -> None:
    with connect(instance) as conn:
        assert databases.encoding(conn) == "UTF8"


def test_ls(
    ctx: Context, instance: system.Instance, database_factory: DatabaseFactory
) -> None:
    database_factory("db1")
    database_factory("db2")
    dbs = databases.ls(ctx, instance)
    dbnames = [d.name for d in dbs]
    assert "db2" in dbnames
    dbs = databases.ls(ctx, instance, dbnames=("db1",))
    dbnames = [d.name for d in dbs]
    assert "db2" not in dbnames
    assert len(dbs) == 1
    db1 = next(d for d in dbs).dict()
    db1.pop("size")
    db1["tablespace"].pop("size")
    assert db1 == {
        "acls": [],
        "collation": "C",
        "ctype": "C",
        "description": None,
        "encoding": "UTF8",
        "name": "db1",
        "owner": "postgres",
        "tablespace": {"location": "", "name": "pg_default"},
    }


def test_drop(
    ctx: Context, instance: system.Instance, database_factory: DatabaseFactory
) -> None:
    with pytest.raises(exceptions.DatabaseNotFound, match="absent"):
        databases.drop(ctx, instance, interface.DatabaseDropped(name="absent"))

    database_factory("dropme")
    databases.drop(ctx, instance, interface.DatabaseDropped(name="dropme"))
    assert not databases.exists(ctx, instance, "dropme")


def test_drop_force(
    ctx: Context,
    pg_version: str,
    instance: system.Instance,
    database_factory: DatabaseFactory,
) -> None:
    database_factory("dropme")

    if pg_version >= PostgreSQLVersion.v13:
        with connect(instance, dbname="dropme"):
            with pytest.raises(psycopg.errors.ObjectInUse):
                databases.drop(ctx, instance, interface.DatabaseDropped(name="dropme"))
            databases.drop(
                ctx, instance, interface.DatabaseDropped(name="dropme", force_drop=True)
            )
        assert not databases.exists(ctx, instance, "dropme")
    else:
        with pytest.raises(
            exceptions.UnsupportedError,
            match=r"^Force drop option can't be used with PostgreSQL < 13$",
        ):
            databases.drop(
                ctx, instance, interface.DatabaseDropped(name="dropme", force_drop=True)
            )


def test_run(
    ctx: Context,
    instance: system.Instance,
    database_factory: DatabaseFactory,
    caplog: pytest.LogCaptureFixture,
) -> None:
    database_factory("test")
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="pglift"):
        result_run = databases.run(
            ctx,
            instance,
            "CREATE TABLE persons AS (SELECT 'bob' AS name)",
            dbnames=["test"],
        )
    assert "CREATE TABLE persons AS (SELECT 'bob' AS name)" in caplog.records[0].message
    assert "SELECT 1" in caplog.records[1].message
    assert not result_run
    result = execute(instance, "SELECT * FROM persons", dbname="test")
    assert result == [{"name": "bob"}]
    result_run = databases.run(
        ctx,
        instance,
        "SELECT * from persons",
        dbnames=["test"],
    )
    assert result_run == {"test": [{"name": "bob"}]}


def test_run_analyze(
    ctx: Context, instance: system.Instance, database_factory: DatabaseFactory
) -> None:
    database_factory("test")

    def last_analyze() -> datetime.datetime:
        result = execute(
            instance,
            "SELECT MIN(last_analyze) m FROM pg_stat_all_tables WHERE last_analyze IS NOT NULL",
            dbname="test",
        )[0]["m"]
        assert isinstance(result, datetime.datetime), result
        return result

    retrying = partial(
        Retrying,
        retry=retry_if_exception_type(AssertionError),
        stop=stop_after_attempt(5),
        wait=wait_fixed(0.2),
        reraise=True,
    )

    databases.run(ctx, instance, "ANALYZE")
    previous = last_analyze()
    databases.run(ctx, instance, "ANALYZE")
    for attempt in retrying():
        now = last_analyze()
        with attempt:
            assert now > previous
    databases.run(ctx, instance, "ANALYZE", exclude_dbnames=["test"])
    for attempt in retrying():
        with attempt:
            assert last_analyze() == now


def test_run_output_notices(
    ctx: Context, instance: system.Instance, capsys: pytest.CaptureFixture[str]
) -> None:
    databases.run(
        ctx, instance, "DO $$ BEGIN RAISE NOTICE 'foo'; END $$", dbnames=["postgres"]
    )
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "foo\n"


def test_dump(
    ctx: Context, instance: system.Instance, database_factory: DatabaseFactory
) -> None:
    with pytest.raises(exceptions.DatabaseNotFound, match="absent"):
        databases.dump(ctx, instance, "absent")
    database_factory("dbtodump")
    databases.dump(ctx, instance, "dbtodump")
    directory = instance.dumps_directory
    assert directory.exists()
    (dumpfile, manifest) = sorted(directory.iterdir())
    assert fnmatch.fnmatch(str(dumpfile), "*dbtodump_*.dump"), dumpfile
    assert fnmatch.fnmatch(str(manifest), "*dbtodump_*.manifest"), manifest


def test_list_dumps(
    ctx: Context, instance: system.Instance, database_factory: DatabaseFactory
) -> None:
    database_factory("dbtodump")
    databases.dump(ctx, instance, "dbtodump")
    dumps = databases.list_dumps(ctx, instance)
    dbnames = [d.dbname for d in dumps]
    assert "dbtodump" in dbnames

    dumps = databases.list_dumps(ctx, instance, dbnames=("dbtodump",))
    dbnames = [d.dbname for d in dumps]
    assert "dbtodump" in dbnames

    dumps = databases.list_dumps(ctx, instance, dbnames=("otherdb",))
    assert dumps == []


def test_restore(
    ctx: Context, instance: system.Instance, database_factory: DatabaseFactory
) -> None:
    database_factory("dbtodump2")
    databases.run(
        ctx,
        instance,
        "CREATE TABLE persons AS (SELECT 'bob' AS name)",
        dbnames=["dbtodump2"],
    )
    databases.dump(ctx, instance, "dbtodump2")

    with pytest.raises(
        exceptions.DatabaseDumpNotFound, match=r"dump .*notexisting dump.* not found"
    ):
        databases.restore(ctx, instance, "notexisting dump")

    # Get id from an existing dump
    dumps = databases.list_dumps(ctx, instance, dbnames=("dbtodump2",))
    dump_id = dumps[0].id

    # Fails because database already exists
    with pytest.raises(exceptions.CommandError):
        databases.restore(ctx, instance, dump_id)

    databases.run(ctx, instance, "DROP DATABASE dbtodump2", dbnames=["postgres"])
    databases.restore(ctx, instance, dump_id)
    result = execute(instance, "SELECT * FROM persons", dbname="dbtodump2")
    assert result == [{"name": "bob"}]

    # Restore dump on a new database
    # Fails because new database doesn't exist
    with pytest.raises(exceptions.CommandError):
        databases.restore(ctx, instance, dump_id, targetdbname="newdb")

    database_factory("newdb")
    databases.restore(ctx, instance, dump_id, targetdbname="newdb")
    result = execute(instance, "SELECT * FROM persons", dbname="newdb")
    assert result == [{"name": "bob"}]
