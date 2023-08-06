from pglift import rsyslog
from pglift.pm import PluginManager
from pglift.settings import Settings


def test_site_configure(settings: Settings, pm: PluginManager) -> None:
    rsyslog_settings = settings.rsyslog
    assert rsyslog_settings is not None
    rsyslog_config_file = rsyslog_settings.configdir / "rsyslog.conf"
    assert not rsyslog_config_file.exists()

    rsyslog.site_configure_install(settings, pm)
    assert rsyslog_settings.configdir.exists()
    assert rsyslog_config_file.exists()

    username, group = settings.sysuser
    assert rsyslog_config_file.read_text().strip() == "\n".join(
        [
            "$umask 0027",
            "$FileCreateMode 0640",
            f"$FileOwner {username}",
            f"$FileGroup {group}",
            f'template (name="pglift_postgresql_template" type="string" string="{settings.postgresql.logpath}/%PROGRAMNAME%.log")',
            'if (re_match($programname, "postgresql-.*")) then -?pglift_postgresql_template',
            "&stop",
        ]
    )

    rsyslog.site_configure_uninstall(settings=settings)
    assert not rsyslog_config_file.exists()
