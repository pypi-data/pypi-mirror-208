.. _systemd-setup:

Systemd
=======

.. _systemd_install:

Installation
------------

To operate pglift with systemd, set the ``systemd`` setting to a non-``null``
value, e.g.:

.. code-block:: yaml
   :caption: File ~/.config/pglift/settings.yaml

    systemd: {}

Then use the ``site-configure`` command to install systemd unit templates:

.. code-block:: console

    (.venv) $ pglift site-configure install
    INFO     installing systemd template unit for PostgreSQL
    INFO     installed pglift-postgresql@.service systemd unit at
             ~/.local/share/systemd/user/pglift-postgresql@.service
    INFO     installing systemd template unit for Prometheus postgres_exporter
    INFO     installed pglift-postgres_exporter@.service systemd unit at
             ~/.local/share/systemd/user/pglift-postgres_exporter@.service
    INFO     installing systemd template unit and timer for PostgreSQL backups
    INFO     installed pglift-backup@.service systemd unit at
             ~/.local/share/systemd/user/pglift-backup@.service
    INFO     installed pglift-backup@.timer systemd unit at
             ~/.local/share/systemd/user/pglift-backup@.timer

If ``systemd`` is set, we assume that you want to use it for
``service_manager`` and ``scheduler``. To disable it, you have to explicitly
set either setting to ``null``.

.. note::
   Use ``pglift site-configure uninstall`` to uninstall those templates.

How it works
------------

By default, systemd is used in `user` mode, by running ``systemctl --user``
commands. This way, the operator can install systemd units in their home
directory (typically in ``$HOME/.local/share/systemd/user``).

.. warning::
   Running ``systemctl --user`` commands requires a "real" login: i.e. the
   user manager unit `user@UID.service`_ to be active.
   Simply switching users (using, e.g., ``sudo``) is not enough, but an SSH
   connection usually is.
   When in doubt, querying ``loginctl list-sessions`` can help.

.. _`user@UID.service`: https://www.freedesktop.org/software/systemd/man/user@.service.html

Several services are set up at instance creation; these can be listed as
follows for an instance with ``13-main`` identifier:

::

    $ systemctl --user list-units "*13-main*"
      UNIT                                     LOAD   ACTIVE SUB     DESCRIPTION
      pglift-postgres_exporter@13-main.service loaded active running Prometheus exporter for PostgreSQL 13-main database server metrics
      pglift-postgresql@13-main.service        loaded active running PostgreSQL 13-main database server
      pglift-backup@13-main.timer              loaded active waiting Backup 13-main PostgreSQL database instance
    $ systemctl --user list-timers "*13-main*"
    NEXT                         LEFT     LAST                         PASSED       UNIT                            ACTIVATES
    Sat 2021-08-07 00:00:00 CEST 10h left Fri 2021-08-06 12:21:07 CEST 1h 25min ago postgresql-backup@13-main.timer pglift-backup@13-main.service

Overriding
----------

``systemd.service`` and ``systemd.timer`` shipped with pglift may be overridden
using standard methods, as described in `systemd.unit(5)`_.

Here is how to obtain the definition of built-in units (in `user` mode here):

::

    $ systemctl --user list-unit-files pglift-\*
    UNIT FILE                         STATE    VENDOR PRESET
    pglift-backup@.service            static   -
    pglift-postgres_exporter@.service indirect enabled
    pglift-postgresql@.service        indirect enabled
    pglift-backup@.timer              indirect enabled

::

    $ systemctl --user cat pglift-postgresql@.service
    [Unit]
    Description=PostgreSQL %i database server
    After=network.target

    [Service]
    Type=forking


    # Disable OOM kill on the postmaster
    OOMScoreAdjust=-1000
    Environment=PG_OOM_ADJUST_FILE=/proc/self/oom_score_adj
    Environment=PG_OOM_ADJUST_VALUE=0


    ExecStart=/home/denis/src/dalibo/pglift/.venv/bin/python3 -m pglift.postgres %i
    ExecReload=/bin/kill -HUP $MAINPID

    PIDFile=/home/denis/.local/share/pglift/run/postgresql/postgresql-%i.pid

    [Install]
    WantedBy=multi-user.target


.. _`systemd.unit(5)`: https://www.freedesktop.org/software/systemd/man/systemd.unit.html

`system` mode
-------------

