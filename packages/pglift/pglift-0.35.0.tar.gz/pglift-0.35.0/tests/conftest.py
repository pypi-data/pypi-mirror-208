import logging
import pathlib
import shutil
from collections.abc import Iterator
from typing import Any, Callable, Optional
from unittest.mock import MagicMock, patch

import port_for
import pytest

from .certificates import CA
from .etcd import Etcd

default_pg_version: Optional[str]
try:
    from pglift.settings import _postgresql_bindir_version

    default_pg_version = _postgresql_bindir_version()[1]
except (ImportError, OSError):
    default_pg_version = None


def pytest_addoption(parser: Any) -> None:
    try:
        from pglift.settings import PostgreSQLVersion
    except ImportError:
        pass
    else:
        parser.addoption(
            "--pg-version",
            choices=list(PostgreSQLVersion),
            help="Run tests with specified PostgreSQL version (default: %(default)s)",
        )
    parser.addoption(
        "--no-plugins",
        action="store_true",
        default=False,
        help="Run tests without any pglift plugin loaded.",
    )


def pytest_report_header(config: Any) -> list[str]:
    try:
        pg_version = config.option.pg_version or default_pg_version
    except AttributeError:
        return []
    return [f"postgresql: {pg_version}"]


@pytest.fixture(scope="session")
def no_plugins(request: Any) -> bool:
    value = request.config.option.no_plugins
    assert isinstance(value, bool)
    return value


@pytest.fixture
def datadir() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def logger() -> logging.Logger:
    return logging.getLogger("pglift-tests")


@pytest.fixture(scope="session", autouse=True)
def _log_level(logger: logging.Logger) -> None:
    logging.getLogger("pglift").setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)


@pytest.fixture(scope="session", autouse=True)
def site_config() -> Iterator[Callable[..., Optional[str]]]:
    """Avoid looking up for configuration files in site directories, fall back
    to distribution one.
    """
    try:
        from pglift import util
    except ImportError:
        yield  # type: ignore[misc]
        return

    with patch("pglift.util.site_config", new=util.dist_config) as fn:
        yield fn


@pytest.fixture(autouse=True)
def site_settings() -> Iterator[MagicMock]:
    """Prevent lookup of site settings in XDG user directory or /etc."""
    try:
        from pglift.settings import SiteSettings
    except ImportError:
        yield  # type: ignore[misc]
        return

    with patch.object(SiteSettings, "site_settings", return_value=None) as m:
        yield m


@pytest.fixture(scope="session")
def pg_bindir(request: Any) -> tuple[pathlib.Path, str]:
    from pglift.settings import bindir

    # --pg-version option should be available at this point
    version = request.config.option.pg_version or default_pg_version
    if version is None:
        pytest.skip("no PostgreSQL installation found")
    assert isinstance(version, str)
    assert bindir is not None  # otherwise, version would be None too.
    return pathlib.Path(bindir.format(version=version)), version


@pytest.fixture(scope="session")
def pg_version(pg_bindir: tuple[pathlib.Path, str]) -> str:
    return pg_bindir[1]


@pytest.fixture(scope="session")
def pgbackrest_available(no_plugins: bool) -> bool:
    if no_plugins:
        return False
    return shutil.which("pgbackrest") is not None


@pytest.fixture(scope="session")
def prometheus_execpath(no_plugins: bool) -> Optional[pathlib.Path]:
    if no_plugins:
        return None
    for name in ("prometheus-postgres-exporter", "postgres_exporter"):
        path = shutil.which(name)
        if path is not None:
            return pathlib.Path(path)
    return None


@pytest.fixture(scope="session")
def temboard_execpath(no_plugins: bool) -> Optional[pathlib.Path]:
    if no_plugins:
        return None
    path = shutil.which("temboard-agent")
    if path is not None:
        return pathlib.Path(path)
    return None


@pytest.fixture(scope="session")
def patroni_execpath(no_plugins: bool) -> Optional[pathlib.Path]:
    if no_plugins:
        return None
    path = shutil.which("patroni")
    if path is not None:
        return pathlib.Path(path)
    return None


@pytest.fixture(scope="package")
def tmp_port_factory() -> Iterator[int]:
    """Return a generator producing available and distinct TCP ports."""

    def available_ports() -> Iterator[int]:
        used: set[int] = set()
        while True:
            port = port_for.select_random(exclude_ports=list(used))
            used.add(port)
            yield port

    return available_ports()


@pytest.fixture(scope="package")
def etcd() -> str:
    p = shutil.which("etcd")
    if p is None:
        pytest.skip("etcd executable not found")
    return p


@pytest.fixture(scope="package")
def etcd_host(
    etcd: str, tmp_path_factory: pytest.TempPathFactory, tmp_port_factory: Iterator[int]
) -> Etcd:
    return Etcd(
        execpath=etcd,
        datadir=tmp_path_factory.mktemp("etcd"),
        client_port=next(tmp_port_factory),
        peer_port=next(tmp_port_factory),
    )


@pytest.fixture(scope="package")
def ca(tmp_path_factory: pytest.TempPathFactory) -> CA:
    return CA.make(tmp_path_factory.mktemp("ca-certs"), "pglift-tests-ca")
