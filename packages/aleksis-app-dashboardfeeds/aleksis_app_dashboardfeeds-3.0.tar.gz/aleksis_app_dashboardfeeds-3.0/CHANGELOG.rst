Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.

`3.0`_ - 2023-05-14
-------------------

Nothing changed.

`3.0b0`_ - 2023-02-22
--------------------

This version requires AlekSIS-Core 3.0. It is incompatible with any previous
version.

`2.1`_ - 2022-06-23
-------------------

Added
~~~~~

* Add Ukrainian locale (contributed by Sergiy Gorichenko from Fre(i)e Software GmbH).

Changed
~~~~~~~

* The `base_url` of iCal and RSS widgets is now optional

`2.0.1`_ - 2022-01-21
---------------------

Changed
~~~~~~~

* ``get_feeds`` task is now automatically scheduled every 10 minutes

Fixed
~~~~~

* Add admin docs.

`2.0`_ - 2021-10-30
-------------------

Changed
~~~~~~~

* German translations were updated.

`2.0rc1`_ - 2021-06-23
----------------------

Changed
~~~~~~~

* Increase cache time for events to one hour.

Fixed
~~~~~

* Don't delete cache if there was an error while receiving the events.

`2.0b0`_ - 2021-05-21
---------------------

Changed
~~~~~~~

* RSS sources now get automatically deleted if their respective widget gets deleted.

Fixed
~~~~~

* All-day events were displayed one day too long.
* Invalid iCal data broke the iCal widget.

`2.0a2`_ - 2020-05-04
---------------------

Added
~~~~~

* Allow adding iCal widgets to dashboard
* Allow adding RSS widgets to dashboard

----------


.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html


.. _2.0a2: https://edugit.org/AlekSIS/Official/AlekSIS-App-DashboardFeeds/-/tags/2.0a2
.. _2.0b0: https://edugit.org/AlekSIS/Official/AlekSIS-App-DashboardFeeds/-/tags/2.0b0
.. _2.0rc1: https://edugit.org/AlekSIS/Official/AlekSIS-App-DashboardFeeds/-/tags/2.0rc1
.. _2.0: https://edugit.org/AlekSIS/Official/AlekSIS-App-DashboardFeeds/-/tags/2.0
.. _2.0.1: https://edugit.org/AlekSIS/Official/AlekSIS-App-DashboardFeeds/-/tags/2.0.1
.. _2.1: https://edugit.org/AlekSIS/Official/AlekSIS-App-DashboardFeeds/-/tags/2.1
.. _3.0b0: https://edugit.org/AlekSIS/Official/AlekSIS-App-DashboardFeeds/-/tags/3.0b0
.. _3.0: https://edugit.org/AlekSIS/Official/AlekSIS-App-DashboardFeeds/-/tags/3.0
