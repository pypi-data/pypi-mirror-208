import importlib.resources
import sys
from typing import Optional

if sys.version_info[:2] >= (3, 11):
    from typing import Self

    def read_resource(pkgname: str, name: str) -> Optional[str]:
        resource = importlib.resources.files(pkgname).joinpath(name)
        if resource.is_file():
            return resource.read_text()
        return None

else:
    from typing_extensions import Self

    def read_resource(pkgname: str, name: str) -> Optional[str]:
        if importlib.resources.is_resource(pkgname, name):
            return importlib.resources.read_text(pkgname, name)
        return None


__all__ = [
    "Self",
    "read_resource",
]