Operating pglift with systemd in system mode (i.e. through ``systemctl
--system`` commands) is possible with a few configuration and installation
steps.

First assume we're working in the ``/srv/pglift`` prefix directory, where all
instances data and configuration would live, and set ownership to the current
user:

.. code-block:: console

    $ sudo mkdir /srv/pglift
    $ sudo chown -R $(whoami): /srv/pglift

A typical site settings file would contain:

.. code-block:: yaml
   :caption: File /etc/pglift/settings.yaml

    systemd:
      unit_path: /etc/systemd/system
      user: false
      sudo: true
    sysuser: [postgres, postgres]
    prefix: /srv/pglift

- ``systemd`` is configured to have its unit files in ``/etc/systemd/system``,
- the ``systemd.user`` setting is unset (meaning ``--system`` option will be
  passed to ``systemctl``),
- the ``systemd.sudo`` setting can optionally be set in order to invoke
  ``systemctl`` command with ``sudo``,
- a ``sysuser`` (user name, group name) is set to define the system user
  operating PostgreSQL (typically ``whoami``),
- the global ``prefix`` is set to previously created directory.

.. note::
   Check that the overall settings correspond to what's expected by running:
   ``pglift site-settings``.

Next the site needs to be configured.

.. note::
    This may be done at package installation step, if installed from a
    distribution package.

The following command will create systemd service and/or timer files:

.. code-block:: console
   :name: systemd-system-site-configure-install

    $ env SYSTEMD='{"unit_path": "/srv/pglift/systemd"}' pglift site-configure install
    INFO     installing systemd template unit for PostgreSQL
    INFO     installed pglift-postgresql@.service systemd unit at
             /srv/pglift/pglift-postgresql@.service

By temporarily changing the ``unit_path`` setting, we ensure that the user
has the sufficient permissions to write the unit files.

Then these systemd files need to be moved to the actual unit files path:

.. code-block:: console

    $ sudo mv /srv/pglift/systemd/* /etc/systemd/system

Also, in order to operate pglift with such settings, the user needs
permissions to invoke the ``sudo systemctl`` command without being asked to
provide a password. All systemd units managed by pglift are named with a
``pglift-`` prefix (e.g. ``pglift-postgresql@15-main.service``). Accordingly,
the site administrator should add a sudoers entry allowing such commands,
taking care to use the absolute path to ``systemctl``.

Finally, operations are performed as usual but using configured ``sysuser``,
e.g.:

.. code-block:: console

    $ pglift instance create --port=5455 main
    INFO     initializing PostgreSQL instance
    INFO     configuring PostgreSQL authentication
    INFO     configuring PostgreSQL instance
    INFO     creating role 'replication' on instance 15/main
    $ pglift instance list
    ┏━━━━━━┳━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
    ┃ name ┃ version ┃ port ┃ datadir                            ┃ status  ┃
    ┡━━━━━━╇━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
    │ main │ 15      │ 5455 │ /srv/pglift/srv/pgsql/15/main/data │ running │
    └──────┴─────────┴──────┴────────────────────────────────────┴─────────┘
    $ sudo systemctl status --system pglift-\*
    ● pglift-postgresql@15-main.service - PostgreSQL 15-main database server
         Loaded: loaded (/etc/systemd/system/pglift-postgresql@.service; enabled; vendor preset: enabled)
         Active: active (running) since Fri 2022-12-16 14:16:31 CET; 14s ago
       Main PID: 83348 (postgres)
          Tasks: 7 (limit: 6871)
         Memory: 48.3M
            CPU: 444ms
         CGroup: /system.slice/system-pglift\x2dpostgresql.slice/pglift-postgresql@15-main.service
                 ├─83348 /usr/lib/postgresql/15/bin/postgres -D /srv/pglift/srv/pgsql/15/main/data
                 ├─83349 postgres: main: logger
                 ├─83350 postgres: main: checkpointer
                 ├─83351 postgres: main: background writer
                 ├─83353 postgres: main: walwriter
                 ├─83354 postgres: main: autovacuum launcher
                 └─83355 postgres: main: logical replication launcher

Uninstallation follows the same logic as the :ref:`installation
<systemd-system-site-configure-install>`:

.. code-block:: console

    $ sudo pglift site-configure uninstall
    INFO     uninstalling systemd template unit for PostgreSQL
    INFO     removing pglift-postgresql@.service systemd unit
             (/etc/systemd/system/pglift-postgresql@.service)
