Uploadable posters for time-based documents
===========================================

Posters are documents that can be manually supplied in a
time-based manner. Example use cases are cantine menus,
that are provided weekly by an external supplier, who
will only get privileges to upload this poster as a PDF
file.

Poster files can be uploaded for a defined time period,
and AlekSIS will then deliver the currently valid version
under a stable menu item and URL.

Defining poster groups
----------------------

Uploadable posters are categorised into poster groups, with
each poster group representing one time-based document that
AlekSIS will provide. Each poster group has:

 * A name
 * A URL slug making up the final, stable URL
 * A schedule defining the cycle for providing the document
 * A default PDF file for periods for which no document is uploaded

Permissions to upload documents are managed per poster group
as well.

Creating poster groups
~~~~~~~~~~~~~~~~~~~~~~

Poster groups are created from the menu under the `Documents → Poster groups`
menu item. After clicking the `Create new poster group` button or the `Edit`
action for any poster group, the following form allows editing the details
of the poster group.

.. image:: ../_static/create_poster_group.png
  :width: 600
  :alt: Create or edit a poster group

In addition to the properties explained above, the form provides two options
to configure if and how the document will be presented to users. It is possible
to include or exclude the document from the main menu, and to allow access
by anonymous users. Documents that are hidden from the menu can be used if
they should only be accessible through links from external sites, or
loaded by a digital signage system.

The stable URL for the poster group can be copied from the link
in the `Filename` column of the `Poster groups` list.
