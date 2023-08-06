High availability
=================

PostgreSQL high availability is achieved by using the `patroni` plugin of
pglift. Refer to :doc:`/user/setup/patroni` section for setup.

The ``instance create`` command gains a number of new options to control
Patroni integration:

.. code-block:: console

    $ pglift instance create --help
    Usage: pglift instance create [OPTIONS] NAME

      Initialize a PostgreSQL instance

    Options:
    [...]
      --patroni-cluster CLUSTER       Name (scope) of the Patroni cluster.
      --patroni-node NODE             Name of the node (usually the host name).
      --patroni-restapi-connect-address CONNECT_ADDRESS
                                      IP address (or hostname) and port, to access
                                      the Patroni's REST API.
      --patroni-restapi-listen LISTEN
                                      IP address (or hostname) and port that
                                      Patroni will listen to for the REST API.
      --patroni-postgresql-connect-host POSTGRESQL_CONNECT_HOST
                                      Host or IP address through which PostgreSQL
                                      is externally accessible.

At least the "patroni cluster" option is required to create an instance
managed by Patroni. Other options have default values corresponding to
Patroni's defaults.

Assuming an *open* etcd server is available at ``127.0.0.1:2379``, the
following command will create an instance with Patroni enabled:

.. code-block:: console

    $ pglift instance create pg1 --patroni-cluster=pgdemo --patroni-node=pg1
    INFO     initializing PostgreSQL instance
    INFO     setting up Patroni service
    INFO     bootstrapping PostgreSQL with Patroni
    INFO     instance 14/pg1 successfully created by Patroni
    INFO     stopping Patroni 14-pg1
    INFO     waiting for Patroni REST API to stop
    INFO     configuring PostgreSQL instance
    INFO     setting up Patroni service
    INFO     starting PostgreSQL
    INFO     altering role 'replication' on instance 14/pg1
    INFO     creating role 'powa' on instance 14/pg1
    INFO     creating 'powa' database on instance 14/pg1
    INFO     stopping PostgreSQL
    INFO     starting instance 14/pg1
    INFO     starting Patroni 14-pg1

We can then inspect the instance:

.. code-block:: console

    $ pglift instance get pg1 -o json
    {
      "name": "pg1",
      "version": "14",
      "port": 5432,
      "settings": {
        "hba_file": "/srv/pgsql/14/pg1/data/pg_hba.conf",
        "ident_file": "/srv/pgsql/14/pg1/data/pg_ident.conf",
        "listen_addresses": "*",
        "max_connections": 100,
        "unix_socket_directories": "/run/user/1000/pglift/postgresql",
        "shared_buffers": "1 GB",
        "max_prepared_transactions": 0,
        "max_worker_processes": 8,
        "wal_level": "replica",
        "wal_log_hints": true,
        "recovery_target": "",
        "recovery_target_name": "",
        "recovery_target_time": "",
        "recovery_target_xid": "",
        "recovery_target_lsn": "",
        "recovery_target_timeline": "latest",
        "max_wal_senders": 10,
        "max_replication_slots": 10,
        "wal_keep_size": "128MB",
        "track_commit_timestamp": false,
        "hot_standby": true,
        "effective_cache_size": "4 GB",
        "log_destination": "stderr",
        "logging_collector": "True",
        "cluster_name": "pgdemo",
        "lc_messages": "C",
        "lc_monetary": "C",
        "lc_numeric": "C",
        "lc_time": "C",
        "shared_preload_libraries": "pg_qualstats, pg_stat_statements, pg_stat_kcache",
        "max_locks_per_transaction": 64
      },
      "data_checksums": false,
      "locale": "C",
      "encoding": "UTF8",
      "state": "started",
      "pending_restart": false,
      "powa": {},
      "patroni": {
        "cluster": "pgdemo",
        "node": "pg1",
        "restapi": {
          "connect_address": "pghost:8008",
          "listen": "pghost:8008"
        },
        "postgresql_connect_host": "pghost",
        "cluster_members": [
          {
            "host": "pghost",
            "name": "pg1",
            "port": 5432,
            "role": "leader",
            "state": "running",
            "api_url": "http://pghost:8008/patroni",
            "timeline": 2
          }
        ]
      }
    }

We can see, in particular, that many fields in ``settings`` have been set
by Patroni. The ``cluster_members`` entry lists members of the Patroni this
instance is member of (only itself, currently).

The instance can be stopped/started/restarted as normal. Notice ``start
--foreground`` that can be used to monitor Patroni state in real-time.

We can create a second node in our ``pgdemo`` cluster (on the same host here):

.. code-block:: console

    $ pglift -Ldebug instance create pg2 --port=5444 --patroni-cluster=pgdemo \
        --patroni-node=pg2 \
        --patroni-restapi-connect-address=127.0.1.1:8009 \
        --patroni-restapi-listen=127.0.1.1:8009
    INFO     initializing PostgreSQL instance
    INFO     setting up Patroni service
    DEBUG    /usr/bin/patroni --validate-config
             /tmp/tmptb5vfdtp.yaml
    INFO     bootstrapping PostgreSQL with Patroni
    DEBUG    starting program '/usr/bin/patroni
             /etc/patroni/14-pg2.yaml'
    DEBUG    /usr/bin/patroni: 2022-09-01 16:57:17,163
             INFO: Selected new etcd server http://localhost:2379
    DEBUG    /usr/bin/patroni: 2022-09-01 16:57:17,174
             INFO: No PostgreSQL configuration items changed, nothing to reload.
    DEBUG    /usr/bin/patroni: 2022-09-01 16:57:17,179
             INFO: Lock owner: pg1; I am pg2
    DEBUG    /usr/bin/patroni: 2022-09-01 16:57:17,181
             INFO: trying to bootstrap from leader 'pg1'
    DEBUG    /usr/bin/patroni: 2022-09-01 16:57:17,548
             INFO: replica has been created using basebackup
    DEBUG    /usr/bin/patroni: 2022-09-01 16:57:17,550
             INFO: bootstrapped from leader 'pg1'
    DEBUG    /usr/bin/patroni: 2022-09-01 16:57:17,716
             INFO: postmaster pid=54984
    DEBUG    /usr/bin/patroni: 2022-09-01 14:57:17.722 GMT
             [54984] LOG:  Auto detecting pg_stat_kcache.linux_hz parameter...
    DEBUG    /usr/bin/patroni: 2022-09-01 14:57:17.722 GMT
             [54984] LOG:  pg_stat_kcache.linux_hz is set to 1000000
    DEBUG    /usr/bin/patroni: 2022-09-01 14:57:17.762 GMT
             [54984] LOG:  redirecting log output to logging collector process
    DEBUG    /usr/bin/patroni: 2022-09-01 14:57:17.762 GMT
             [54984] HINT:  Future log output will appear in directory "log".
    DEBUG    /usr/bin/patroni: 2022-09-01 16:57:18,765
             INFO: Lock owner: pg1; I am pg2
    DEBUG    /usr/bin/patroni: 2022-09-01 16:57:18,766
             INFO: establishing a new patroni connection to the postgres cluster
    DEBUG    /usr/bin/patroni: 2022-09-01 16:57:18,787
             INFO: no action. I am (pg2), a secondary, and following a leader (pg1)
    DEBUG    /usr/bin/patroni: 2022-09-01 16:57:18,903
             INFO: no action. I am (pg2), a secondary, and following a leader (pg1)
    DEBUG    checking status of REST API for Patroni 14-pg2 at 127.0.1.1:8009
    DEBUG    checking if PostgreSQL instance 14/pg2 is ready
    DEBUG    /usr/lib/postgresql/14/bin/pg_isready -d 'user=postgres port=5444
             host=/run/user/1000/pglift/postgresql'
    INFO     instance 14/pg2 successfully created by Patroni
    INFO     stopping Patroni 14-pg2
    DEBUG    terminating process 54969
    INFO     waiting for Patroni REST API to stop
    DEBUG    Retrying pglift.patroni.impl.wait_api_down in 1.0 seconds as it raised Error:
             Patroni REST API still running.
    DEBUG    commenting PostgreSQL configuration entries in
             /srv/pgsql/14/pg2/data/postgresql.base.conf:
    INFO     configuring PostgreSQL instance
    INFO     setting up Patroni service
    DEBUG    get status of PostgreSQL instance 14/pg2
    DEBUG    /usr/lib/postgresql/14/bin/pg_ctl --version
    DEBUG    /usr/lib/postgresql/14/bin/pg_ctl status -D
             /srv/pgsql/14/pg2/data
    INFO     starting instance 14/pg2
    INFO     starting Patroni 14-pg2
    DEBUG    starting program '/usr/bin/patroni
             /etc/patroni/14-pg2.yaml'
    DEBUG    /usr/bin/patroni: 2022-09-01 14:57:23.569 GMT
             [55032] LOG:  Auto detecting pg_stat_kcache.linux_hz parameter...
    DEBUG    /usr/bin/patroni: 2022-09-01 14:57:23.570 GMT
             [55032] LOG:  pg_stat_kcache.linux_hz is set to 1000000
    DEBUG    /usr/bin/patroni: 2022-09-01 14:57:23.600 GMT
             [55032] LOG:  redirecting log output to logging collector process
    DEBUG    /usr/bin/patroni: 2022-09-01 14:57:23.600 GMT
             [55032] HINT:  Future log output will appear in directory "log".
    DEBUG    checking status of REST API for Patroni 14-pg2 at 127.0.1.1:8009

And get pg1's description again:

.. code-block:: console

    $ pglift instance get pg1 -o json
    {
      "name": "pg1",
      "version": "14",
      "port": 5432,
      "settings": {
        "hba_file": "/srv/pgsql/14/pg1/data/pg_hba.conf",
        "ident_file": "/srv/pgsql/14/pg1/data/pg_ident.conf",
        "listen_addresses": "*",
        "max_connections": 100,
        "unix_socket_directories": "/run/user/1000/pglift/postgresql",
        "shared_buffers": "1 GB",
        "max_prepared_transactions": 0,
        "max_worker_processes": 8,
        "wal_level": "replica",
        "wal_log_hints": true,
        "recovery_target": "",
        "recovery_target_name": "",
        "recovery_target_time": "",
        "recovery_target_xid": "",
        "recovery_target_lsn": "",
        "recovery_target_timeline": "latest",
        "max_wal_senders": 10,
        "max_replication_slots": 10,
        "wal_keep_size": "128MB",
        "track_commit_timestamp": false,
        "hot_standby": true,
        "effective_cache_size": "4 GB",
        "log_destination": "stderr",
        "logging_collector": "True",
        "cluster_name": "pgdemo",
        "lc_messages": "C",
        "lc_monetary": "C",
        "lc_numeric": "C",
        "lc_time": "C",
        "shared_preload_libraries": "pg_qualstats, pg_stat_statements, pg_stat_kcache",
        "max_locks_per_transaction": 64
      },
      "data_checksums": false,
      "locale": "C",
      "encoding": "UTF8",
      "state": "started",
      "pending_restart": false,
      "patroni": {
        "cluster": "pgdemo",
        "node": "pg1",
        "restapi": {
          "connect_address": "pghost:8008",
          "listen": "pghost:8008"
        },
        "postgresql_connect_host": "pghost",
        "cluster_members": [
          {
            "host": "pghost",
            "name": "pg1",
            "port": 5432,
            "role": "leader",
            "state": "running",
            "api_url": "http://pghost:8008/patroni",
            "timeline": 4
          },
          {
            "host": "pghost",
            "name": "pg2",
            "port": 5444,
            "role": "replica",
            "state": "running",
            "lag": 0,
            "timeline": 4,
            "api_url": "http://127.0.1.1:8009/patroni"
          }
        ]
      },
      "powa": {}
    }

