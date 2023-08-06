Rsyslog site configuration
==========================

rsyslog configuration files are created upon site configuration, through
invocation of the ``site-configure`` command.

This can be enabled through site settings by defining a ``rsyslog`` key,
e.g.:

.. code-block:: yaml
   :name: rsyslog-settings
   :caption: settings.yaml

    rsyslog: {}

.. note::
   Use ``pglift site-settings --schema -o json`` (possibly piped through
   ``jq .definitions.RsyslogSettings``) to retrieve possible settings
   for the ``rsyslog`` section.

The base rsyslog configuration is installed site-wise from a template
(which may be :ref:`overridden <configuration_templates>`).

The default rsyslog configuration template provided by pglift assumes
the ``syslog_ident`` is set to ``postgresql-{version}-{name}`` (on the
postgresql.conf template). With the default template, logs are routed
on the ``programname`` which is equivalent to ``syslog_ident`` value.

This default template file contains:

.. literalinclude:: ../../../src/pglift/postgresql/rsyslog.conf
   :caption: postgresql/rsyslog.conf

And the default PostgreSQL configuration template file used to
automatically adjust the ``syslog_ident`` and the ``log_destination``
looks like this:

.. literalinclude:: ../../../src/pglift/postgresql/postgresql-rsyslog.conf
   :caption: postgresql/postgresql-rsyslog.conf

pglift users can always adapt those values (``syslog_ident`` and rsyslog
routing rule based on ``programname``), but they will have to override
both configuration templates (postgresql and rsyslog).

To use this plugin, it's also required to set the ``log_destination``
to ``syslog``, otherwise PostgreSQL will not send the log to the
syslog server. This configuration item is configured with the correct
value when using the postgresql and rsyslog default templates provided
by pglift.

Running ``rsyslog`` is not handled by pglift, one may ``include`` pglift
rsyslog directory given by ``pglift site-settings -o json | jq
'.rsyslog.configdir`` in the global rsyslog configuration.
