from collections.abc import Sequence
from typing import IO, Any

import click
from pydantic.utils import deep_update

from .. import plugin_manager, postgresql, privileges, roles
from ..ctx import Context
from ..models import helpers, interface, system
from ..settings import Settings
from .util import (
    Callback,
    CompositeCommandGroup,
    OutputFormat,
    dry_run_option,
    instance_identifier_option,
    output_format_option,
    pass_ctx,
    pass_instance,
    print_argspec,
    print_json_for,
    print_schema,
    print_table_for,
)


def print_role_schema(
    context: click.Context, param: click.Parameter, value: bool
) -> None:
    p = plugin_manager(context.obj.ctx.settings)
    model = interface.Role.composite(p)
    return print_schema(context, param, value, model=model)


def print_role_argspec(
    context: click.Context, param: click.Parameter, value: bool
) -> None:
    settings: Settings = context.obj.ctx.settings
    model = interface.Role.composite(plugin_manager(settings))
    print_argspec(context, param, value, model=model)


class RoleCommands(CompositeCommandGroup[interface.Role]):
    """Group for 'role' sub-commands handling some of them that require a
    composite interface.Role model built from registered plugins at
    runtime.
    """

    model = interface.Role


@click.group("role", cls=RoleCommands)
@instance_identifier_option
@click.option(
    "--schema",
    is_flag=True,
    callback=print_role_schema,
    expose_value=False,
    is_eager=True,
    help="Print the JSON schema of role model and exit.",
)
@click.option(
    "--ansible-argspec",
    is_flag=True,
    callback=print_role_argspec,
    expose_value=False,
    is_eager=True,
    hidden=True,
    help="Print the Ansible argspec of role model and exit.",
)
def cli(instance: system.Instance) -> None:
    """Manage roles."""


# Help mypy because click.group() looses the type of 'cls' argument.
assert isinstance(cli, RoleCommands)


@cli.command_with_composite_model("create")
def _role_create(Role: type[interface.Role]) -> Callback:
    @helpers.parameters_from_model(Role, "create")
    @pass_instance
    @pass_ctx
    def command(ctx: Context, instance: system.Instance, role: interface.Role) -> None:
        """Create a role in a PostgreSQL instance"""
        with ctx.lock, postgresql.running(ctx, instance):
            if roles.exists(ctx, instance, role.name):
                raise click.ClickException("role already exists")
            roles.apply(ctx, instance, role)

    return command


@cli.command_with_composite_model("alter")
def _role_alter(Role: type[interface.Role]) -> Callback:
    @helpers.parameters_from_model(Role, "update", parse_model=False)
    @click.argument("rolname")
    @pass_instance
    @pass_ctx
    def command(
        ctx: Context, instance: system.Instance, rolname: str, **changes: Any
    ) -> None:
        """Alter a role in a PostgreSQL instance"""
        with ctx.lock, postgresql.running(ctx, instance):
            values = roles.get(ctx, instance, rolname).dict()
            values = deep_update(values, changes)
            altered = Role.parse_obj(values)
            roles.apply(ctx, instance, altered)

    return command


@cli.command("apply", hidden=True)
@click.option("-f", "--file", type=click.File("r"), metavar="MANIFEST", required=True)
@output_format_option
@dry_run_option
@pass_instance
@pass_ctx
def role_apply(
    ctx: Context,
    instance: system.Instance,
    file: IO[str],
    output_format: OutputFormat,
    dry_run: bool,
) -> None:
    """Apply manifest as a role"""
    p = plugin_manager(ctx.settings)
    model = interface.Role.composite(p)
    role = model.parse_yaml(file)
    if dry_run:
        ret = interface.ApplyResult(change_state=None)
    else:
        with ctx.lock, postgresql.running(ctx, instance):
            ret = roles.apply(ctx, instance, role)
    if output_format == OutputFormat.json:
        print_json_for(ret)


@cli.command("list")
@output_format_option
@pass_instance
@pass_ctx
def role_list(
    ctx: Context,
    instance: system.Instance,
    output_format: OutputFormat,
) -> None:
    """List roles in instance"""

    with postgresql.running(ctx, instance):
        rls = [
            r.dict(by_alias=True, exclude={"pgpass"}) for r in roles.ls(ctx, instance)
        ]

    if output_format == OutputFormat.json:
        print_json_for(rls)
    else:
        print_table_for(rls)


@cli.command("get")
@output_format_option
@click.argument("name")
@pass_instance
@pass_ctx
def role_get(
    ctx: Context,
    instance: system.Instance,
    name: str,
    output_format: OutputFormat,
) -> None:
    """Get the description of a role"""
    with postgresql.running(ctx, instance):
        m = roles.get(ctx, instance, name).dict(by_alias=True)
    if output_format == OutputFormat.json:
        print_json_for(m)
    else:
        print_table_for([m], box=None)


@cli.command("drop")
@helpers.parameters_from_model(interface.RoleDropped, "create")
@pass_instance
@pass_ctx
def role_drop(
    ctx: Context, instance: system.Instance, roledropped: interface.RoleDropped
) -> None:
    """Drop a role"""
    with postgresql.running(ctx, instance):
        roles.drop(ctx, instance, roledropped)


@cli.command("privileges")
@click.argument("name")
@click.option(
    "-d", "--database", "databases", multiple=True, help="Database to inspect"
)
@click.option("--default", "defaults", is_flag=True, help="Display default privileges")
@output_format_option
@pass_instance
@pass_ctx
def role_privileges(
    ctx: Context,
    instance: system.Instance,
    name: str,
    databases: Sequence[str],
    defaults: bool,
    output_format: OutputFormat,
) -> None:
    """List privileges of a role."""
    with postgresql.running(ctx, instance):
        roles.get(ctx, instance, name)  # check existence
        try:
            prvlgs = privileges.get(
                ctx, instance, databases=databases, roles=(name,), defaults=defaults
            )
        except ValueError as e:
            raise click.ClickException(str(e))
    if output_format == OutputFormat.json:
        print_json_for(i.dict(by_alias=True) for i in prvlgs)
    else:
        print_table_for(i.dict(by_alias=True) for i in prvlgs)