where it appears that ``pg2`` is a replica for ``pg1`` (same host,
``port=5432``).

Configuration
-------------

When ``patroni`` managed instances, it also manages PostgreSQL configuration.
This is defined as *local configuration* in Patroni YAML configuration file
that pglift generates at instance creation (section
``postgresql.parameters``). The *dynamic configuration* is **not** used.

PostgreSQL configuration can be managed in usual ways provided by pglift, such
as the :ref:`pglift pgconf <pgconf>` commands.

.. code-block:: console

    $ pglift pgconf -i pg1 edit
    [ ... editing to change effective_cache_size and logging_collector ...]
    INFO     configuring PostgreSQL instance
    INFO     setting up Patroni service
    INFO     reloading Patroni 14-pg1
    INFO     instance 14/pg1 needs reload due to parameter changes: effective_cache_size
    INFO     reloading Patroni 14-pg1
    WARNING  instance 14/pg1 needs restart due to parameter changes: logging_collector
    > PostgreSQL needs to be restarted; restart now? [y/n] (n): y
    INFO     restarting Patroni 14-pg1
    $ pglift instance exec pg1 -- postgres -C logging_collector
    off

.. warning::
   :ref:`pglift pgconf <pgconf>` commands other than ``edit`` should be
   avoided as they do not work correctly at the moment.


Logs
----

Logs for the Patroni process driving an instance are available through the
``patroni logs`` command-line entry point:

.. code-block:: console

    $ pglift patroni -i pg2 logs
    [...]
    2022-09-01 17:04:08,901 INFO: no action. I am (pg2), a secondary, and following a leader (pg1)
    [...]

PostgreSQL logs are accessible normally:

.. code-block:: console

    $ pglift instance logs pg2
    INFO     reading logs of instance '14/pg2' from
         /srv/pgsql/14/pg2/data/log/postgresql-2022-09-01_145723.log
    2022-09-01 14:57:23.600 GMT [55032] LOG:  starting PostgreSQL 14.5 (Debian 14.5-1.pgdg110+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 10.2.1-6) 10.2.1 20210110, 64-bit
    2022-09-01 14:57:23.600 GMT [55032] LOG:  listening on IPv4 address "0.0.0.0", port 5444
    2022-09-01 14:57:23.600 GMT [55032] LOG:  listening on IPv6 address "::", port 5444
    2022-09-01 14:57:23.601 GMT [55032] LOG:  listening on Unix socket "/run/user/1000/pglift/postgresql/.s.PGSQL.5444"
    2022-09-01 14:57:23.605 GMT [55035] LOG:  database system was shut down in recovery at 2022-09-01 14:57:22 GMT
    2022-09-01 14:57:23.605 GMT [55035] LOG:  entering standby mode
    2022-09-01 14:57:23.608 GMT [55035] LOG:  redo starts at 0/2000028
    2022-09-01 14:57:23.608 GMT [55035] LOG:  consistent recovery state reached at 0/3000000
    2022-09-01 14:57:23.609 GMT [55032] LOG:  database system is ready to accept read-only connections
    2022-09-01 14:57:23.616 GMT [55039] LOG:  started streaming WAL from primary at 0/3000000 on timeline 4
    2022-09-01 15:22:59.787 GMT [55039] LOG:  replication terminated by primary server
    2022-09-01 15:22:59.787 GMT [55039] DETAIL:  End of WAL reached on timeline 4 at 0/3000270.
    2022-09-01 15:22:59.787 GMT [55039] FATAL:  could not send end-of-streaming message to primary: server closed the connection unexpectedly
            This probably means the server terminated abnormally
            before or while processing the request.
        no COPY in progress
    2022-09-01 15:22:59.787 GMT [55035] LOG:  invalid record length at 0/3000270: wanted 24, got 0
    2022-09-01 15:22:59.801 GMT [56995] FATAL:  could not connect to the primary server: connection to server at "gong" (127.0.1.1), port 5432 failed: server closed the connection unexpectedly
            This probably means the server terminated abnormally
            before or while processing the request.
    2022-09-01 15:23:04.799 GMT [57027] LOG:  started streaming WAL from primary at 0/3000000 on timeline 4


