from pathlib import Path

import pytest
from pgtoolkit import conf as pgconf

from pglift import conf
from pglift.settings import Settings


def test_read(pg_version: str, settings: Settings, tmp_path: Path) -> None:
    datadir = tmp_path
    postgresql_auto_conf = datadir / "postgresql.auto.conf"
    postgresql_auto_conf.write_text("primary_conn_info = host=primary\n")
    postgresql_conf = datadir / "postgresql.conf"
    postgresql_conf.write_text("\n".join(["bonjour = hello", "port=1234"]))

    config = conf.read(datadir)
    assert config.bonjour == "hello"
    assert config.port == 1234
    assert config.primary_conn_info == "host=primary"

    config = conf.read(datadir, managed_only=True)
    assert config.bonjour == "hello"
    assert config.port == 1234
    assert "primary_conn_info" not in config

    postgresql_conf.unlink()
    with pytest.raises(FileNotFoundError, match=str(postgresql_conf)):
        conf.read(datadir, True)


def test_update(datadir: Path, write_changes: bool) -> None:
    cfg = pgconf.parse(datadir / "postgresql.conf.sample")
    conf.update(
        cfg,
        max_connections=10,  # changed
        bonjour=True,  # uncommented
        log_destination="stderr",  # added
    )
    fpath = datadir / "postgresql.conf"
    if write_changes:
        cfg.save(fpath)
    expected = fpath.read_text().splitlines(keepends=True)
    assert cfg.lines == expected


def test_changes() -> None:
    assert conf.changes(
        {"unchanged": "x", "changed": 5432, "removed": "rmme"},
        {"unchanged": "x", "changed": 5433, "added": "x,y,z"},
    ) == {
        "changed": (5432, 5433),
        "removed": ("rmme", None),
        "added": (None, "x,y,z"),
    }
