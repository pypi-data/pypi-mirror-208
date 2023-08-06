import functools
import logging
import re
import sys
from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from typing import Any, Optional

import psycopg.conninfo
import psycopg.errors
import psycopg.rows
from psycopg import sql

from . import __name__ as pkgname
from ._compat import read_resource
from .ctx import Context
from .models.system import PostgreSQLInstance, Standby
from .postgresql.ctl import libpq_environ

Connection = psycopg.Connection[psycopg.rows.DictRow]
logger = logging.getLogger(__name__)


def query(name: str, **kwargs: sql.Composable) -> sql.Composed:
    for qname, qstr in queries():
        if qname == name:
            return sql.SQL(qstr).format(**kwargs)
    raise ValueError(name)


def queries() -> Iterator[tuple[str, str]]:
    content = read_resource(pkgname, "queries.sql")
    assert content is not None
    for block in re.split("-- name:", content):
        if not (block := block.strip()):
            continue
        qname, query = block.split("\n", 1)
        yield qname.strip(), query.strip()


def dsn(instance: "PostgreSQLInstance", **kwargs: Any) -> str:
    for badarg in ("port", "passfile", "host"):
        if badarg in kwargs:
            raise TypeError(f"unexpected '{badarg}' argument")

    kwargs["port"] = instance.port
    config = instance.config()
    if config.unix_socket_directories:
        kwargs["host"] = config.unix_socket_directories
    passfile = instance._settings.postgresql.auth.passfile
    if passfile is not None and passfile.exists():
        kwargs["passfile"] = str(passfile)

    assert "dsn" not in kwargs
    return psycopg.conninfo.make_conninfo(**kwargs)


def obfuscate_conninfo(conninfo: str, **kwargs: Any) -> str:
    """Return an obfuscated connection string with password hidden.

    >>> obfuscate_conninfo("user=postgres password=foo")
    'user=postgres password=********'
    >>> obfuscate_conninfo("user=postgres", password="secret")
    'user=postgres password=********'
    >>> obfuscate_conninfo("port=5444")
    'port=5444'
    """
    params = psycopg.conninfo.conninfo_to_dict(conninfo, **kwargs)
    if "password" in params:
        params["password"] = "*" * 8
    return psycopg.conninfo.make_conninfo(**params)


@functools.singledispatch
def connect(_: Any, **kwargs: Any) -> AbstractContextManager[Connection]:
    """Connect to a PostgreSQL instance.

    Either from a connection string directly as `connect(dsn)`; or from a
    PostgreSQLInstance value as `connect(instance, ctx)`,
    """
    raise NotImplementedError


@connect.register
def _(conninfo: str) -> AbstractContextManager[Connection]:
    logger.debug(
        "connecting to PostgreSQL instance with: %s",
        obfuscate_conninfo(conninfo),
    )
    return psycopg.connect(conninfo, autocommit=True, row_factory=psycopg.rows.dict_row)


@connect.register
@contextmanager
def _(
    instance: "PostgreSQLInstance",
    *,
    ctx: "Context",
    user: Optional[str] = None,
    password: Optional[str] = None,
    **kwargs: Any,
) -> Iterator[Connection]:
    postgresql_settings = ctx.settings.postgresql
    if user is None:
        user = postgresql_settings.surole.name
        if password is None:
            password = libpq_environ(instance, user).get("PGPASSWORD")

    build_conninfo = functools.partial(dsn, instance, user=user, **kwargs)

    conninfo = build_conninfo(password=password)
    try:
        with connect(conninfo) as cnx:
            yield cnx
    except psycopg.OperationalError as e:
        if not e.pgconn:
            raise
        if e.pgconn.needs_password:
            password = ctx.prompt(f"Password for user {user}", hide_input=True)
        elif e.pgconn.used_password:
            password = ctx.prompt(
                f"Password for user {user} is incorrect, re-enter a valid one",
                hide_input=True,
            )
        if not password:
            raise
        conninfo = build_conninfo(password=password)
        with connect(conninfo) as cnx:
            yield cnx


def primary_connect(standby: "Standby") -> AbstractContextManager[Connection]:
    """Connect to the primary of standby."""
    kwargs = {}
    if standby.password:
        kwargs["password"] = standby.password.get_secret_value()
    conninfo = psycopg.conninfo.make_conninfo(
        standby.primary_conninfo, dbname="template1", **kwargs
    )
    return connect(conninfo)


def default_notice_handler(diag: psycopg.errors.Diagnostic) -> None:
    if diag.message_primary is not None:
        sys.stderr.write(diag.message_primary + "\n")
