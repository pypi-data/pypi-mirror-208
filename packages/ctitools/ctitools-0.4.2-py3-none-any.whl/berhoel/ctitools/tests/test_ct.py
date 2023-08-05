#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for processing c't entries.
"""

# Standard library imports.
from datetime import datetime

# Third party library imports.
import pytest

# First party library imports.
from berhoel.ctitools import ct

__date__ = "2023/05/12 20:48:30 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


@pytest.fixture(scope="session")
def issue_map():
    return ct.IssueMap()


@pytest.mark.parametrize(
    "issue,date",
    [
        ((2023, 13), datetime(2023, 5, 20)),
        ((2023, 12), datetime(2023, 5, 13)),
        ((2023, 11), datetime(2023, 5, 6)),
        ((2023, 1), datetime(2022, 12, 17)),
        ((2022, 26), datetime(2022, 12, 3)),
        ((2022, 17), datetime(2022, 7, 30)),
        ((2022, 16), datetime(2022, 7, 16)),
        ((2007, 10), datetime(2007, 4, 30)),
        ((2018, 27), datetime(2018, 10, 23)),
        ((2019, 27), datetime(2019, 10, 21)),
        ((2020, 27), datetime(2020, 10, 20)),
        ((2021, 27), datetime(2021, 10, 19)),
        ((2014, 15), datetime(2014, 6, 30)),
        ((1997, 10), datetime(1997, 10, 1)),
    ],
)
def test_ct_dategen(issue, date, issue_map):
    assert issue_map(*issue) == date


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%:y/%02m/%02d %02H:%02M:%02S %u\""
# End:
