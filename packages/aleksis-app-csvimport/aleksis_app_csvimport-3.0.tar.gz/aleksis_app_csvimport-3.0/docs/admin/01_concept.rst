Base concept of the generic importer
====================================

For importing comma-separated or, more generally, any
sort of column-based data in text files, AlekSIS provides
a generic importer.

The importer works with so-called *import templates*. These
templates set a field type for each column in a file. With
this information, the importer will know how to interpret
each cell.

Default templates
-----------------

For import sources that have already been tested, AlekSIS
provides import templates that are readily available.

Right now, the following import sources are supported:

* `Pedasos`_, a school management solution popular in Northern Germany
* `Schild-NRW`_, the obligatory school management solution in North-Rhine Westphalia, Germany

These software products either provide hard-coded export mechanisms,
or allow the creation of report/export templates to generate CSV-like output.

Custom templates
----------------

In addition to the integrated default templates, custom
templates can be created by administrators. Creating custom
import templates currently requires hand-crafting *YAML* files
that can then be uploaded through the user interface.

However, this feature is currently deliberately undocumented.

.. _Pedasos: https://ostertun.de/produkt.html
.. _Schild-NRW: https://www.svws.nrw.de/download/schild-nrw
