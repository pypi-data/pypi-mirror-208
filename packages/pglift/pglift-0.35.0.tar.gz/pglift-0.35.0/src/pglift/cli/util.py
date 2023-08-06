import abc
import enum
import json
import logging
import os
import pathlib
import tempfile
import time
from collections.abc import Iterable, Iterator, Mapping
from contextlib import contextmanager
from functools import cache, singledispatch, wraps
from types import ModuleType
from typing import Any, Callable, Generic, Optional, TypeVar, Union

import click
import filelock
import psycopg
import pydantic
import pydantic.json
import rich
from click.shell_completion import CompletionItem
from pydantic import ByteSize
from rich.table import Table
from typing_extensions import ParamSpec

from .. import __name__ as pkgname
from .. import exceptions, instances, plugin_manager, task
from ..ctx import Context
from ..models import helpers, system
from ..settings import PostgreSQLVersion, SiteSettings
from ..task import Displayer
from ..types import AutoStrEnum, CompositeManifest

logger = logging.getLogger(pkgname)


@singledispatch
def prettify(value: Any) -> str:
    """Prettify a value

    The prettification will depend on value type.

    >>> prettify(ByteSize(1024))
    '1.0KiB'
    >>> prettify([None, 1, "foo"])
    'None, 1, foo'
    >>> prettify({"z", "b", "a"})
    'a, b, z'
    >>> prettify(None)
    ''
    >>> prettify({"foo": "bob"})
    'foo: bob'
    """
    return str(value)


@prettify.register(ByteSize)
def _(value: ByteSize) -> str:
    """Prettify a ByteSize value"""
    return value.human_readable()


@prettify.register(list)
def _(value: list[Any]) -> str:
    """Prettify a List value"""
    return ", ".join(str(x) for x in value)


@prettify.register(set)
def _(value: set[Any]) -> str:
    """Prettify a Set value"""
    return prettify(sorted(value))


@prettify.register(type(None))
def _(value: None) -> str:
    """Prettify a None value"""
    return ""


@prettify.register(dict)
def _(value: dict[str, Any]) -> str:
    """Prettify a Dict value.

    >>> print(prettify({"foo": "bob", "bar": {"blah": ["some", 123]}}))
    foo: bob
    bar:
      blah: some, 123
    """

    def prettify_dict(
        d: dict[str, Any], level: int = 0, indent: str = "  "
    ) -> Iterator[str]:
        for key, value in d.items():
            row = f"{indent * level}{key}:"
            if isinstance(value, dict):
                yield row
                yield from prettify_dict(value, level + 1)
            else:
                yield row + " " + prettify(value)

    return "\n".join(prettify_dict(value))


def print_table_for(
    items: Iterable[Mapping[str, Any]],
    title: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """Render a list of items as a table.

    >>> class Address(pydantic.BaseModel):
    ...     street: str
    ...     zipcode: int = pydantic.Field(alias="zip")
    ...     city: str
    >>> class Person(pydantic.BaseModel):
    ...     name: str
    ...     children: Optional[list[str]]
    ...     address: Address
    >>> items = [Person(name="bob", children=["marley", "dylan"],
    ...                 address=Address(street="main street", zip=31234, city="luz")),
    ...          Person(name="janis", children=None,
    ...                 address=Address(street="robinson lane", zip=38650, city="mars"))]
    >>> print_table_for((i.dict(by_alias=True) for i in items), title="address book")  # doctest: +NORMALIZE_WHITESPACE
                      address book
    ┏━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ name  ┃ children      ┃ address               ┃
    ┡━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
    │ bob   │ marley, dylan │ street: main street   │
    │       │               │ zip: 31234            │
    │       │               │ city: luz             │
    │ janis │               │ street: robinson lane │
    │       │               │ zip: 38650            │
    │       │               │ city: mars            │
    └───────┴───────────────┴───────────────────────┘
    """
    table = None
    headers: list[str] = []
    rows = []
    for item in items:
        row = []
        hdr = []
        for k, v in list(item.items()):
            hdr.append(k)
            row.append(prettify(v))
        if not headers:
            headers = hdr[:]
        rows.append(row)
    if not rows:
        return
    table = Table(*headers, title=title, **kwargs)
    for row in rows:
        table.add_row(*row)
    rich.print(table)


def print_json_for(data: Any) -> None:
    """Render `data` as JSON.

    >>> class Foo(pydantic.BaseModel):
    ...     bar_: str = pydantic.Field(alias="bar")
    ...     baz: int
    >>> items = [Foo(bar="x", baz=1), Foo(bar="y", baz=3)]
    >>> print_json_for(items)
    [
      {
        "bar_": "x",
        "baz": 1
      },
      {
        "bar_": "y",
        "baz": 3
      }
    ]
    >>> print_json_for(items[0].dict(by_alias=True))
    {
      "bar": "x",
      "baz": 1
    }
    """
    rich.print_json(json.dumps(data, default=pydantic.json.pydantic_encoder))


P = ParamSpec("P")


def print_schema(
    context: click.Context,
    param: click.Parameter,
    value: bool,
    *,
    model: type[pydantic.BaseModel],
) -> None:
    """Callback for --schema flag."""
    if value:
        rich.print_json(model.schema_json(indent=2))
        context.exit()


def print_argspec(
    context: click.Context,
    param: click.Parameter,
    value: bool,
    *,
    model: type[pydantic.BaseModel],
) -> None:
    """Callback for --ansible-argspec flag."""
    if value:
        click.echo(
            json.dumps(helpers.argspec_from_model(model), sort_keys=False, indent=2)
        )
        context.exit()


def pass_ctx(f: Callable[P, None]) -> Callable[P, None]:
    """Command decorator passing 'Context' bound to click.Context's object."""

    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        context = click.get_current_context()
        ctx: Context = context.obj.ctx
        assert isinstance(ctx, Context), ctx
        context.invoke(f, ctx, *args, **kwargs)

    return wrapper


def pass_instance(f: Callable[P, None]) -> Callable[P, None]:
    """Command decorator passing 'instance' bound to click.Context's object."""

    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        context = click.get_current_context()
        instance = context.obj.instance
        assert isinstance(instance, system.Instance), instance
        context.invoke(f, instance, *args, **kwargs)

    return wrapper


def pass_component_settings(
    mod: ModuleType, name: str, f: Callable[P, None]
) -> Callable[P, None]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        context = click.get_current_context()
        ctx: Context = context.obj.ctx
        assert isinstance(ctx, Context), ctx
        settings = mod.available(ctx.settings)
        assert settings
        context.invoke(f, settings, *args, **kwargs)

    return wrapper


def get_instance(ctx: Context, name: str, version: Optional[str]) -> system.Instance:
    """Return an Instance from name/version, possibly guessing version if unspecified."""
    if version is None:
        found = None
        for version in PostgreSQLVersion:
            try:
                instance = system.Instance.system_lookup(ctx, (name, version))
            except exceptions.InstanceNotFound:
                logger.debug("instance '%s' not found in version %s", name, version)
            else:
                if found:
                    raise click.BadParameter(
                        f"instance '{name}' exists in several PostgreSQL versions;"
                        " please select version explicitly"
                    )
                found = instance

        if found:
            return found

        raise click.BadParameter(f"instance '{name}' not found")

    try:
        return system.Instance.system_lookup(ctx, (name, version))
    except Exception as e:
        raise click.BadParameter(str(e))


def nameversion_from_id(instance_id: str) -> tuple[str, Optional[str]]:
    version = None
    try:
        version, name = instance_id.split("/", 1)
    except ValueError:
        name = instance_id
    return name, version


def instance_lookup(
    context: click.Context, param: click.Parameter, value: Union[None, str, tuple[str]]
) -> Union[system.Instance, tuple[system.Instance, ...]]:
    """Return one or more system.Instance, possibly guessed if there is only
    one on system, depending on 'param' variadic flag (nargs).
    """

    ctx: Context = context.obj.ctx

    def guess() -> tuple[str, Optional[str]]:
        """Return (name, version) of the instance found on system, if there's
        only one, or fail.
        """
        try:
            (i,) = instances.system_list(ctx)
        except ValueError:
            raise click.UsageError(
                f"argument {param.get_error_hint(context)} is required."
            )
        return i.name, i.version

    if context.params.get("all_instances"):
        return tuple(
            get_instance(ctx, i.name, i.version) for i in instances.system_list(ctx)
        )

    if param.nargs == 1:
        if value is None:
            name, version = guess()
        else:
            assert isinstance(value, str)
            name, version = nameversion_from_id(value)
        return get_instance(ctx, name, version)

    elif param.nargs == -1:
        assert isinstance(value, tuple)
        if value:
            return tuple(
                get_instance(ctx, *nameversion_from_id(item)) for item in value
            )
        else:
            name, version = guess()
            return (get_instance(ctx, name, version),)

    else:
        raise AssertionError(f"unexpected nargs={param.nargs}")


def instance_bind_context(
    context: click.Context, param: click.Parameter, value: Optional[str]
) -> system.Instance:
    """Bind instance specified as -i/--instance to context's object, possibly
    guessing from available instance if there is only one.
    """
    obj: Obj = context.obj
    ctx = obj.ctx
    version: Optional[str]
    if value is None:
        try:
            (i,) = instances.ls(ctx)
        except ValueError:
            raise click.UsageError(
                f"option {param.get_error_hint(context)} is required."
            )
        name, version = i.name, i.version
    else:
        name, version = nameversion_from_id(value)
    instance = get_instance(ctx, name, version)
    obj.instance = instance
    return instance


def _list_instances(
    context: click.Context, param: click.Parameter, incomplete: str
) -> list[CompletionItem]:
    """Shell completion function for instance identifier <name> or <version>/<name>."""
    out = []
    iname, iversion = nameversion_from_id(incomplete)
    ctx = Context(settings=SiteSettings())
    for i in instances.system_list(ctx):
        if iversion is not None and i.version.startswith(iversion):
            if i.name.startswith(iname):
                out.append(
                    CompletionItem(f"{i.version}/{i.name}", help=f"port={i.port}")
                )
            else:
                out.append(CompletionItem(i.version))
        else:
            out.append(
                CompletionItem(i.name, help=f"{i.version}/{i.name} port={i.port}")
            )
    return out


instance_identifier_option = click.option(
    "-i",
    "--instance",
    "instance",
    metavar="<version>/<name>",
    callback=instance_bind_context,
    shell_complete=_list_instances,
    help=(
        "Instance identifier; the <version>/ prefix may be omitted if "
        "there's only one instance matching <name>. "
        "Required if there is more than one instance on system."
    ),
)


class OutputFormat(AutoStrEnum):
    """Output format"""

    json = enum.auto()


output_format_option = click.option(
    "-o",
    "--output-format",
    type=click.Choice(helpers.choices_from_enum(OutputFormat), case_sensitive=False),
    help="Specify the output format.",
)

dry_run_option = click.option(
    "--dry-run", is_flag=True, help="Only validate input data."
)


def validate_foreground(
    context: click.Context, param: click.Parameter, value: bool
) -> bool:
    ctx: Context = context.obj.ctx
    if ctx.settings.service_manager == "systemd" and value:
        raise click.BadParameter("cannot be used with systemd")
    return value


foreground_option = click.option(
    "--foreground",
    is_flag=True,
    help="Start the program in foreground.",
    callback=validate_foreground,
)


@contextmanager
def command_logging(logdir: pathlib.Path) -> Iterator[None]:
    logdir_created = False
    logfilename = f"{time.time()}.log"
    logfile = logdir / logfilename
    try:
        if not logdir.exists():
            logdir.mkdir(parents=True)
            logdir_created = True
        handler = logging.FileHandler(logfile)
    except OSError:
        # Might be, e.g. PermissionError, if log file path is not writable.
        logfile = pathlib.Path(
            tempfile.NamedTemporaryFile(prefix="pglift", suffix=logfilename).name
        )
        handler = logging.FileHandler(logfile)
    formatter = logging.Formatter(
        fmt="%(levelname)-8s - %(asctime)s - %(name)s:%(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if logdir_created:
        logger.debug("created log directory %s", logdir)
    logger.debug("logging command at %s", logfile)
    keep_logfile = False
    try:
        yield None
    except (click.Abort, click.ClickException, click.exceptions.Exit):
        raise
    except Exception:
        keep_logfile = True
        logger.exception("an unexpected error occurred")
        raise click.ClickException(
            "an unexpected error occurred, this is probably a bug; "
            f"details can be found at {logfile}"
        )
    finally:
        if not keep_logfile:
            os.unlink(logfile)
            if logdir_created and next(logdir.iterdir(), None) is None:
                logger.debug("removing log directory %s", logdir)
                logdir.rmdir()


class InvalidSettingsError(click.ClickException):
    """Failure to load site settings."""

    def __init__(self, error: Exception) -> None:
        message = f"invalid site settings\n{error}"
        super().__init__(message)


class LogDisplayer:
    def handle(self, msg: str) -> None:
        logger.info(msg)


class CLIContext(Context):
    """Default CLI context, non-interactive."""

    def confirm(self, message: str, default: bool) -> bool:
        return default


class InteractiveCLIContext(CLIContext):
    """An interactive CLI context that prompts for confirmation."""

    def confirm(self, message: str, default: bool) -> bool:
        return rich.prompt.Confirm().ask(
            f"[yellow]>[/yellow] {message}", default=default
        )

    @cache
    def prompt(self, message: str, hide_input: bool = False) -> str:
        return rich.prompt.Prompt().ask(
            f"[yellow]>[/yellow] {message}", password=hide_input
        )


class Obj:
    """Object bound to click.Context"""

    def __init__(
        self,
        *,
        context: Optional[CLIContext] = None,
        displayer: Optional[Displayer] = None,
        interactive: bool = True,
        debug: bool = False,
    ) -> None:
        if context is None:
            cls = InteractiveCLIContext if interactive else CLIContext
            try:
                settings = SiteSettings()
            except (exceptions.SettingsError, pydantic.ValidationError) as e:
                raise InvalidSettingsError(e)
            except exceptions.UnsupportedError as e:
                raise click.ClickException(f"unsupported operation: {e}")
            context = cls(settings=settings)
        self.ctx = context
        self.displayer = displayer
        self.debug = debug
        # Set in commands taking a -i/--instance option through
        # instance_identifier_option decorator's callback.
        self.instance: Optional[system.Instance] = None


class Command(click.Command):
    def invoke(self, context: click.Context) -> Any:
        obj: Obj = context.obj
        ctx = obj.ctx
        displayer = context.obj.displayer
        logger = logging.getLogger(pkgname)
        with command_logging(ctx.settings.cli.logpath):
            try:
                with task.displayer_installed(displayer):
                    return super().invoke(context)
            except filelock.Timeout:
                raise click.ClickException("another operation is in progress")
            except exceptions.Cancelled as e:
                logger.warning(str(e))
                raise click.Abort
            except exceptions.Error as e:
                logger.debug("an internal error occurred", exc_info=obj.debug)
                msg = str(e)
                if isinstance(e, exceptions.CommandError):
                    if e.stderr:
                        msg += f"\n{e.stderr}"
                    if e.stdout:
                        msg += f"\n{e.stdout}"
                raise click.ClickException(msg)
            except pydantic.ValidationError as e:
                raise click.ClickException(str(e))
            except psycopg.OperationalError as e:
                logger.debug("an operational error occurred", exc_info=True)
                raise click.ClickException(str(e).strip())


class Group(click.Group):
    command_class = Command
    group_class = type

    def add_command(self, cmd: click.Command, name: Optional[str] = None) -> None:
        name = name or cmd.name
        assert name not in self.commands, f"command '{name}' already registered"
        super().add_command(cmd, name)


class PluggableCommandGroup(abc.ABC, Group):
    _plugin_commands_loaded: bool = False

    @abc.abstractmethod
    def register_plugin_commands(self, obj: Obj) -> None:
        ...

    def _load_plugins_commands(self, context: click.Context) -> None:
        if self._plugin_commands_loaded:
            return
        obj: Optional[Obj] = context.obj
        if obj is None:
            try:
                obj = context.ensure_object(Obj)
            except InvalidSettingsError:
                return
        if obj is None:
            return
        self.register_plugin_commands(obj)
        self._plugin_commands_loaded = True

    def list_commands(self, context: click.Context) -> list[str]:
        self._load_plugins_commands(context)
        return super().list_commands(context)

    def get_command(self, context: click.Context, name: str) -> Optional[click.Command]:
        self._load_plugins_commands(context)
        return super().get_command(context, name)


Callback = Callable[..., Any]

T = TypeVar("T", bound=CompositeManifest)
CommandFactory = Callable[[type[T]], Callback]


class CompositeCommandGroup(abc.ABC, Generic[T], Group):
    @property
    @abc.abstractmethod
    def model(self) -> type[T]:
        ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._composite_commands: dict[str, CommandFactory[T]] = {}
        super().__init__(*args, **kwargs)

    def command_with_composite_model(
        self, name: str
    ) -> Callable[[CommandFactory[T]], None]:
        """Decorator for callback that needs a composite model"""
        assert name not in self._composite_commands, name

        def decorator(factory: CommandFactory[T]) -> None:
            self._composite_commands[name] = factory

        return decorator

    def list_commands(self, context: click.Context) -> list[str]:
        return sorted(list(self._composite_commands) + super().list_commands(context))

    def get_command(self, context: click.Context, name: str) -> Optional[click.Command]:
        try:
            factory = self._composite_commands[name]
        except KeyError:
            return super().get_command(context, name)
        else:
            if context.obj is None:  # During shell complete.
                model = self.model
            else:
                obj: Obj = context.obj
                p = plugin_manager(obj.ctx.settings)
                model = self.model.composite(p)
            f = factory(model)
            return click.command(cls=Command)(f)
