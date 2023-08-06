Standby setup
=============

.. highlight:: console

Command-line interface
----------------------

From the command-line interface, creating a standby instance is done through
the ``instance create`` command:

::

    $ pglift instance create standby --standby-for <primary dsn> --standby-password
    Password for the replication user:
    Repeat for confirmation:


The ``--standby-for`` option should be a `connection string`_ to the primary
server (e.g. ``host=primary port=5433``).
If the primary is also a pglift instance, you must use the dedicated
``replication`` user, set ``user=replication`` in the dsn.

pglift will call `pg_basebackup`_ utility to create a standby. A replication
slot can be specified with ``--standby-slot <slot name>``.

.. note::
   If the primary instance has a password set for the super-user role, and is
   needed for local authentication through the password file in particular, it
   might be useful to provide the same password through ``--surole-password``
   option when creating the standby.

.. note::
   If Prometheus postgres_exporter was set up on the primary instance and is
   wanted on the standby, don't forget to provide ``--prometheus-password``
   option to the above command with the same password as on the primary
   instance.

Promoting a standby instance:

::

    $ pglift instance promote standby

.. _`connection string`: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
.. _pg_basebackup: https://www.postgresql.org/docs/current/app-pgbasebackup.html

Ansible
-------

Standby instance management is also possible from the Ansible interface.
Please refer to the :ref:`tutorial <tutorial_ansible>` for starting up with
this.

The ``dalibo.pglift.instance`` module exposes a ``standby`` field to define
connection to the primary, password and replication slot.

First, we will define a password for the replication user on the ``control``
node and store that in Ansible vault:

::

    user@control:~$ cat << EOF | ansible-vault encrypt > pglift-vars
    replication_role_password: $(openssl rand -base64 9)
    EOF

The following playbook will create 2 instances on the same host:

- ``pg1`` as a primary, port ``5432``
- ``pg2`` as a standby, port ``5433``

.. literalinclude:: ../ansible/standby-setup.yml
    :language: yaml
    :caption: standby-setup.yml

And finally, run the playbook:
::

    user@control:~$ ansible-playbook --extra-vars @pglift-vars --ask-vault-password standby-setup.yml
    Vault password:

    PLAY [standby setup] ***********************************************************************************************************************

    TASK [Gathering Facts] *********************************************************************************************************************
    ok: [localhost]

    TASK [primary instance 14/main] ************************************************************************************************************
    changed: [localhost]

    TASK [replica instance 14/main] ************************************************************************************************************
    changed: [localhost]

    PLAY RECAP *********************************************************************************************************************************
    localhost                  : ok=3    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

We can find our instances running on ``managed`` node :
::

    user@managed:~$ pglift instance list
    ┏━━━━━━┳━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
    ┃ name ┃ version ┃ port ┃ datadir                ┃ status  ┃
    ┡━━━━━━╇━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
    │ pg1  │ 14      │ 5432 │ /srv/pgsql/14/pg1/data │ running │
    │ pg2  │ 14      │ 5433 │ /srv/pgsql/14/pg2/data │ running │
    └──────┴─────────┴──────┴────────────────────────┴─────────┘

The following playbook will promote ``pg2`` and rebuild ``pg1`` as a
standby:

.. literalinclude:: ../ansible/standby-promote.yml
    :language: yaml
    :caption: standby-promote.yml

Run the playbook:
::

    user@control:~$ ansible-playbook --extra-vars @pglift-vars --ask-vault-password standby-promote.yml
    Vault password:

    PLAY [promote standby] **************************************************************************************************

    TASK [Gathering Facts] **************************************************************************************************
    ok: [localhost]

    TASK [promote standby instance 14/pg2] **********************************************************************************
    ok: [localhost]

    TASK [delete 14/pg1 instance] *******************************************************************************************
    changed: [localhost]

    TASK [rebuild 14/pg1 instance as a standby] *****************************************************************************
    changed: [localhost]

    PLAY RECAP **************************************************************************************************************
    localhost                  : ok=5    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0



Finally we can see ``pg1`` as a standby and both running :
::

    user@managed:~$ pglift instance get pg1
     name  version  port  data_checksums  locale  encoding  extensions  pending_restart  standby
     pg1   14       5432  False           C       UTF8                  False            primary_conninfo: user=replication
                                                                                         channel_binding=prefer
                                                                                         host=127.0.0.1 port=5433
                                                                                         sslmode=prefer sslcompression=0
                                                                                         sslsni=1
                                                                                         ssl_min_protocol_version=TLSv1.2
                                                                                         gssencmode=prefer
                                                                                         krbsrvname=postgres
                                                                                         target_session_attrs=any
                                                                                         status: demoted
                                                                                         slot:
                                                                                         replication_lag: 0

    user@managed:~$ pglift instance list
    ┏━━━━━━┳━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
    ┃ name ┃ version ┃ port ┃ datadir                ┃ status  ┃
    ┡━━━━━━╇━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
    │ pg1  │ 14      │ 5432 │ /srv/pgsql/14/pg1/data │ running │
    │ pg2  │ 14      │ 5433 │ /srv/pgsql/14/pg2/data │ running │
    └──────┴─────────┴──────┴────────────────────────┴─────────┘
