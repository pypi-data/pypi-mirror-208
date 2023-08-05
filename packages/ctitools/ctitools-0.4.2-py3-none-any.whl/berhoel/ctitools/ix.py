#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Manage entries for iX.
"""

# Standard library imports.
from datetime import datetime

# Local library imports.
from .ctientry import CTIEntry

__date__ = "2022/08/01 17:08:30 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


class Ix(CTIEntry):
    """Prepare iX issue information."""

    month_issue_map = {
        1: "Januar",
        2: "Februar",
        3: "März",
        4: "April",
        5: "Mai",
        6: "Juni",
        7: "Juli",
        8: "August",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Dezember",
    }

    def __init__(
        self,
        shorttitle: str,
        title: str,
        author: str,
        pages: int,
        issue: int,
        info: str,
        year: int,
        references: str,
        keywords: str,
    ):
        """Add information for a iX issue.

        Args:
          shorttitle (str):
          title (str):
          author (str):
          pages (int):
          issue (int):
          info (str):
          journal (str):
          year (int):
          keywords (str):
        """
        if not title:
            self.shorttitle, self.title = None, shorttitle
        else:
            self.shorttitle, self.title = shorttitle, title
        self.issue, self.date = (
            {
                2016: ("iX Special 2016", datetime(2016, 6, 3)),
                2017: ("iX Special 2017", datetime(2017, 6, 9)),
                2018: ("iX Special 2018", datetime(2018, 5, 25)),
                2019: ("iX Special 2019", datetime(2019, 6, 3)),
                2020: ("iX Special 2020", datetime(2020, 6, 12)),
                2021: ("iX Special 2021", datetime(2021, 6, 9)),
                2022: ("iX Special Green IT", datetime(2022, 6, 8)),
            }[year]
            if issue > 12
            else (self.month_issue_map[issue], datetime(year, issue, 1))
        )
        self.full_issue = f"{year} / {issue}"
        self.author = author
        self.pages = pages
        self.info = info
        self.references = references
        self.keywords = keywords

    def __call__(self):
        return CTIEntry(
            self.shorttitle,
            self.title,
            self.author,
            self.pages,
            self.full_issue,
            self.info,
            "iX",
            self.date.strftime("%Y-%m-%d"),
            self.references,
            self.keywords,
        )


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%:y/%02m/%02d %02H:%02M:%02S %u\""
# End:
