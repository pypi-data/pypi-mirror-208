Ctitools
========

Work with cti index files for the Heise papers c’t and iX

Description
-----------

This project provides diffrent tool for processing index files from
Heise papers c’t and iX.

Saving the current base dataset, downloaded from Heise and extractng to
data, the command

.. code:: console

  > cti2bibtex data/inhalt.frm result.bibtex

creates a ``.bib`` file with 82100 entries. Importing this result in
Zotero took more than 28h and use more than 7GB of RAM.

Installation
------------

.. code:: console

  > pip install git+https://gitlab.com/berhoel/python/ctitools.git

Documentation
-------------

Documentation can be found `here <https://python.höllmanns.de/ctitools/>`_

Authors
-------

- Berthold Höllmann <berthold@xn--hllmanns-n4a.de>

Project status
--------------

The projects works for converting the `cti` and `frm` file, provided
by Heise, to `bib` files.