Operations
----------

``start``, ``stop``, ``restart`` and ``reload`` operations are supported. The
``restart`` and ``reload`` operations are delegated to Patroni (through
requests to the REST API), which might as such be effective asynchronously.

The ``promote`` operation is not supported and change to the cluster topology
should be managed directly through Patroni commands or REST API.

Environment and ``patronictl``
------------------------------

Command ``instance env`` exposes some Patroni variables:

.. code-block:: console

    $ pglift instance env pg2
    PATRONICTL_CONFIG_FILE=/etc/patroni/14-pg2.yaml
    PATRONI_NAME=pg2
    PATRONI_SCOPE=pgdemo

It is then easy to handle over ``patronictl``, e.g.:

.. code-block:: console

    $ pglift instance exec pg2 -- $(which patronictl) topology
    +--------+-------------+---------+---------+----+-----------+
    | Member | Host        | Role    | State   | TL | Lag in MB |
    + Cluster: pgdemo (7138424622880019582) ---+----+-----------+
    | pg1    | pghost:5432 | Leader  | running |  4 |           |
    | + pg2  | pghost:5444 | Replica | running |  4 |         0 |
    +--------+-------------+---------+---------+----+-----------+

Cluster removal
---------------

Upon drop of the instance being the last node of a Patroni cluster, it might
be desirable to also remove the cluster (i.e. clean-up the DCS from respective
data). This is usually done with ``patronictl remove <clustername>``.
Yet, as there is no dedicated endpoint in Patroni's REST API, this is not
handled by pglift. When this happens, pglift will instead back up the
configuration file of the last node and warn about it:

.. code-block:: console

    $ pglift instance drop pg1
    INFO     dropping PostgreSQL instance
    > Confirm complete deletion of instance 14/pg1? [y/n] (y): y
    INFO     stopping instance 14/pg1
    WARNING  'pg1' appears to be the last member of cluster 'pgdemo', saving Patroni
             configuration file to /etc/patroni/pgdemo-pg1-1663664101.3698814.yaml
    INFO     stopping Patroni 14-pg1
    INFO     waiting for Patroni REST API to stop
    INFO     deleting PostgreSQL cluster

It is then straightforward to delete the cluster:

.. code-block:: console

    $ patronictl --config-file /etc/patroni/pgdemo-pg1-1663664101.3698814.yaml remove pgdemo
    ('GET MEMBERS', 'http://127.0.0.1:2379/v2/machines', {'headers': {'user-agent': 'Patroni/2.1.4 Python/3.9.2 Linux'}, 'redirect': True, 'preload_content': False, 'timeout': Timeout(connect=1.6666666666666667, read=<object object at 0x7fdf09fd3080>, total=3.3333333333333335), 'retries': 2})
    +--------+--------+---------+---------+----+-----------+
    | Member | Host   | Role    | State   | TL | Lag in MB |
    + Cluster: pgdemo (7145378431101334004) ---+-----------+
    | pg1    | pghost | Replica | stopped |    |   unknown |
    +--------+--------+---------+---------+----+-----------+
    Please confirm the cluster name to remove: pgdemo
    You are about to remove all information in DCS for pgdemo, please type: "Yes I am aware": Yes I am aware
    $ rm /etc/patroni/pgdemo-pg1-1663664101.3698814.yaml

.. _`Patroni configuration documentation`: https://patroni.readthedocs.io/en/latest/SETTINGS.html#etcd
