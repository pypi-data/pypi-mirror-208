#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Test article entry processing.
"""

# Standard library imports.
import zipfile

# Third party library imports.
import pytest

# First party library imports.
from berhoel.ctitools import CTI
from berhoel.ctitools.ctientry import CTIEntry

__date__ = "2022/09/08 12:05:11 Berthold Höllmann"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


@pytest.fixture
def cti_entry_data_1():
    return b"""Java nur mit -server-Option

Dr. Volker Zota, Dusan Wasserb\xc7\xcfch
vza
154
10
c07

Praxis,Hotline,Java, Server, Internet, Programmierung, JAR-Archiv
Ein Artikel

Von Torsten T. Will und Ein Autor, Duzan Zivadinovic
ola
 74
 3
c08

kurz vorgestellt,Code Review, Open Source, Entwicklungssystem,Entwicklungs-Tools,Open-Source-Projekt Review Board
"""  # noqa: E501


@pytest.fixture
def cti_entry_1(tmp_path, cti_entry_data_1):
    p = tmp_path / "cti_entry_1.cti"
    p.write_bytes(cti_entry_data_1)
    return p


@pytest.fixture
def cti_entry_zip_1(tmp_path, cti_entry_data_1):
    p = tmp_path / "cti_entry_1.zip"
    with zipfile.ZipFile(p, "w") as myzip:
        myzip.writestr("cti_entry_1.frm", cti_entry_data_1)
    return p


@pytest.fixture
def cti_entry_data_2():
    return b"""Doppelt gemoppelt
\334\344\374\366\337\351
Von Torsten T. Will und Ein Autor, Duzan Zivadinovic
ola
 74
 3
c08

kurz vorgestellt,Code Review, Open Source, Entwicklungssystem,Entwicklungs-Tools,Open-Source-Projekt Review Board
"""  # noqa: E501


@pytest.fixture
def cti_entry(request):
    return request.getfixturevalue(request.param)


@pytest.fixture
def cti_entry_2(tmp_path, cti_entry_data_2):
    p = tmp_path / "cti_entry_2.cti"
    p.write_bytes(cti_entry_data_2)
    return p


@pytest.fixture
def cti_entry_zip_2(tmp_path, cti_entry_data_2):
    p = tmp_path / "cti_entry_2.zip"
    with zipfile.ZipFile(p, "w") as myzip:
        myzip.writestr("cti_entry_2.cti", cti_entry_data_2)
    return p


@pytest.fixture
def cti_entry_data_3():
    return b"""Familienleben
Digitals Alpha-Linie: Vorstellung von f\201nf 64-Bit-Rechnern in London
Behme, Henning
hb
 13
 1
i93

Markt + Trends
Schlu\341folgerungsmuster
Objektorientierte Verkn\201pfung von Wissensbasen und Datenbanken
Higa, Kunihiko/Morrison, Joline+Mike
hb
132
 1
i93

Wissen
"""


@pytest.fixture
def cti_entry_3(tmp_path, cti_entry_data_3):
    p = tmp_path / "cti_entry_3.cti"
    p.write_bytes(cti_entry_data_3)
    return p


@pytest.mark.parametrize("cti_entry", ["cti_entry_1", "cti_entry_zip_1"], indirect=True)
def test_process_author_1(cti_entry):
    probe = iter(CTI(cti_entry))
    assert next(probe).author == ("Dr. Volker Zota", "Dušan Wasserbäch")


def test_ctientry_1():
    assert CTIEntry(
        shorttitle="a",
        title="a",
        author="a",
        pages=1,
        issue=1,
        info="a",
        journaltitle="a",
        date="a",
        references="a",
        keywords="a",
    ) == CTIEntry(
        shorttitle="a",
        title="a",
        author="a",
        pages=1,
        issue=1,
        info="a",
        journaltitle="a",
        date="a",
        references="a",
        keywords="a",
    )


def test_ctientry_2():
    assert CTIEntry(
        shorttitle="b",
        title="a",
        author="a",
        pages=1,
        issue=1,
        info="a",
        journaltitle="a",
        date="a",
        references="a",
        keywords="a",
    ) != CTIEntry(
        shorttitle="a",
        title="a",
        author="a",
        pages=1,
        issue=1,
        info="a",
        journaltitle="a",
        date="a",
        references="a",
        keywords="a",
    )


@pytest.mark.parametrize("cti_entry", ["cti_entry_2", "cti_entry_zip_2"], indirect=True)
def test_process_author_2(cti_entry):
    probe = iter(CTI(cti_entry))
    assert next(probe).author == (
        "Torsten T. Will",
        "Ein Autor",
        "Dušan Živadinović",
    )


@pytest.mark.parametrize("cti_entry", ["cti_entry_2", "cti_entry_zip_2"], indirect=True)
def test_process_chars_2(cti_entry):
    probe = iter(CTI(cti_entry))
    assert next(probe).title == "Üäüößé"


def test_process_authors_ix_3(cti_entry_3):
    references = (
        CTIEntry(
            shorttitle="Familienleben",
            title="Digitals Alpha-Linie: Vorstellung von fünf 64-Bit-Rechnern in "
            "London",
            author=("Henning Behme",),
            pages=13,
            issue="1993 / 1",
            info={"paper": "i", "year": "93"},
            journaltitle="iX",
            date="1993-01-01",
            references="",
            keywords="Markt + Trends",
        ),
        CTIEntry(
            shorttitle="Schlußfolgerungsmuster",
            title="Objektorientierte Verknüpfung von Wissensbasen und Datenbanken",
            author=("Kunihiko Higa", "Joline+Mike Morrison"),
            pages=132,
            issue="1993 / 1",
            info={"paper": "i", "year": "93"},
            journaltitle="iX",
            date="1993-01-01",
            references="",
            keywords="Wissen",
        ),
    )

    data_read = False
    for probe, ref in zip(iter(CTI(cti_entry_3)), references):
        assert probe == ref
        data_read = True
    assert data_read, "No data read"


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%Y/%02m/%02d %02H:%02M:%02S %L\""
# End:
