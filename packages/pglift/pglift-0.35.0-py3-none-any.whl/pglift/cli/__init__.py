import json
import logging
import pathlib
import sys
from collections import OrderedDict
from functools import partial
from typing import Literal, Optional, Union

import click
import click.exceptions
import rich.logging
import rich.prompt
import rich.text
import rich.tree
import yaml
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.syntax import Syntax

from .. import __name__ as pkgname
from .. import _install, plugin_manager, version
from ..ctx import Context
from ..settings import Settings
from . import database, instance, pgconf, postgres, role
from .util import (
    Group,
    InvalidSettingsError,
    LogDisplayer,
    Obj,
    OutputFormat,
    output_format_option,
    pass_ctx,
)

logger = logging.getLogger(__name__)


class CLIGroup(Group):
    """Group gathering main commands (defined here), commands from submodules
    and commands from plugins.
    """

    submodules = OrderedDict(
        [
            ("instance", instance.cli),
            ("pgconf", pgconf.cli),
            ("role", role.cli),
            ("database", database.cli),
            ("postgres", postgres.cli),
        ]
    )

    def list_commands(self, context: click.Context) -> list[str]:
        main_commands = super().list_commands(context)
        obj: Optional[Obj] = context.obj
        if obj is None:
            try:
                obj = context.ensure_object(Obj)
            except InvalidSettingsError:
                return []
        plugins_commands = sorted(g.name for g in obj.ctx.hook.cli())
        return main_commands + list(self.submodules) + plugins_commands

    def get_command(
        self, context: click.Context, cmd_name: str
    ) -> Optional[click.Command]:
        main_command = super().get_command(context, cmd_name)
        if main_command is not None:
            return main_command
        try:
            cmd = self.submodules[cmd_name]
        except KeyError:
            pass
        else:
            assert isinstance(cmd, click.Command), cmd
            return cmd
        obj: Optional[Obj] = context.obj
        if obj is None:
            obj = context.ensure_object(Obj)
        for group in obj.ctx.hook.cli():
            assert isinstance(group, click.Command)
            if group.name == cmd_name:
                return group
        return None


def completion(
    context: click.Context,
    param: click.Parameter,
    value: Literal["bash", "fish", "zsh"],
) -> None:
    if not value or context.resilient_parsing:
        return
    shell_complete_class_map = {
        "bash": click.shell_completion.BashComplete,
        "fish": click.shell_completion.FishComplete,
        "zsh": click.shell_completion.ZshComplete,
    }
    click.echo(
        shell_complete_class_map[value](cli, {}, "pglift", "_PGLIFT_COMPLETE").source(),
        nl=False,
    )
    context.exit()


def print_version(context: click.Context, param: click.Parameter, value: bool) -> None:
    if not value or context.resilient_parsing:
        return
    click.echo(f"pglift version {version()}")
    context.exit()


def log_level(
    context: click.Context, param: click.Parameter, value: Optional[str]
) -> Optional[int]:
    if value is None:
        return None
    return getattr(logging, value)  # type: ignore[no-any-return]


@click.group(cls=CLIGroup)
@click.option(
    "-L",
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default=None,
    callback=log_level,
    help="Set log threshold (default to INFO when logging to stderr or WARNING when logging to a file).",
)
@click.option(
    "-l",
    "--log-file",
    type=click.Path(dir_okay=False, resolve_path=True, path_type=pathlib.Path),
    metavar="LOGFILE",
    help="Write logs to LOGFILE, instead of stderr.",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    hidden=True,
    help="Set log level to DEBUG and eventually display tracebacks.",
)
@click.option(
    "--interactive/--non-interactive",
    default=True,
    help=(
        "Interactively prompt for confirmation when needed (the default), "
        "or automatically pick the default option for all choices."
    ),
)
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show program version.",
)
@click.option(
    "--completion",
    type=click.Choice(["bash", "fish", "zsh"]),
    callback=completion,
    expose_value=False,
    is_eager=True,
    help="Output completion for specified shell and exit.",
)
@click.pass_context
def cli(
    context: click.Context,
    log_level: Optional[int],
    log_file: Optional[pathlib.Path],
    debug: bool,
    interactive: bool,
) -> None:
    """Deploy production-ready instances of PostgreSQL"""
    if not context.obj:
        context.obj = Obj(
            displayer=None if log_file else LogDisplayer(),
            interactive=interactive,
            debug=debug,
        )
    else:
        assert isinstance(context.obj, Obj), context.obj

    settings: Settings = context.obj.ctx.settings
    loggers = [logging.getLogger(n) for n in (pkgname, "filelock")]
    for logger in loggers:
        logger.setLevel(logging.DEBUG)
    handler: Union[logging.Handler, rich.logging.RichHandler]
    if log_file or not sys.stderr.isatty():
        if log_file:
            handler = logging.FileHandler(log_file)
            context.call_on_close(handler.close)
        else:
            handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            fmt=settings.cli.log_format, datefmt=settings.cli.date_format
        )
        handler.setFormatter(formatter)
        handler.setLevel(log_level or logging.WARNING)
    else:
        if debug:
            log_level = logging.DEBUG
        handler = rich.logging.RichHandler(
            level=log_level or logging.INFO,
            console=Console(stderr=True),
            show_time=False,
            show_path=False,
            highlighter=NullHighlighter(),
        )
    for logger in loggers:
        logger.addHandler(handler)
    # Remove rich handler on close since this would pollute all tests stderr
    # otherwise.
    context.call_on_close(partial(logger.removeHandler, handler))


@cli.command("site-settings", hidden=True)
@click.option(
    "--defaults/--no-defaults",
    default=None,
    help="Output only default settings, or only site configuration.",
    show_default=True,
)
@click.option(
    "--schema", is_flag=True, help="Print the JSON Schema of site settings model."
)
@output_format_option
@pass_ctx
def site_settings(
    ctx: Context, defaults: Optional[bool], schema: bool, output_format: OutputFormat
) -> None:
    """Show site settings.

    Without any option, the combination of site configuration and default
    values is shown.
    With --defaults, only default values and those depending on the
    environment are shown (not accounting for site configuration).
    With --no-defaults, the site configuration is shown alone and default
    values are excluded.
    """
    if schema:
        output = Settings.schema_json()
    else:
        if defaults:
            output = Settings().json()
        else:
            output = ctx.settings.json(exclude_defaults=defaults is False)
    if output_format == OutputFormat.json:
        rich.print_json(output)
    else:
        assert output_format is None
        output = yaml.safe_dump(json.loads(output))
        syntax = Syntax(output, "yaml", background_color="default")
        rich.print(syntax)


@cli.command(
    "site-configure",
    hidden=True,
)
@click.argument(
    "action", type=click.Choice(["install", "uninstall"]), default="install"
)
@click.option(
    "--settings",
    type=click.Path(exists=True, path_type=pathlib.Path),
    help="Custom settings file.",
)
@pass_ctx
def site_configure(
    ctx: Context,
    action: Literal["install", "uninstall"],
    settings: Optional[pathlib.Path],
) -> None:
    """Manage installation of extra data files for pglift.

    This is an INTERNAL command.
    """
    pm = plugin_manager(ctx.settings)
    with ctx.lock:
        if action == "install":
            env = f"SETTINGS=@{settings}" if settings else None
            _install.do(pm, ctx.settings, env=env)
        elif action == "uninstall":
            _install.undo(pm, ctx.settings, ctx)
