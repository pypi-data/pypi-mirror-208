
CHANGELOG
=========

0.2.9 (2023-05-16)
------------------

* Replace ``setup.py`` contents with ``setup.cfg``.


0.2.8 (2023-02-12)
------------------

* Refactor ``Query.get()`` => ``Session.get()`` per SQLAlchemy 1.4.


0.2.7 (2023-02-10)
------------------

* Officially drop support for python2.

* Address a warning from SQLAlchemy for ``declarative_base``.


0.2.6 (2022-08-06)
------------------

* Register email profiles provided by this pkg.


0.2.5 (2020-09-22)
------------------

* Remove config for deprecated 'tempmon_critical_temp' email.

* Declare sort order for ``Appliance.probes`` relationship.


0.2.4 (2019-04-23)
------------------

* Make sure we use zero as fallback/default timeout values.


0.2.3 (2019-01-28)
------------------

* Add more template context for email previews.

* Convert ``enabled`` for Client, Probe to use datetime instead of boolean.

* Modify tempmon server logic to take "unfair" time windows into account.


0.2.2 (2018-10-25)
------------------

* Fix bug when sending certain emails while checking probe readings.


0.2.1 (2018-10-24)
------------------

* Make dummy probe use tighter pattern for random readings.

* Add "default" probe timeout logic for server readings check.

* Don't mark client as online unless it's also enabled.

* Add try/catch for client's "read temp" logic.


0.2.0 (2018-10-19)
------------------

* Add per-status timeouts and tracking for probe status.

* Add appliance table, and probe "location" in that context.

* Add image fields for Appliance table.


0.1.19 (2018-10-17)
-------------------

* Add probe URL to email template context.

* Leverage common "now" value when sending emails from server.

* Fix logic bug when checking readings for client.


0.1.18 (2018-10-09)
-------------------

* Log our supposed hostname on client startup.

* Log error on client, when probe takes a 185.0 reading.

* Improve docstrings for some model attributes (for Tailbone).

* Make server more tolerant of database restart.

* Make client more tolerant of database restart.

* Add "status since" to template context for email alerts.

* Add "recent readings" to email template context.


0.1.17 (2018-10-04)
-------------------

* Include client key in disabled probe list email.

* Don't let server mark client as offline until readings fail 3 times in a row.

* Add ``Client.archived`` flag, ignore archived for "disabled probes" check.

* Add notes field to client and probe tables.

* Add ``Client.disk_type`` to track SD card vs. USB.


0.1.16 (2018-02-07)
-------------------

* Send first alert "immediately" if critical temp status.

* Send email alert when tempmon server marks a client as offline.


0.1.15 (2017-11-19)
-------------------

* Add problem report for disabled clients/probes.


0.1.14 (2017-08-08)
-------------------

* Fix alembic script AGAIN


0.1.13 (2017-08-08)
-------------------

* Don't kill tempmon client if DB session.commit() fails

* Grow the ``Reading.degrees_f`` column

* Fix tempmon alembic script per continuum needs


0.1.12 (2017-08-04)
-------------------

* Auto-delete child objects when deleting Client or Probe object


0.1.11 (2017-07-07)
-------------------

* Switch license to GPL v3 (no longer Affero)


0.1.10 (2017-07-06)
-------------------

* Add ``rattail purge-tempmon`` command

* Tweak import placement to fix startup


0.1.9 (2017-06-01)
------------------

* Fix bug when marking client as offline from server loop


0.1.8 (2017-06-01)
------------------

* Refactor main server loop a bit, to add basic retry w/ error logging

* Tweak mail templates a bit, to reference config values


0.1.7 (2017-06-01)
------------------

* Add ``rattail export-hotcooler`` command, for initial hotcooler support

* Add client error logging in case committing session fails..


0.1.6 (2017-02-09)
------------------

* Add configurable delay per client; improve client try/catch


0.1.5 (2016-12-12)
------------------

* Add config for "good temp" email


0.1.4 (2016-12-11)
------------------

* Hopefully fix alert logic when status becomes good


0.1.3 (2016-12-10)
------------------

* Add email config for tempmon-server alerts

* Add mail templates to project manifest


0.1.2 (2016-12-10)
------------------

* Add support for dummy probes (random temp data)

* Add mail templates, plus initial status alert delay for probes


0.1.1 (2016-12-05)
------------------

* Fix import bug in server daemon


0.1.0 (2016-12-05)
------------------

* Initial release.
