import json
from pathlib import Path
from unittest.mock import patch

import psycopg.rows
import pytest
from psycopg import sql

from pglift import db
from pglift.ctx import Context
from pglift.models.system import Instance
from pglift.settings import Settings


def test_queries(datadir: Path, write_changes: bool) -> None:
    actual = dict(db.queries())
    fpath = datadir / "queries.json"
    if write_changes:
        fpath.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    expected = json.loads(fpath.read_text())
    assert actual == expected


def test_query() -> None:
    query = db.query(
        "role_alter",
        username=sql.Identifier("bob"),
        options=sql.Literal("PASSWORD 'ha'"),
    )
    assert list(query) == [
        sql.SQL("ALTER ROLE "),
        sql.Identifier("bob"),
        sql.SQL(" "),
        sql.Literal("PASSWORD 'ha'"),
        sql.SQL(";"),
    ]


@pytest.mark.parametrize(
    "connargs, expected",
    [
        (
            {"user": "bob"},
            "dbname=mydb sslmode=off user=bob port=999 host=/socks passfile={passfile}",
        ),
        (
            {"user": "alice", "password": "s3kret"},
            "dbname=mydb sslmode=off user=alice password=s3kret port=999 host=/socks passfile={passfile}",
        ),
    ],
)
def test_dsn(
    settings: Settings, instance: Instance, connargs: dict[str, str], expected: str
) -> None:
    passfile = settings.postgresql.auth.passfile
    conninfo = db.dsn(instance, dbname="mydb", sslmode="off", **connargs)
    assert conninfo == expected.format(passfile=passfile)


def test_dsn_badarg(instance: Instance) -> None:
    with pytest.raises(TypeError, match="unexpected 'port' argument"):
        db.dsn(instance, port=123)


def test_connect_str() -> None:
    with patch("psycopg.connect") as connect:
        with db.connect("port=1234"):
            pass
    connect.assert_called_once_with(
        "port=1234", autocommit=True, row_factory=psycopg.rows.dict_row
    )


def test_connect_instance(ctx: Context, instance: Instance, settings: Settings) -> None:
    with patch("psycopg.connect") as connect:
        cnx = db.connect(instance, ctx=ctx, user="dba")
        assert not connect.called
        with cnx:
            pass
    passfile = settings.postgresql.auth.passfile
    assert passfile is not None and passfile.exists()
    connect.assert_called_once_with(
        f"user=dba port=999 host=/socks passfile={passfile}",
        autocommit=True,
        row_factory=psycopg.rows.dict_row,
    )


def test_primary_connect(standby_instance: Instance, settings: Settings) -> None:
    standby = standby_instance.standby
    assert standby
    with patch("psycopg.connect") as connect:
        with db.primary_connect(standby):
            pass
    connect.assert_called_once_with(
        "user=pg host=/tmp port=4242 dbname=template1",
        autocommit=True,
        row_factory=psycopg.rows.dict_row,
    )


def test_connect_notimplementederror() -> None:
    with pytest.raises(NotImplementedError):
        db.connect({"host": "localhost"})
