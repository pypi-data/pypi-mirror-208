Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.

`3.0`_ - 2023-05-12
-------------------

Nothing changed.

`3.0b2`_ - 2023-03-20
---------------------

Fixed
~~~~~

* Menu item was shown for all users independent of permissions.

`3.0b1`_ - 2023-03-09
---------------------

Fixed
~~~~~

* Provide PDF documents outside django/ URL namespace again

`3.0b0`_ - 2023-02-16
---------------------

This version requires AlekSIS-Core 3.0. It is incompatible with any previous
version.

Removed
~~~~~~~

* Legacy menu integration for AlekSIS-Core pre-3.0

Added
~~~~~

* Add SPA support for AlekSIS-Core 3.0

`2.2`_ - 2022-06-23
-------------------

Added
~~~~~

* Add Ukrainian locale (contributed by Sergiy Gorichenko from Fre(i)e Software GmbH).

`2.1`_ - 2022-01-12
-------------------

Added
~~~~~

* Open poster group menu entries in new tab.
* [Dev] LiveDocument.update() now has a default implementaiton, rendering
  ``self.template`` using ``self.get_context_data()``
* End-user, admin and dev documentation

Fixed
~~~~~

* Live documents table showed two "Actions" columns.
* Menu was not correctly re-generated after creating or editing poster groups
* Button for creation of live documents was there even if there weren't any live document types registered.

`2.0`_ - 2021-12-27
-------------------

Nothing changed.

`2.0b1`_ - 2021-11-07
---------------------

Added
~~~~~

* Provide API view for accessing the current PDF file of a live document (secured with OAuth2).

Changed
~~~~~~~

* German translations were updated.

`2.0b0`_ - 2021-11-03
--------------------

Added
~~~~~

* Provide ``Poster`` model for time-based documents.
  * Organise posters in poster groups.
  * Return current poster of a poster group as PDF file under a specific endpoint.
* Provide ``LiveDocument`` for periodically updated documents.


.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

.. _2.0b0: https://edugit.org/AlekSIS/official/AlekSIS-App-Resint/-/tags/2.0b0
.. _2.0b1: https://edugit.org/AlekSIS/official/AlekSIS-App-Resint/-/tags/2.0b1
.. _2.0: https://edugit.org/AlekSIS/official/AlekSIS-App-Resint/-/tags/2.0
.. _2.1: https://edugit.org/AlekSIS/official/AlekSIS-App-Resint/-/tags/2.1
.. _2.2: https://edugit.org/AlekSIS/official/AlekSIS-App-Resint/-/tags/2.2
.. _3.0b0: https://edugit.org/AlekSIS/official/AlekSIS-App-Resint/-/tags/3.0b0
.. _3.0b1: https://edugit.org/AlekSIS/official/AlekSIS-App-Resint/-/tags/3.0b1
.. _3.0b2: https://edugit.org/AlekSIS/official/AlekSIS-App-Resint/-/tags/3.0b2
.. _3.0: https://edugit.org/AlekSIS/official/AlekSIS-App-Resint/-/tags/3.0
