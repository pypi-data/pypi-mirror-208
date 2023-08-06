Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.

`2.0`_ - 2023-05-15
-------------------

Nothing changed.

`2.0b0`_ - 2023-03-01
---------------------

This version requires AlekSIS-Core 3.0. It is incompatible with any previous
version.

Removed
~~~~~~~

* Legacy menu integration for AlekSIS-Core pre-3.0

Added
~~~~~

* Add SPA support for AlekSIS-Core 3.0

Fixed
~~~~~

* When no page to redirect to was passed to some of the seating plan views, an error occured.

`1.0.2`_ - 2022-11-04
---------------------

Fixed
~~~~~

* Creating new seating plans was still forbidden for some users.

`1.0.1`_ - 2022-09-01
---------------------

Fixed
~~~~~

* Creating new seating plans was forbidden for all users.

`1.0`_
------

Added
~~~~~

* Add views for creating and managing seating plans for different groups in different rooms.
* Make these plans available in the class register.
* Allow customizing plans for individual combinations of groups, subjects and rooms.
* Add preliminary and incomplete translation to Ukrainian.

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html


.. _1.0: https://edugit.org/AlekSIS/official/AlekSIS-App-Stoelindeling/-/tags/1.0
.. _1.0.1: https://edugit.org/AlekSIS/official/AlekSIS-App-Stoelindeling/-/tags/1.0.1
.. _1.0.2: https://edugit.org/AlekSIS/official/AlekSIS-App-Stoelindeling/-/tags/1.0.2
.. _2.0b0: https://edugit.org/AlekSIS/official/AlekSIS-App-Stoelindeling/-/tags/2.0b0
.. _2.0: https://edugit.org/AlekSIS/official/AlekSIS-App-Stoelindeling/-/tags/2.0
