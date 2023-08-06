import logging
from pathlib import Path
from unittest import mock

import pytest

from pglift import systemd
from pglift.settings import Settings, SystemdSettings, default_sysuser
from pglift.types import CompletedProcess


@pytest.mark.usefixtures("systemctl")
def test_executeas() -> None:
    s = Settings.parse_obj({"systemd": {"user": True}})
    assert systemd.executeas(s) == ""

    s = Settings.parse_obj(
        {"systemd": {"user": False}, "sysuser": ["postgres", "pgsql"]}
    )
    assert systemd.executeas(s) == "User=postgres\nGroup=pgsql"


def test_systemctl_cmd(systemctl: str) -> None:
    settings = SystemdSettings()
    assert systemd.systemctl_cmd(settings, "status", "-n", "2", unit="foo.service") == [
        systemctl,
        "--user",
        "-n",
        "2",
        "status",
        "foo.service",
    ]

    settings = SystemdSettings(user=False)
    assert systemd.systemctl_cmd(settings, "daemon-reload", unit=None) == [
        systemctl,
        "--system",
        "daemon-reload",
    ]

    settings = SystemdSettings(user=False, sudo=True)
    assert systemd.systemctl_cmd(settings, "start", unit="foo.service") == [
        "sudo",
        systemctl,
        "--system",
        "start",
        "foo.service",
    ]


@pytest.mark.usefixtures("systemctl")
def test_systemctl_env(caplog: pytest.LogCaptureFixture) -> None:
    settings = SystemdSettings(user=False)
    assert systemd.systemctl_env(settings) == {}
    settings = SystemdSettings(user=True)
    systemd.systemctl_env.cache_clear()
    with mock.patch.dict("os.environ", {}, clear=True), mock.patch(
        "pglift.cmd.run",
        side_effect=[
            CompletedProcess(
                [],
                0,
                "/run/user/test\nno\n",
                "",
            ),
            CompletedProcess(
                [],
                0,
                "SOMEVAR=value\nDBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/test/bus\n",
                "",
            ),
        ],
    ) as cmd:
        assert systemd.systemctl_env(settings) == {
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/test/bus",
            "XDG_RUNTIME_DIR": "/run/user/test",
        }

    username, _ = default_sysuser()
    assert cmd.mock_calls == [
        mock.call(
            [
                "loginctl",
                "show-user",
                username,
                "--value",
                "--property",
                "RuntimePath",
                "--property",
                "Linger",
            ],
            check=True,
        ),
        mock.call(
            ["systemctl", "--user", "show-environment"],
            env={"XDG_RUNTIME_DIR": "/run/user/test"},
            check=True,
        ),
    ]
    assert [r.message for r in caplog.records] == [
        f"systemd lingering for user {username} is not enabled, "
        "pglift services won't start automatically at boot"
    ]


def test_install_uninstall(tmp_path: Path) -> None:
    logger = logging.getLogger(__name__)
    systemd.install("foo", "ahah", tmp_path, logger=logger)
    unit_path = tmp_path / "foo"
    mtime = unit_path.stat().st_mtime
    assert unit_path.read_text() == "ahah"
    systemd.install("foo", "ahah", tmp_path, logger=logger)
    assert unit_path.stat().st_mtime == mtime
    with pytest.raises(FileExistsError, match="not overwriting"):
        systemd.install("foo", "ahahah", tmp_path, logger=logger)
    systemd.uninstall("foo", tmp_path, logger=logger)
    assert not unit_path.exists()
    systemd.uninstall("foo", tmp_path, logger=logger)  # no-op
