import logging
from typing import TYPE_CHECKING, Any

import psycopg.pq
import psycopg.rows
from psycopg import sql

from . import databases, db, exceptions
from .models import interface
from .types import Role

if TYPE_CHECKING:
    from .ctx import Context
    from .models import system

logger = logging.getLogger(__name__)


def apply(
    ctx: "Context", instance: "system.PostgreSQLInstance", role: interface.Role
) -> interface.ApplyResult:
    """Apply state described by specified interface model as a PostgreSQL role.

    In case it's not possible to inspect changed role, possibly due to the super-user
    password being modified, change_state attribute within the returned object
    is set to interface.ApplyResult.changed with a warning logged.

    The instance should be running and not a standby.

    :raises ~pglift.exceptions.DependencyError: if the role cannot be dropped due some database dependency.
    """
    if instance.standby:
        raise exceptions.InstanceReadOnlyError(instance)

    with db.connect(instance, ctx=ctx) as cnx:
        return _apply(cnx, role, instance, ctx)


def _apply(
    cnx: db.Connection,
    role: interface.Role,
    instance: "system.PostgreSQLInstance",
    ctx: "Context",
) -> interface.ApplyResult:
    name = role.name
    if role.state == interface.PresenceState.absent:
        dropped = False
        if _exists(cnx, name):
            _drop(cnx, role, instance=instance, ctx=ctx)
            dropped = True
        return interface.ApplyResult(
            change_state=interface.ApplyChangeState.dropped if dropped else None
        )

    if not _exists(cnx, name):
        _create(cnx, role)
        ctx.hook.role_change(ctx=ctx, role=role, instance=instance)
        return interface.ApplyResult(change_state=interface.ApplyChangeState.created)
    else:
        actual = _get(cnx, name, instance=instance, ctx=ctx, password=False)
        _alter(cnx, role, instance=instance, ctx=ctx)
        if any(ctx.hook.role_change(ctx=ctx, role=role, instance=instance)):
            return interface.ApplyResult(
                change_state=interface.ApplyChangeState.changed
            )
        changed = _get(cnx, name, instance=instance, ctx=ctx, password=False) != actual
        return interface.ApplyResult(
            change_state=interface.ApplyChangeState.changed if changed else None
        )


def get(
    ctx: "Context",
    instance: "system.PostgreSQLInstance",
    name: str,
    *,
    password: bool = True,
) -> interface.Role:
    """Return the role object with specified name.

    :raises ~pglift.exceptions.RoleNotFound: if no role with specified 'name' exists.
    """
    with db.connect(instance, ctx=ctx) as cnx:
        return _get(cnx, name, instance=instance, ctx=ctx, password=password)


def _get(
    cnx: db.Connection,
    name: str,
    *,
    instance: "system.PostgreSQLInstance",
    ctx: "Context",
    password: bool = True,
) -> interface.Role:
    values = cnx.execute(db.query("role_inspect"), {"username": name}).fetchone()
    if values is None:
        raise exceptions.RoleNotFound(name)
    if not password:
        values["password"] = None
    for extra in ctx.hook.role_inspect(ctx=ctx, instance=instance, name=name):
        conflicts = set(values) & set(extra)
        assert (
            not conflicts
        ), f"conflicting keys returned by role_inspect() hook: {', '.join(conflicts)}"
        values.update(extra)
    return interface.Role(**values)


def ls(ctx: "Context", instance: "system.PostgreSQLInstance") -> list[interface.Role]:
    """Return the list of roles for an instance."""
    with db.connect(instance, ctx=ctx) as cnx, cnx.cursor(
        row_factory=psycopg.rows.class_row(interface.Role)
    ) as cur:
        return cur.execute(db.query("role_list")).fetchall()


def drop(
    ctx: "Context",
    instance: "system.PostgreSQLInstance",
    role: interface.RoleDropped,
) -> None:
    """Drop a role from instance.

    :raises ~pglift.exceptions.RoleNotFound: if no role with specified 'role.name' exists.
    :raises ~pglift.exceptions.RoleNotFound: if no role with specified 'role.reassign_owned' exists.
    :raises ~pglift.exceptions.DependencyError: if the role cannot be dropped due some database dependency.
    """
    if instance.standby:
        raise exceptions.InstanceReadOnlyError(instance)
    with db.connect(instance, ctx=ctx) as cnx:
        if not _exists(cnx, role.name):
            raise exceptions.RoleNotFound(role.name)
        _drop(cnx, role, instance=instance, ctx=ctx)


