Changelog
---------

.. towncrier release notes start

0.35.0 - 2023-05-17
~~~~~~~~~~~~~~~~~~~

Bug fixes
+++++++++

- Implicitly convert ``None`` value to the default value for ``patroni.node``
  and ``patroni.restapi`` fields when using Ansible modules.


0.34.0 - 2023-04-21
~~~~~~~~~~~~~~~~~~~

Features
++++++++

- The ``instance status`` command has been extended to return the status of
  all satellite components. It will exit with code 3 if any service is not
  running.
  The prometheus and temBoard agent statuses have been implemented in addition to
  the existing PostgreSQL status.
- When creating a standby instance, if a pgbackrest backup for target stanza
  exists, it will be used instead of ``pg_basebackup``.
- Upon deletion of an instance, do not prompt for possible deletion of its
  pgbackrest stanza when another instance is using it.
- Upon deletion of an instance, delete its pgbackrest configuration even if
  stanza deletion was not confirmed.
- Remove log, spool and lock paths for pgbackrest upon ``site-configure
  uninstall``.
- Remove, after confirmation, the backup directory for pgbackrest upon
  ``site-configure uninstall``.
- Add a default value for ``pgbackrest.repository.path`` setting with value
  ``$prefix/pgbackrest``.


Bug fixes
+++++++++

- Fix deletion of pgbackrest include directory upon ``site-configure
  uninstall``: the command previously emitted a warning and the directory was
  left empty; now it is correctly removed.


Removals
++++++++

- The ``{version}`` template variable is once again required in
  ``postgresql.datadir`` and ``postgresql.waldir`` settings.
- Option ``--pgbackrest-restore-stanza`` got removed as it is confusing now
  that ``--pgbackrest-stanza`` option is required.


Misc.
+++++

- Set project's development status to *beta*.


0.33.0 - 2023-04-14
~~~~~~~~~~~~~~~~~~~

Features
++++++++

- Attributes CREATEROLE and CREATEDB can now be set when creating or altering
  roles.
- The ``version`` of an extension can now be specified.
- The temBoard logging can be configured via site settings with ``logpath``,
  ``logmethod`` and ``loglevel``.
  By default ``logmethod`` is set to ``stderr``. If ``file`` is selected, a
  logfile for each instance will be created in the ``logpath`` folder named
  ``temboard_agent_{qualname}.log``. ``loglevel`` can be set to ``DEBUG``,
  ``INFO``, ``WARNING``, ``ERROR`` or ``CRITICAL``.
- The option ``--pgbackrest-restore-stanza`` is now taken into account when
  using Patroni.
  Using this option will try to provision new standby from pgbackrest backups
  using `create_replica_methods
  <https://patroni.readthedocs.io/en/latest/replica_bootstrap.html#building-replicas>`_


Bug fixes
+++++++++

- Do not fail upon socket creation error while checking for port availability;
  emit a ``DEBUG`` log message instead in that case.
- Let the user-defined ``port`` take precedence over what's defined in
  postgresql.conf site template.


Removals
++++++++

- Change the ``completion`` command into a ``--completion=SHELL`` option to
  ``pglift``. This is now implemented as an eager callback which does not load
  site settings or any user data and can thus be safely used by any user (e.g.
  ``root``).
- After being marked as required extension schema field is optional again.


0.32.0 - 2023-03-29
~~~~~~~~~~~~~~~~~~~

Features
++++++++

- Add the ``logpath`` setting within PostgreSQL settings section.

  This new field allows to determine the directory containing log for our
  instances.

  The postgresql.conf template distributed with pglift now sets
  ``log_directory`` based on this field, along with a ``log_filename`` value
  that includes the instance qualified name (i.e. ``<version>-<name>``) as a
  prefix.
- Add ``cli.log_format`` and ``cli.date_format`` settings to control the format
  of log messages when writing to a file from the command-line interface.
- Add a ``--defaults/--no-defaults`` options to ``site-settings`` command to
  control whether default settings values should be shown, possibly along with
  site configuration.
- Add support for handling database schemas.
- Allow ``postgresql.datadir`` and ``postgresql.waldir`` settings to not contain
  the ``{version}`` template variable; only the ``{name}`` is required by now.
- Allow to set already encrypted password to a Role using
  ``--encrypted-password`` instead of ``--password``.
- A new rsyslog configuration option has been added to generate rsyslog
  config when running ``pglift site-configure install``.
- Logrotate configuration is now handled at site-configure step and no
  longer when creating/dropping an instance. The logorate configuration
  is now shared among the PostgreSQL instances and satelittes components.
- The required ``ca_cert`` field has been added to the temBoard settings, it's part
  of the ``certificate`` field and must be defined as ``temboard.certificate.ca_cert``.
  This makes the use of ssl more consistent. It's used in the temBoard agent
  configuration file.


Bug fixes
+++++++++

- Fix crash upon early pglift command invocation when the creation of (CLI) log
  directory fails.
- Avoid starting a stopped instance when no role or database changes are needed.
- Do not override environment from parent process in ``instance exec``.
- Fix logrotate configuration file for Patroni, which was missing templating.
- Patroni ``postgresql.pgpass`` configuration item is now configurable with
  ``patroni.passfile`` site setting and defaults to ``etc/patroni/<instance
  qualname>.pgpass``. This passfile is deleted when instance is deleted.
- Fix a validation error when patroni watchdog device setting was not a file but a
  character device.


Removals
++++++++

- Remove possibility to template ``logpath`` setting for Patroni

  We remove the placeholder ``{name}`` from default value for patroni
  ``logpath`` setting. Using the ``{name}`` within the patroni logpath is no
  longer supported, we now always append the instance name at the end of the
  logpath.
- Extension schema field is now required. As a consequence, it's not possible to
  provide a list of extensions to install upon database creation in the CLI.
- Extensions now have a "state" field. To drop an extension from a database
  users now have to explicitly use "state: absent".
- ``log_directory`` for PostgreSQL is no longer created (automatically) by
  pglift.

  We remove the portion of code parsing the postgresql.conf and creating
  the corresponding log_directory. User should make sure the log_directory
  is present when they change this setting on postgresql.conf.
- In pgBackRest settings, ``ca_cert`` is now a part of certificate field.
  ``pgbackrest.repository.ca_cert`` should now be defined as
  ``pgbackrest.repository.certificate.ca_cert``.
- Pglift usage as root user is now prevented.

  According to PostgreSQL documentation, ``initdb`` or ``pg_ctl`` commands cannot
  be run as root.


Documentation
+++++++++++++

- The documentation explaining the steps to configure the site when using systemd
  in system mode has been changed to avoid calling pglift commands with ``sudo``.


Misc.
+++++

- Move command-line specific settings (``lock_file`` and ``logpath``) to a new
  ``cli`` field.


0.31.0 - 2023-02-28
~~~~~~~~~~~~~~~~~~~

Features
++++++++

- A new logrotate service has been added to generate logrotate configuration
  file for each instance.
- The ``passfile`` site setting, under ``postgresql.auth`` section now accepts a
  ``null`` value in order to completely disable support for the password file.
  When disabled, ``--pgpass`` option to ``role`` commands are no longer
  available.
- Validate existence of ``bindir`` fields set in ``postgresql.versions``
  setting.


Bug fixes
+++++++++

- Define the ``cluster_name`` in ``postgresql.conf`` template file, thus
  allowing to create instances without the value (which used to be hard-coded
  from instance name).


Removals
++++++++

- The ``pgpass`` field in ``roles`` items for an ``Instance`` is no longer
  supported (in Ansible or the declarative API). The field can still be
  specified on ``Role`` objects.
- To enable SSL in PostgreSQL configuration file, in addition to setting
  ``ssl`` to ``true``, providing ``ssl_cert_file`` and ``ssl_key_file`` is
  required. The previous self-signed certificate is no longer generated.
- No longer output the ``pgpass`` field when listing roles.


Documentation
+++++++++++++

- The commands for exporting the Ansible doc fragments have been simplified for
  the release workflow. Now it is only a copy of the data files already
  generated for the tests.
- Add a note about the ability for devs to run systemd jobs on sourcehut.
- Document sudo pre-requisites for systemd "system" mode with a sudoers entry example.


0.30.0 - 2023-02-06
~~~~~~~~~~~~~~~~~~~

Features
++++++++

- Make it possible to specify the schema in which a database extension would be installed.

  Until now, when an extension was added to a database, the extension's objects were
  installed by default on the current schema of the database (usually ``public``
  schema).

  Now, the name of the ``schema`` in which to install the extension's objects can be
  specified when adding or altering extensions, by specifying it in the manifest.
- Add a ``-f/--follow`` option to ``instance logs`` command to follow log output
  and log file change.
- Log create/alter/delete operations on database extensions.
- Add support for TLS encryption settings for patroni REST API.
- Log messages from pgBackRest commands: ``pgbackrest`` commands are now invoked
  with ``--log-level-stderr=info`` and respective messages are forwarded to
  pglift's logger at ``DEBUG`` level (as are all ``stderr`` messages from
  subprocesses).
- Configure pgBackRest on standby instances, even in ``repository.path``
  mode, removing a previous limitation from the implementation.

  In addition, when calling ``instance backup <instance>`` with ``<instance>``
  being a standby, ``pgbackrest`` is now invoked with ``--backup-standby``
  option.
- Setup pgbackrest on standby instances when using a remote repository.
- Add support for TLS for Etcd for HA with Patroni via site-settings.
- Make ``host_port`` and ``host_config`` item of pgbackrest's repo-host settings
  optional.
- Separate server from client pgbackrest configuration in remote repository
  mode.
- temboard-agent V8 is now needed for pglift, older versions are no longer supported.


Bug fixes
+++++++++

- Do not write the ``port`` value in ``postgresql.conf`` if it has the default
  value.
- If any change in the configuration files is detected for prometheus or temboard,
  we now perform a restart of the services for the changes to take effect.
- Fix possibly not working ``Exec`` command in postgresql systemd unit file.


Removals
++++++++

- If pgbackrest is enabled, the stanza name must now be provided upon instance
  creation.
- Temboard-agent SSL files are no longer auto-generated, their path must be provided
  in site-settings. The ``certificate`` field containing ``cert`` and ``key`` is
  required in temboard section.
- CLI option ``--extension`` of ``database alter`` command has been removed.
- CLI option ``--in-role`` of ``role alter`` command has been removed.
- Patroni etcd ``host`` setting has been replaced by ``hosts``.
- Configuration for etcd for HA with patroni is now managed in site settings.

  Etcd host can no longer be provided by user when creating an instance.


Documentation
+++++++++++++

- Update the Ansible tutorial to refer to the collection and simplify
  installation steps.
- Warn about the prerequisites for using ``systemctl --user``.
- Document patroni etcd ``hosts`` setting usage
- Document Patroni security (TLS support)
- Recommend to use systemd as a service manager when operating with pgBackRest
  in remote repository mode.


Misc.
+++++

- Add ``--pg1-path`` option to ``pgbackrest archive-push`` command set in
  PostgreSQL ``archive_command``.


0.29.0 - 2022-12-30
~~~~~~~~~~~~~~~~~~~

Features
++++++++

- Improve warning message when failing to connect to primary instance in
  ``instance get``.
- Make `replication` role a member of ``pg_read_all_stats``.
- Add WAL sender state (from `pg_stat_replication
  <https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-REPLICATION-VIEW>`_
  view) to standby information (as available in ``instance get`` command).
- Export paths to PostgreSQL data and WAL directories when getting an Instance
  (e.g. through ``instance get -o json`` command).
- Introduce ``$PGLIFT_CONFIG_PATH`` environment variable.

  This new variable allows users to provide a path to site configuration files
  to be taken into account prior to ``$XDG_CONFIG_HOME/pglift`` or
  ``/etc/pglift``.
- Preserve user edits of Patroni configuration file.
- Add support for pgbackrest remote host repository.


Bug fixes
+++++++++

- Catch JSON decode exception when parsing ``SETTINGS`` environment variable.

  This prevents showing a traceback when the json provided for ``SETTINGS``
  environment variable is invalid.
- Catch :class:`~pglift.exceptions.SettingsError` when loading site settings
  in CLI.

  Prevents displaying a traceback if there's an error when parsing the site
  settings YAML file.
- Fix path to pglift in systemd service when using pre-built binary

  `ExecPath` in ``pglift-postgresql@`` systemd service which was wrongly set
  to an inexistent path.


Removals
++++++++

- Require pgbackrest>=2.41

  ``pglift instance backups`` now runs ``pgbackrest info --set=<backup set>
  --output=json`` which only works since pgbackrest 2.41.
- Hide ``standby.status`` field from ``instance get`` output: this field is
  not very useful since it will only appear on standby instances, which are by
  definition in *demoted* state.
- Change priority order of site config files. Order is now xdg > etc > dist.
- Improve instance privileges command help message
- Drop `archive-push` section in global pgbackrest configuration.
- Replace ``pgbackrest.repopath`` setting by ``pgbackrest.repository``, now an
  object with keys ``path`` and ``retention`` (see ``pglift site-settings
  --schema`` for details). The ``path`` field is now required and has no default
  value, in contrast with ``repopath`` previously.
- The ``site-settings`` command output format is now YAML by default.


Documentation
+++++++++++++

- Add a section in docs for site configuration templates.
- Explain how base pgBackRest configuration is installed, and how to override
  it.
- Improve and clarify documentation about systemd in `system` mode.


Misc.
+++++

- Use pgbackrest's `recovery-option
  <https://pgbackrest.org/configuration.html#section-restore/option-recovery-option>`_
  when restoring a standby from a backup.
- Only restart PostgreSQL upon configuration changes, not all satellite
  services.


0.28.0 - 2022-12-02
~~~~~~~~~~~~~~~~~~~

Features
++++++++

- If pgbackrest is enabled, log install and uninstall operations at
  ``site-configure``.
- Configure systemd timer for instance backup with a randomized delay.
- Add a ``--dry-run`` option to `apply` commands.
- Add support for "force" option for database drop.
- Improve logging when starting/stopping Prometheus `postgres_exporter` and
  `temboard-agent`.
- Allow to pass any command to ``instance exec`` (not just Postgres commands
  or absolute ones as previously).
- Make it possible to operate normal instances even when `patroni` is enabled
  in site settings.
- Add support for PostgreSQL 15.
- Make check for port availability more robust.
- Improve `systemd` unit template for PostgreSQL. It is now defined as a
  ``Type=notify`` service and does not use a ``PIDFile`` anymore, following
  more closely what's suggested in `PostgreSQL documentation
  <https://www.postgresql.org/docs/current/server-start.html>`_.


Bug fixes
+++++++++

- pglift 0.27.0 is now the minimum required version for the Ansible
  collection.
- Fixed error during enabling/disabling temboard service with systemd caused by a
  bad service name.
- Fix error in ``instance env`` command for a standby instance with pgbackrest
  enabled.
- Only start Patroni once at instance creation (avoid a stop and a start).
  This should make concurrent setups (e.g. from Ansible targeting different
  hosts in parallel) work without dead-locking Patroni.
- Avoid starting / stopping PostgreSQL many times at instance creation.


Removals
++++++++

- The Ansible collection got moved to its `own repository
  <https://gitlab.com/dalibo/pglift-ansible>`_.
- Avoid useless ``pgbackrest start`` invocation after stanza creation.
- Separate management of shared_preload_libraries and database extensions.

  The ``extensions`` key in instance's model has been dropped. To install
  extensions in an instance, you now need to provide the
  ``shared_preload_libraries`` in instance settings.
- No longer error out, but simply warn, upon invalid Patroni configuration as
  reported by ``patroni --validate-config``.
- Only validate generated Patroni configuration for Patroni version higher than
  2.1.5.



Documentation
+++++++++++++

- Extend how to about standby management with Ansible to illustrate promote
  operation.
- Add some details about `site configuration` in installation documentation.


Misc.
+++++

- Add a hidden ``--debug`` command-line flag to set log level to ``DEBUG`` and
  eventually get tracebacks displayed.
- Unconditionally call ``pgbackrest stanza-create`` upon instance.
  re-configuration whereas this was previously only done at instance creation.
  Conversely, the ``--no-online`` option is used to avoid superfluous instance
  startup. On the other hand the ``pgbackrest check`` command is still only
  emitted at instance creation.
- Add ``--output=json`` option to ``postgres_exporter apply`` command.
- Rework systemd installation through site-configure hook.
- Use pglift CLI in systemd unit for PostgreSQL.
- Use `towncrier <https://towncrier.readthedocs.io/>`_ to manage news
  fragments.


0.27.0 - 2022-11-02
~~~~~~~~~~~~~~~~~~~

Features
++++++++

- Support for RockyLinux 9
- Ability to provide a name for pgbackrest stanza
- Handling of ``REASSIGN OWNED`` and ``DROP OWNED`` when dropping a role
- Better handling of model validation errors in the CLI
- Ability to create a database as a clone of an existing one
- JSON output to ``instance env`` command
- JSON output to ``apply`` sub-commands
- Prometheus password change upon ``instance alter``
- Prometheus password kept upon instance upgrade
- Raise a specific error if role being dropped has dependent database objects
- Raise a specific error when Postgres binary directory for requested version
  does not exist

Bug fixes
+++++++++

- ``SETTINGS`` environment variable takes precedence over YAML setting file
- Fix systemd service name for Patroni-managed instances
- Fix service name inconsistency for temboard-agent
- Entries of ``postgresql.conf``, set by ``initdb``, no longer commented
- Fix a type error when retrieve instance environment from Ansible module
- Replication password passed through environment when invoking
  ``pg_basebackup``

Removals
++++++++

- Field ``pgbackrest_restore`` excluded from ``instance get`` command output
- Database auto discover in default postgres_exporter configuration
- CLI option ``--json``, replaced by ``--output-format=json``
- Instance model's ``configuration``, renamed as ``settings``, to be
  consistent with eponymous field on Database objects
- Standby's ``for`` field renamed as ``primary_conninfo`` in the declarative
  API

Documentation
+++++++++++++

- Added an example playbook for a standby instance
- Fix settings in Ansible tutorial (``pgpass`` fields missing for ``surole``
  and ``backuprole``)

Misc.
+++++

- Limit database connection openings in ``instance get``
- Installation of global pgbackrest configuration through ``site-configure``
  command
- Setting ``postgresql.versions`` now defined as a list
- Use pglift CLI in Ansible modules, instead of the Python API
- PyOxidizer configuration to build a binary version of pglift
