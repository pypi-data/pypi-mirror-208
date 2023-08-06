Setting up the Untis integration
================================

Requirements
------------

To use the importer, you must have a current Untis MultiUser
license (version 2019 and above) and a MySQL database which
is reachable by the AlekSIS server. How to configure Untis
to use this database is described in the `Untis MultiUser Manual`_.

In addition to the technical :ref:`core-install-prerequisites` of
the AlekSIS core itself, a few extra system packages are required:

.. code-block:: shell

   apt install libmariadb-dev

The MySQL (or `MariaDB`_) server must be reachable from the AlekSIS
server, and a user account in the database is needed. It is sufficient
to create this user with ``SELECT`` permissions. On the MySQL shell,
you can create such a user with something like:

.. code-block:: sql

   CREATE USER `aleksis`@`aleksisserver` IDENTIFIED BY 'securepassword';
   GRANT SELECT ON `untis`.* TO `aleksis`@`aleksisserver`;
   FLUSH PRIVILEGES;

.. _Untis MultiUser Manual: https://help.Untis.at/hc/de/article_attachments/360004504079/Untis_MultiUser.pdf

Configure database connection
-----------------------------

In the AlekSIS configuration file (cf. :ref:`core-configuration-files`),
you have to set the following settings:

.. code-block:: toml

   [untis.database]
   enabled = true
   name = "untis"
   user = "aleksis"
   password = "securepassword"
   host = "mysqlserver"
   port = 3306

Preferences
-----------

The preferences for the import can be set from the menu under
`Admin → Configuration → Untis`.

Configure the school ID
~~~~~~~~~~~~~~~~~~~~~~~

The only required preference is the Untis school ID. You need to
provide this in all cases, even if your Untis database hosts only one
school.

.. warning::

   If your Untis database hosts several schools, but you forget to
   configure the school ID, data corruption may occur!

Customise how data are imported
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The behaviour of the import can be customised in several ways. The
following preferences are available:

* **Update values of existing subjects:** This will update the values of
  already existing subjects if Untis has different data.
* **Update short name of existing persons:** This will update the short
  name of already existing persons if Untis has different data.
* **Update name of existing persons:** This will update the name of
  already existing persons if Untis has different data.
* **Update short name of existing groups:** This will update the short name
  of already existing groups if Untis has different data.
* **Update name of existing groups:** This will update the name of already
  existing groups if Untis has different data.
* **Overwrite group owners:** This will update the group owners of already
  existing groups if Untis has different data.
* **Update name of existing rooms:** This will update the name of already
  existing rooms if Untis has different data.
* **Update existing supervision areas:** This will update the values of
  already existing supervision areas if Untis has different data.
* **Use course groups:** This will search course groups (groups
  for each subject in a class) instead of setting the classes as groups.
* **Create non-existing course groups**: In combination with _Use course groups_ being enabled,
  this will create new course groups if no matching group was found.
* **Register a data problem if a course group has been not found:** When this is activated,
  the import will register a data problem if no matching course group was found,
  independent of whether a new course group was created or not.
* **Ignore incomplete substitutions**: If this is activated, Untis won't import any substitutions
  which are not cancelled or without a new room, new teacher or new subject .

Scheduling import tasks
-----------------------

The integration provides different :ref:`core-periodic-tasks` to import the data from Untis:

* ``untis_import_mysql_current_term``: This will import all data from the **current**
  Untis term.
* ``untis_import_mysql_future_terms``: This will import all data from all **future**
  Untis terms, but not from the current.
* ``untis_import_mysql_all_terms``: This will import all data from **all** Untis
  terms which are in the database.
* ``untis_import_mysql_current_next_term``: This will import all data from the
  **current and the directly following** Untis term.
* ``untis_import_mysql_current_future_terms``: This will import all data from the
  **current and all future** Untis terms.

We suggest using ``untis_import_mysql_current_next_term`` as a task because this will
ensure that all current data are up-to-date, but also that the next timetable version
is also already imported when it becomes reelvant.

In general, all tasks will do nothing if there is no matching Untis term.

To use these tasks, you have to add them as periodic tasks. By default, they will
import the most recent plan version from Untis. To select a specific version (i.e.
to import an older snapshot), you can pass the ``version`` argument in the tasks.

How existing data is matched
----------------------------

If there are already existing data in AlekSIS' database, the Untis import will
always try to combine these data. The main data field used for this is the
``short name`` field (cf. :ref:`core-concept-group`). If the data were imported
one time, each object in Chronos will save the respective ID from Untis to make
sure that the data are properly updated at the next import.

The import is thus idempotent.

.. _MariaDB: https://mariadb.org