def _drop(
    cnx: db.Connection,
    role: interface.RoleDropped,
    *,
    instance: "system.PostgreSQLInstance",
    ctx: "Context",
) -> None:
    if role.reassign_owned and not _exists(cnx, role.reassign_owned):
        raise exceptions.RoleNotFound(role.reassign_owned)
    logger.info("dropping role '%s'", role.name)
    dbs_to_drop: list[str] = []
    if role.drop_owned or role.reassign_owned:
        for database in databases._list(cnx):
            if role.drop_owned and database.owner == role.name:
                dbs_to_drop.append(database.name)
            else:
                if role.drop_owned:
                    query = db.query(
                        "role_drop_owned", username=sql.Identifier(role.name)
                    )
                elif role.reassign_owned:
                    query = db.query(
                        "role_drop_reassign",
                        oldowner=sql.Identifier(role.name),
                        newowner=sql.Identifier(role.reassign_owned),
                    )
                with db.connect(instance, ctx=ctx, dbname=database.name) as db_cnx:
                    db_cnx.execute(query)

    for dbname in dbs_to_drop:
        cnx.execute(
            db.query(
                "database_drop",
                database=sql.Identifier(dbname),
                options=sql.SQL(""),
            )
        )
    try:
        cnx.execute(db.query("role_drop", username=sql.Identifier(role.name)))
    except psycopg.errors.DependentObjectsStillExist as e:
        assert (
            not role.drop_owned and not role.reassign_owned
        ), f"unexpected {e!r} while dropping {role}"
        raise exceptions.DependencyError(
            f"{e.diag.message_primary} (detail: {e.diag.message_detail})"
        ) from None

    ctx.hook.role_change(ctx=ctx, role=role, instance=instance)


def exists(ctx: "Context", instance: "system.PostgreSQLInstance", name: str) -> bool:
    """Return True if named role exists in 'instance'.

    The instance should be running.
    """
    with db.connect(instance, ctx=ctx) as cnx:
        return _exists(cnx, name)


def _exists(cnx: db.Connection, name: str) -> bool:
    cur = cnx.execute(db.query("role_exists"), {"username": name})
    return cur.rowcount == 1


def encrypt_password(cnx: psycopg.Connection[Any], role: Role) -> str:
    if role.encrypted_password is not None:
        return role.encrypted_password.get_secret_value()
    assert role.password is not None, "role has no password to encrypt"
    encoding = cnx.info.encoding
    return cnx.pgconn.encrypt_password(
        role.password.get_secret_value().encode(encoding), role.name.encode(encoding)
    ).decode(encoding)


def options(
    cnx: psycopg.Connection[Any],
    role: interface.Role,
    *,
    in_roles: bool = True,
) -> sql.Composable:
    """Return the "options" part of CREATE ROLE or ALTER ROLE SQL commands
    based on 'role' model.
    """
    opts: list[sql.Composable] = [
        sql.SQL("INHERIT" if role.inherit else "NOINHERIT"),
        sql.SQL("LOGIN" if role.login else "NOLOGIN"),
        sql.SQL("SUPERUSER" if role.superuser else "NOSUPERUSER"),
        sql.SQL("REPLICATION" if role.replication else "NOREPLICATION"),
        sql.SQL("CREATEDB" if role.createdb else "NOCREATEDB"),
        sql.SQL("CREATEROLE" if role.createrole else "NOCREATEROLE"),
    ]
    if role.password or role.encrypted_password:
        opts.append(sql.SQL("PASSWORD {}").format(encrypt_password(cnx, role)))
    if role.validity is not None:
        opts.append(sql.SQL("VALID UNTIL {}").format(role.validity.isoformat()))
    opts.append(
        sql.SQL(
            "CONNECTION LIMIT {}".format(
                role.connection_limit if role.connection_limit is not None else -1
            )
        )
    )
    if in_roles and role.in_roles:
        opts.append(
            sql.SQL(" ").join(
                [
                    sql.SQL("IN ROLE"),
                    sql.SQL(", ").join(
                        sql.Identifier(in_role) for in_role in role.in_roles
                    ),
                ]
            )
        )
    return sql.SQL(" ").join(opts)


def create(
    ctx: "Context", instance: "system.PostgreSQLInstance", role: interface.Role
) -> None:
    """Create 'role' in 'instance'.

    The instance should be a running primary and the role should not exist already.
    """
    if instance.standby:
        raise exceptions.InstanceReadOnlyError(instance)
    with db.connect(instance, ctx=ctx) as cnx:
        _create(cnx, role)


def _create(cnx: db.Connection, role: interface.Role) -> None:
    logger.info("creating role '%s'", role.name)
    opts = options(cnx, role)
    cnx.execute(
        db.query("role_create", username=sql.Identifier(role.name), options=opts)
    )


def alter(
    ctx: "Context", instance: "system.PostgreSQLInstance", role: interface.Role
) -> None:
    """Alter 'role' in 'instance'.

    The instance should be running primary and the role should exist already.
    """
    if instance.standby:
        raise exceptions.InstanceReadOnlyError(instance)
    with db.connect(instance, ctx=ctx) as cnx:
        _alter(cnx, role, instance=instance, ctx=ctx)


def _alter(
    cnx: db.Connection,
    role: interface.Role,
    *,
    instance: "system.PostgreSQLInstance",
    ctx: "Context",
) -> None:
    logger.info("altering role '%s'", role.name)
    actual_role = _get(cnx, role.name, instance=instance, ctx=ctx)
    in_roles = {
        "grant": set(role.in_roles) - set(actual_role.in_roles),
        "revoke": set(actual_role.in_roles) - set(role.in_roles),
    }
    with cnx.transaction():
        opts = options(cnx, role, in_roles=False)
        cnx.execute(
            db.query(
                "role_alter",
                username=sql.Identifier(role.name),
                options=opts,
            ),
        )
        for action, values in in_roles.items():
            if values:
                cnx.execute(
                    db.query(
                        f"role_{action}",
                        rolname=sql.SQL(", ").join(sql.Identifier(r) for r in values),
                        rolspec=sql.Identifier(role.name),
                    )
                )
