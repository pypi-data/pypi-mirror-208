import importlib
from types import ModuleType
from typing import Any, Optional

import pluggy

from . import __name__ as pkgname
from . import hookspecs, settings
from ._compat import Self


class PluginManager(pluggy.PluginManager):  # type: ignore[misc]
    modules = (
        "postgresql",
        "databases",
        "passfile",
        "backup",
        "logrotate",
        "pgbackrest",
        "patroni",
        "pgbackrest.repo_host",
        "pgbackrest.repo_path",
        "prometheus",
        "powa",
        "rsyslog",
        "temboard",
        "systemd.service_manager",
        "systemd.scheduler",
    )

    @classmethod
    def all(cls) -> Self:
        """Return a PluginManager with all modules registered."""
        self = cls(pkgname)
        self.add_hookspecs(hookspecs)
        for hname in cls.modules:
            hm = importlib.import_module(f"{pkgname}.{hname}")
            self.register(hm)
        return self

    @classmethod
    def get(cls, settings: settings.Settings) -> Self:
        """Return a PluginManager based on 'settings'."""
        self = cls(pkgname)
        self.add_hookspecs(hookspecs)
        for hname in cls.modules:
            hm = importlib.import_module(f"{pkgname}.{hname}")
            if not hasattr(hm, "register_if") or hm.register_if(settings):
                self.register(hm)
        return self

    def register(self, plugin: Any, name: Optional[str] = None) -> Any:
        rv = super().register(plugin, name)
        assert self.get_hookcallers(plugin), f"{plugin} has no hook caller"
        return rv

    def unregister_all(self) -> list[ModuleType]:
        unregistered = []
        for __, plugin in self.list_name_plugin():
            self.unregister(plugin)
            unregistered.append(plugin)
        return unregistered

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.get_plugins() == other.get_plugins()  # type: ignore[no-any-return]
