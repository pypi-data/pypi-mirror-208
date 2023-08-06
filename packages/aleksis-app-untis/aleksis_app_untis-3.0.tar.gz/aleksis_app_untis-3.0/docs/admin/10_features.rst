Untis data and their relation to AlekSIS
========================================

Untis is a proprietary timetable management software which is popular
in the German-speaking area, but used internationally. AlekSIS provides
functionality to automatically import data from Untis into data models
of the core and `Chronos`, the timetable and substitution app of AlekSIS.

Currently, we only support importing data from the MySQL database of
`Untis MultiUser`_. This is done through configurable background tasks
which are executed in a specific interval or at specific points in time.

Supported Untis features
------------------------

Not all features of Untis are supported in AlekSIS. The following
information from Untis can be imported into AlekSIS:

* Terms
* Holidays
* Classes, teachers, subjects
* Rooms, supervision areas (corridors in Untis)
* Lesson and break times
* Timetable data (lessons, supervisions)
* Absences, absence reasons
* Substitutions, extra lessons, cancellations
* Events
* Exams

The Untis integration supports the versioning features of Untis. By default,
the most recent version of each object is imported.

Currently, the following features are known not to be supported:

* Students, student groups, student choices
* Prebookings
* Statistical data
* Special rooms (subject and group rooms)

AlekSIS does not support so-called "day texts" from Untis. These are incompatible with AlekSIS' announcement feature, which can be used as a replacement.

.. _Untis MultiUser: https://www.untis.at/produkte/untis-das-grundpaket/multiuser
