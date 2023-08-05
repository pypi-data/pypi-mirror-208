#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Check generation of BibTex output.
"""

# Third party library imports.
import pytest

# First party library imports.
from berhoel.ctitools.ctientry import CTIEntry
from berhoel.ctitools.cti2bibtex import BiBTeXEntry

__date__ = "2022/12/15 20:17:58 Berthold Höllmann"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


@pytest.fixture
def cti_entry_1():
    return CTIEntry(
        shorttitle=None,
        title="Java nur mit -server-Option",
        author=["Dr. Volker Zota", "Hans T. Meier"],
        pages=154,
        issue="2007 / 10",
        info={"paper": "c", "year": "07"},
        journaltitle="c't magazin für computertechnik",
        date="2007-04-30",
        references="",
        keywords="Praxis,Hotline,Java,Server,Internet,Programmierung,JAR-Archiv",
    )


@pytest.fixture
def cti_entry_2():
    return CTIEntry(
        shorttitle=None,
        title="Doppelt gemoppelt",
        author=["Torsten T. Will"],
        pages=74,
        issue="2008 / 3",
        info={"paper": "c", "year": "08"},
        journaltitle="c't magazin für computertechnik",
        date="2008-01-21",
        references="",
        keywords="kurz vorgestellt,Code Review,Open Source,Entwicklungssystem,"
        "Entwicklungs-Tools,Open-Source-Projekt Review Board",
    )


@pytest.fixture
def bibtex_entry_1(cti_entry_1):
    return BiBTeXEntry(cti_entry_1)


@pytest.fixture
def bibtex_entry_2(cti_entry_2):
    return BiBTeXEntry(cti_entry_2)


def test_autor_enty_1(bibtex_entry_1):
    assert (
        str(bibtex_entry_1)
        == """@article{154|c't_2007_/_10,
  title = {{J}ava nur mit -server-{O}ption},
  author = {Zota, Dr. Volker and Meier, Hans T.},
  date = {2007-04-30},
  journaltitle = {c't magazin für computertechnik},
  pages = {154},
  issue = {2007 / 10},
  keywords = {Praxis,Hotline,Java,Server,Internet,Programmierung,JAR-Archiv},
}
"""
    )


def test_autor_enty_2(bibtex_entry_2):
    assert (
        str(bibtex_entry_2)
        == """@article{74|c't_2008_/_3,
  title = {{D}oppelt gemoppelt},
  author = {Will, Torsten T.},
  date = {2008-01-21},
  journaltitle = {c't magazin für computertechnik},
  pages = {74},
  issue = {2008 / 3},
  keywords = {kurz vorgestellt,Code Review,Open Source,Entwicklungssystem,Entwicklungs-Tools,Open-Source-Projekt Review Board},
}
"""  # noqa: E501
    )


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%Y/%02m/%02d %02H:%02M:%02S %L\""
# End:
