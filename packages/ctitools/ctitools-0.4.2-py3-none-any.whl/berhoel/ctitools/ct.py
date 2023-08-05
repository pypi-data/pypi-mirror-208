#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Manage entries for c't.
"""

# Standard library imports.
from datetime import datetime, timedelta

# Local library imports.
from .ctientry import CTIEntry

__date__ = "2023/05/12 20:47:25 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


class IssueMap:
    """Class for determinig issue date for c't issues."""

    def __init__(self):
        self._issue_max: tuple[int, int] = (2022, 16)
        self._issue_min: tuple[int, int] = self._issue_max
        self._date_max: datetime = datetime(year=2022, month=7, day=16)
        self._date_min: datetime = self._date_max
        self._cache: dict[tuple[int, int], datetime] = {
            self._issue_max: self._date_max,
            (2018, 27): datetime(2018, 10, 23),
            (2019, 27): datetime(2019, 10, 21),
            (2020, 27): datetime(2020, 10, 20),
            (2021, 27): datetime(2021, 10, 19),
            (2022, 27): datetime(2022, 11, 26),
        }

    def __call__(self, year: int, issue: int) -> datetime:
        """Generate release dates for c't."""
        key = (year, issue)
        diff = timedelta(days=14)
        if self._cache.get(key) is not None:
            return self._cache[key]
        while key > self._issue_max:
            step_year, step_issue = self._issue_max
            step_issue += 1
            if step_issue >= 27:
                step_issue = 1
                step_year += 1
            self._issue_max = (step_year, step_issue)
            if (step_year, step_issue) == (2023, 12):
                self._date_max = datetime(2023, 5, 13)
            elif (step_year, step_issue) == (2023, 13):
                self._date_max = datetime(2023, 5, 20)
            else:
                self._date_max += diff
            self._cache[self._issue_max] = self._date_max
            assert self._date_max < datetime.now() + timedelta(
                days=16
            ), f"{self._date_max=} < {datetime.now() + timedelta(days=14)=}, {key=}"
        while key < self._issue_min:
            if self._date_min <= datetime(1997, 10, 13):
                step_issue -= 1
                if step_issue < 1:
                    step_issue = 12
                    step_year -= 1
                self._date_min = datetime(step_year, step_issue, 1)
                self._issue_min = (step_year, step_issue)
            else:
                self._date_min -= diff
                step_year, step_issue = self._issue_min
                step_issue -= 1
                if self._date_min == datetime(2014, 6, 28):
                    self._date_min += timedelta(days=2)
                if step_issue < 1:
                    step_year -= 1
                    if step_year in {2015}:
                        step_issue = 27
                    elif self._date_min < datetime(1997, 1, 1):
                        step_issue = 12
                    elif self._date_min < datetime(1998, 1, 5):
                        step_issue = 16
                    else:
                        step_issue = 26

                self._issue_min = (step_year, step_issue)
            self._cache[self._issue_min] = self._date_min
            assert self._date_min > datetime(
                1983, 1, 1
            ), f"{self._date_min=} > {datetime(1983, 1, 1)=}"

        return self._cache[key]


class Ct:
    """Prepare c't issue information."""

    issue_map = IssueMap()
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
        author: list[str],
        pages: int,
        issue: int,
        info: str,
        year: int,
        references: str,
        keywords: str,
    ):
        """Add information for a c't issue.

        Args:
          shorttitle (str):
          title (str):
          author (str):
          pages (int):
          issue (int):
          info (str):
          year (int):
          keywords (str):
        """
        full_issue = self.year_issue2full_issue(year, issue)
        self.date = self.issue_map(year, issue)
        if not title:
            self.shorttitle, self.title = None, shorttitle
        else:
            self.shorttitle, self.title = (
                shorttitle,
                title,
            )
        self.author = author
        self.pages = pages
        self.full_issue = full_issue
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
            "c't magazin für computertechnik",
            self.date.strftime("%Y-%m-%d"),
            self.references,
            self.keywords,
        )

    @staticmethod
    def year_issue2full_issue(year, issue):
        """Retrieve full issue for c't from year and issue number.

        Args:
          year (int):
          issue (int):

        Returns:
          str
        """
        if issue == 27:
            if year == 2022:
                issue = "c't Jahresrückblick 2022"
            elif year > 2015:
                issue = "retro"
        if year < 1997 or year == 1997 and issue < 11:
            return f"{year:04d} / {Ct.month_issue_map[issue]}"
        return f"{year:04d} / {issue}"


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%:y/%02m/%02d %02H:%02M:%02S %u\""
# End:
