import functools
import json
import socket
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Optional, Union

import attr
import pgtoolkit.conf
import yaml
from pydantic import BaseModel, Field, validator

from .. import plugin_manager, types
from .._compat import Self
from . import impl

if TYPE_CHECKING:
    from ..models import interface, system
    from ..settings import PatroniSettings, Settings


class _BaseModel(BaseModel):
    class Config:
        allow_mutation = False
        extra = "allow"
        smart_union = True
        validate_always = True
        validate_assignment = True


def bootstrap(manifest: "interface.Instance", settings: "Settings") -> dict[str, Any]:
    """Return values for the "bootstrap" section of Patroni configuration."""
    patroni_settings = settings.patroni
    assert patroni_settings
    initdb_options = manifest.initdb_options(settings.postgresql.initdb)
    initdb: list[Union[str, dict[str, str]]] = [
        {key: value}
        for key, value in initdb_options.dict(exclude_none=True).items()
        if key != "data_checksums"
    ]
    if initdb_options.data_checksums:
        initdb.append("data-checksums")
    pg_hba = manifest.pg_hba(settings).splitlines()
    pg_ident = manifest.pg_ident(settings).splitlines()
    return dict(
        dcs={"loop_wait": patroni_settings.loop_wait},
        initdb=initdb,
        pg_hba=pg_hba,
        pg_ident=pg_ident,
    )


def postgresql(
    instance: "system.BaseInstance",
    manifest: "interface.Instance",
    configuration: pgtoolkit.conf.Configuration,
    postgresql_connect_host: Optional[str],
    **args: Any,
) -> dict[str, Any]:
    """Return values for the "postgresql" section of Patroni configuration.

    Any values from `**args` are used over default values that would be
    inferred but values from `manifest` still take precedence.
    """
    settings = instance._settings
    if "authentication" not in args:

        def r(role: "interface.Role") -> dict[str, str]:
            d = {"username": role.name}
            if role.password:
                d["password"] = role.password.get_secret_value()
            return d

        args["authentication"] = {
            "superuser": r(manifest.surole(settings)),
            "replication": r(manifest.replrole(settings)),
        }
        args["authentication"]["rewind"] = args["authentication"]["superuser"]

    if postgresql_connect_host is not None:
        args["connect_address"] = types.Address.validate(
            f"{postgresql_connect_host}:{manifest.port}"
        )
    else:
        args["connect_address"] = types.Address.get(manifest.port)

    def s(entry: pgtoolkit.conf.Entry) -> Union[str, bool, int, float]:
        # Serialize pgtoolkit entry without quoting; specially needed to
        # timedelta.
        if isinstance(entry.value, timedelta):
            return entry.serialize().strip("'")
        return entry.value

    parameters = args.setdefault("parameters", {})
    parameters.update({k: s(e) for k, e in sorted(configuration.entries.items())})

    listen_addresses = parameters.get("listen_addresses", "*")
    args["listen"] = types.Address.validate(f"{listen_addresses}:{manifest.port}")

    args.setdefault("use_unix_socket", True)
    args.setdefault("use_unix_socket_repl", True)
    args.setdefault("data_dir", instance.datadir)
    args.setdefault("bin_dir", instance.bindir)
    if "pg_hba" not in args:
        args["pg_hba"] = manifest.pg_hba(settings).splitlines()
    if "pg_ident" not in args:
        args["pg_ident"] = manifest.pg_ident(settings).splitlines()

    if "create_replica_methods" not in args:
        args["create_replica_methods"] = []
        pm = plugin_manager(settings)
        for method, config in pm.hook.patroni_create_replica_method(
            manifest=manifest, instance=instance
        ):
            args["create_replica_methods"].append(method)
            args[method] = config
        args["create_replica_methods"].append("basebackup")
    return args


class RESTAPI(_BaseModel):
    connect_address: types.Address = Field(
        default_factory=functools.partial(types.Address.get, port=8008),
        description="IP address (or hostname) and port, to access the Patroni's REST API.",
    )
    listen: types.Address = Field(
        default_factory=types.Address.unspecified,
        description="IP address (or hostname) and port that Patroni will listen to for the REST API. Defaults to connect_address if not provided.",
    )

    @validator("listen", always=True, pre=True)
    def __validate_listen_(cls, value: str, values: dict[str, Any]) -> str:
        """Set 'listen' from 'connect_address' if unspecified.

        >>> RESTAPI()  # doctest: +ELLIPSIS
        RESTAPI(connect_address='...:8008', listen='...:8008')
        >>> RESTAPI(connect_address="localhost:8008")
        RESTAPI(connect_address='localhost:8008', listen='localhost:8008')
        >>> RESTAPI(connect_address="localhost:8008", listen="server:123")
        RESTAPI(connect_address='localhost:8008', listen='server:123')
        """
        if not value:
            value = values["connect_address"]
            assert isinstance(value, str)
        return value


class Patroni(_BaseModel):
    """A Patroni instance."""

    class PostgreSQL(_BaseModel):
        connect_address: types.Address
        listen: types.Address
        parameters: dict[str, Any]

    class RESTAPI_(RESTAPI):
        cafile: Optional[Path] = None
        certfile: Optional[Path] = None
        keyfile: Optional[Path] = None
        verify_client: Optional[Literal["optional", "required"]] = None

    scope: str = Field(description="Cluster name.")
    name: str = Field(description="Host name.")
    restapi: RESTAPI_ = Field(default_factory=RESTAPI_)
    postgresql: PostgreSQL

    @classmethod
    def build(
        cls,
        postgresql_connect_host: Optional[str],
        instance: "system.BaseInstance",
        manifest: "interface.Instance",
        configuration: pgtoolkit.conf.Configuration,
        **args: Any,
    ) -> Self:
        if "bootstrap" not in args:
            args["bootstrap"] = bootstrap(manifest, instance._settings)
        args["postgresql"] = postgresql(
            instance,
            manifest,
            configuration,
            postgresql_connect_host,
            **args.pop("postgresql", {}),
        )
        return cls(**args)

    def yaml(self) -> str:
        data = json.loads(self.json(exclude_none=True))
        return yaml.dump(data, sort_keys=True)  # type: ignore[no-any-return]


@attr.s(auto_attribs=True, frozen=True, slots=True)
class Service:
    """A Patroni service bound to a PostgreSQL instance."""

    __service_name__: ClassVar = "patroni"
    cluster: str
    node: str
    name: str
    settings: "PatroniSettings"

    def __str__(self) -> str:
        return f"{self.__service_name__}@{self.name}"

    def args(self) -> list[str]:
        configpath = impl._configpath(self.name, self.settings)
        return [str(self.settings.execpath), str(configpath)]

    def pidfile(self) -> Path:
        return Path(str(self.settings.pid_file).format(name=self.name))

    def env(self) -> None:
        return None


class ClusterMember(BaseModel):
    """An item of the list of members returned by Patroni API /cluster endpoint."""

    class Config:
        extra = "allow"
        frozen = True

    host: str
    name: str
    port: int
    role: str
    state: str


class ServiceManifest(types.ServiceManifest, service_name="patroni"):
    _cli_config: ClassVar[dict[str, types.CLIConfig]] = {
        "cluster_members": {"hide": True},
    }
    _ansible_config: ClassVar[dict[str, types.AnsibleConfig]] = {
        "cluster_members": {"hide": True},
    }

    # XXX Or simply use instance.qualname?
    cluster: str = Field(
        description="Name (scope) of the Patroni cluster.",
        readOnly=True,
    )
    node: str = Field(
        default_factory=socket.getfqdn,
        description="Name of the node (usually the host name).",
        readOnly=True,
    )
    restapi: RESTAPI = Field(
        default_factory=RESTAPI, description="REST API configuration"
    )
    postgresql_connect_host: Optional[str] = Field(
        default=None,
        description="Host or IP address through which PostgreSQL is externally accessible.",
    )
    cluster_members: list[ClusterMember] = Field(
        default=[],
        description="Members of the Patroni this instance is member of.",
        readOnly=True,
    )

    __validate_none_values_ = validator("node", "restapi", pre=True, allow_reuse=True)(
        types.default_if_none
    )
