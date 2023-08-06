import logging
from functools import cached_property
from pathlib import Path
from typing import Optional

from filelock import FileLock

from . import plugin_manager, util
from .settings import Settings

logger = logging.getLogger(__name__)


class Context:
    """Execution context."""

    def __init__(self, *, settings: Settings) -> None:
        self.settings = settings
        pm = plugin_manager(settings)
        self.hook = pm.hook

    def rmtree(self, path: Path, ignore_errors: bool = False) -> None:
        util.rmtree(path, ignore_errors)

    def confirm(self, message: str, default: bool) -> bool:
        """Possible ask for confirmation of an action before running.

        Interactive implementations should prompt for confirmation with
        'message' and use the 'default' value as default. Non-interactive
        implementations (this one), will always return the 'default' value.
        """
        return default

    def prompt(self, message: str, hide_input: bool = False) -> Optional[str]:
        """Possible ask for user input.

        Interactive implementation should prompt for input with 'message' and
        return a string value. Non-Interactive implementations (this one), will
        always return None.
        """
        return None

    @cached_property
    def lock(self) -> FileLock:
        """Lock to prevent concurrent execution."""
        lockfile = self.settings.cli.lock_file
        lockfile.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        return FileLock(lockfile, timeout=0)
