from pglift import logrotate
from pglift.pm import PluginManager
from pglift.settings import Settings


def test_site_configure(settings: Settings, pm: PluginManager) -> None:
    logrotate_settings = settings.logrotate
    assert logrotate_settings is not None
    assert not logrotate_settings.configdir.exists()
    logrotate.site_configure_install(settings, pm)
    assert logrotate_settings.configdir.exists()
    config = logrotate_settings.configdir / "logrotate.conf"
    assert config.exists()
    assert settings.pgbackrest is not None
    assert settings.patroni is not None
    assert config.read_text() == "\n".join(
        [
            f"{settings.patroni.logpath}/*/patroni.log {{",
            "  weekly",
            "  rotate 10",
            "  copytruncate",
            "  delaycompress",
            "  compress",
            "  notifempty",
            "  missingok",
            "}",
            "",
            f"{settings.pgbackrest.logpath}/*.log {{",
            "  weekly",
            "  rotate 10",
            "  copytruncate",
            "  delaycompress",
            "  compress",
            "  notifempty",
            "  missingok",
            "}",
            "",
            f"{settings.postgresql.logpath}/*.log {{",
            "  weekly",
            "  rotate 10",
            "  copytruncate",
            "  delaycompress",
            "  compress",
            "  notifempty",
            "  missingok",
            "}",
            "",
        ]
    )
    logrotate.site_configure_uninstall(settings)
    assert not logrotate_settings.configdir.exists()
