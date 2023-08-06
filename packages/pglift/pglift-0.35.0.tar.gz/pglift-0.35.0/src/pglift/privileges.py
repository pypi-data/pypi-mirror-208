from collections.abc import Sequence
from typing import TYPE_CHECKING, Union

import psycopg.rows
from psycopg import sql

from . import db
from .ctx import Context
from .models import interface

if TYPE_CHECKING:
    from .models import system


def inspect_privileges(
    ctx: Context,
    instance: "system.Instance",
    database: str,
    roles: Sequence[str] = (),
    defaults: bool = False,
) -> Union[list[interface.DefaultPrivilege], list[interface.Privilege]]:
    args = {}
    where_clause = sql.SQL("")
    if roles:
        where_clause = sql.SQL("AND pg_roles.rolname = ANY(%(roles)s)")
        args["roles"] = list(roles)
    return_class: Union[type[interface.Privilege], type[interface.DefaultPrivilege]]

    if defaults:
        privilege_query = "database_default_acl"
        return_class = interface.DefaultPrivilege
    else:
        privilege_query = "database_privileges"
        return_class = interface.Privilege
    with db.connect(instance, ctx=ctx, dbname=database) as cnx:
        with cnx.cursor(row_factory=psycopg.rows.class_row(return_class)) as cur:
            cur.execute(db.query(privilege_query, where_clause=where_clause), args)
            return cur.fetchall()


def get(
    ctx: Context,
    instance: "system.Instance",
    *,
    databases: Sequence[str] = (),
    roles: Sequence[str] = (),
    defaults: bool = False,
) -> Union[list[interface.DefaultPrivilege], list[interface.Privilege]]:
    """List access privileges for databases of an instance.

    :param databases: list of databases to inspect (all will be inspected if
        unspecified).
    :param roles: list of roles to restrict inspection on.
    :param defaults: if ``True``, get default privileges.

    :raises ValueError: if an element of `databases` or `roles` does not
        exist.
    """

    with db.connect(instance, ctx=ctx) as cnx:
        cur = cnx.execute(db.query("database_list", where_clause=sql.SQL("")))
        existing_databases = [db["name"] for db in cur.fetchall()]
    if not databases:
        databases = existing_databases
    else:
        if unknown_dbs := set(databases) - set(existing_databases):
            raise ValueError(f"database(s) not found: {', '.join(unknown_dbs)}")

    if roles:
        with db.connect(instance, ctx=ctx) as cnx:
            cur = cnx.execute(db.query("role_list_names"))
            existing_roles = [n["rolname"] for n in cur.fetchall()]
        if unknown_roles := set(roles) - set(existing_roles):
            raise ValueError(f"role(s) not found: {', '.join(unknown_roles)}")

    return [
        prvlg
        for database in databases
        for prvlg in inspect_privileges(
            ctx, instance, database, roles=roles, defaults=defaults
        )
    ]
