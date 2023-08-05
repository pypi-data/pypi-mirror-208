#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Basic tests for generating BibTex entries from c't and iX articles.
"""

# First party library imports.
from berhoel.ctitools.ctientry import CTIEntry
from berhoel.ctitools.cti2bibtex import BiBTeXEntry

__date__ = "2022/10/20 21:16:42 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


def test_with_shorttitle():
    probe = BiBTeXEntry(
        CTIEntry(
            shorttitle="shorttitle",
            title="title",
            author=["author"],
            pages="pages",
            issue="issue",
            info="info",
            journaltitle="journaltitle",
            date="date",
            references="references",
            keywords="keywords",
        )
    )
    assert (
        str(probe)
        == """@article{pages|journaltitle_issue,
  title = {title},
  shorttitle = {shorttitle},
  author = {author},
  date = {date},
  journaltitle = {journaltitle},
  pages = {pages},
  issue = {issue},
  keywords = {keywords},
}
"""
    )


def test_without_shorttitle():
    probe = BiBTeXEntry(
        CTIEntry(
            shorttitle=None,
            title="title",
            author=["author"],
            pages="pages",
            issue="issue",
            info="info",
            journaltitle="journaltitle",
            date="date",
            references="references",
            keywords="keywords",
        )
    )
    assert (
        str(probe)
        == """@article{pages|journaltitle_issue,
  title = {title},
  author = {author},
  date = {date},
  journaltitle = {journaltitle},
  pages = {pages},
  issue = {issue},
  keywords = {keywords},
}
"""
    )


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%:y/%02m/%02d %02H:%02M:%02S %u\""
# End:
