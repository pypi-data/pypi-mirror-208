Logrotate site configuration
============================

Logrotate configuration file is created/delete on site configuration,
through invocation of the ``site-configure`` command.

Logrotate plugin can be enabled through site settings by defining a
``logrotate`` key, e.g.:

.. code-block:: yaml
   :name: logrotate-settings
   :caption: settings.yaml

    logrotate: {}

.. note::
   Use ``pglift site-settings --schema -o json`` (possibly piped through ``jq
   .definitions.LogRotateSettings``) to retrieve possible settings for the
   ``logrotate`` section.

The base logrotate configuration is installed site-wise from a template
(which may be :ref:`overridden <configuration_templates>`).

PostgreSQL, pgbackrest and patroni have their own logrotate template.

.. note::
   Use double curly bracket to escape pglift formatting and generate a single
   curly bracket used by logrotate configuration format.

When using logrotate it's avised to set ``log_filename`` to a format that
does not depend on current date, e.g. ``postgresql.log``, otherwise logrotate
will treat logs files separately. It's also recommended to disable the internal
PosgtreSQL log rotation, this can be achieved by setting ``log_rotation_size``
and ``log_rotation_age`` to 0.

Running ``logrotate`` is not handled by pglift, you may ``include`` pglift
logrotate directory given by ``pglift site-settings -o json | jq
'.logrotate.configdir`` in your global logrotate configuration.
