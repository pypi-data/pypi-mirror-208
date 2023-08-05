#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Work with cti index files for the Heise papers c't and iX
"""

# Standard library imports.
import re
import asyncio
import zipfile
import argparse
from typing import List
from pathlib import Path
from contextlib import suppress
from collections import defaultdict

# Local library imports.
from .ct import Ct
from .ix import Ix

__date__ = "2022/12/02 20:55:12 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"

try:
    # Local library imports.
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0.invalid0"


class CTI:
    """Read entries from cti files:

    .. code:: asc

      Bürokratie: Mit analoger Wucht

      Tim Gerber
      tig
        3
      16
      c22

      Standpunkt,Immer in c't,Gesellschaft,Ukraine-Krieg,Ukraine-Hilfe,Digitalisierung
    """

    paper_year = re.compile(r"(?P<paper>[ci])(?P<year>[0-9]{2})")
    paper_map = {"i": "iX", "c": "c't magazin für computertechnik"}

    def __init__(
        self,
        infile: Path,
        limit_year: int = None,
        limit_issue: int = None,
        limit_journal: str = None,
    ):
        """Read input file.

        Args:
          infile (file): Input file
          limit_year (int): Limit output to given year
          limit_issue (int): Limit output to given issue
          limit_journal (str): Limit output to given journal
        """

        self.__entries = []
        self.limit_year = limit_year
        self.limit_issue = limit_issue
        self.limit_journal = limit_journal
        if zipfile.is_zipfile(infile):
            with zipfile.ZipFile(infile) as thiszip:
                infolist = thiszip.infolist()
                for info in infolist:
                    extension = info.filename.split(".")[-1]
                    if extension in {"frm", "cti"}:
                        with thiszip.open(info, "r") as inp:
                            self.__entries.extend(asyncio.run(self._gen_data(inp)))
        else:
            with infile.open("rb") as inp:
                self.__entries.extend(asyncio.run(self._gen_data(inp)))

    async def _gen_data(self, inp):
        return [
            entry
            async for data in self._read_lines(inp)
            if (entry := await self._parse_input(data)) is not None
        ]

        # return await asyncio.gather(
        #     *[
        #         entry
        #         async for data in self._read_lines(inp)
        #         if (entry := self._parse_input(data)) is not None
        #     ]
        # )

    async def _read_lines(self, inp):
        while True:
            res = [l for _, l in zip(range(9), inp)]
            if len(res) != 9:
                return
            yield res

    async def _parse_input(self, data: List[str]):
        shorttitle = (
            self.fix_chars(data[0]).decode(encoding="cp858", errors="ignore").strip()
        )
        title = (
            self.fix_chars(data[1]).decode(encoding="cp858", errors="ignore").strip()
        )
        author = self.fix_author(
            self.fix_chars(data[2])
            .decode(encoding="cp858", errors="ignore")
            .strip()
            .strip(",")
        )
        data[3].decode(encoding="cp858", errors="ignore").strip()  # author shortsign
        pages = int(data[4].decode(encoding="cp858", errors="ignore").strip())
        issue = int(data[5].decode(encoding="cp858", errors="ignore").strip())
        info = self.paper_year.match(
            data[6].decode(encoding="cp858", errors="ignore").strip()
        ).groupdict()
        journal = info["paper"]
        year = int(info["year"])
        year += 1900 if year > 80 else 2000
        references = data[7].decode(encoding="cp858", errors="ignore").strip()
        keywords = (
            self.fix_chars(data[8])
            .decode(encoding="cp858", errors="ignore")
            .strip()
            .strip(",")
        )
        if (
            (self.limit_issue is not None and issue != self.limit_issue)
            or (self.limit_journal is not None and journal != self.limit_journal)
            or (self.limit_year is not None and year != self.limit_year)
        ):
            return
        return {"c": Ct, "i": Ix}[journal](
            shorttitle=shorttitle,
            title=title,
            author=author,
            pages=pages,
            issue=issue,
            info=info,
            year=year,
            references=references,
            keywords=keywords,
        )()

    @staticmethod
    def fix_chars(inp: str) -> str:
        table = bytes.maketrans(
            b"\334\344\374\366\337\351", b"\232\204\201\224\341\202"
        )
        return inp.translate(table).replace(b"\307\317", b"\204")

    dusan_replace_re = re.compile(
        "|".join(
            (
                "Duzan",
                "Dusan",
            )
        )
    )
    zivadinovic_replace_re = re.compile(
        "|".join(
            (
                "Zivadinovic",
                "Zivadinovi∩c",
                "Zivadinovi'c",
                "Zivadanovic",
                "Zivadinivic",
            )
        )
    )

    @staticmethod
    def fix_author(author):
        """Fix author information

        Args:
          author (str):

        Returns:
          str
        """
        if author.count(",") > 0 and author.count(",") == author.count(" "):
            res = []
            for i in author.split("/"):
                res.append(" ".join(j.strip() for j in i.split(",")[::-1]))
            author = ",".join(res)
        author = author.replace(" und ", ", ")
        author = author.replace("Von ", "")
        author = "Dušan".join(CTI.dusan_replace_re.split(author))
        author = "Živadinović".join(CTI.zivadinovic_replace_re.split(author))
        author = author.replace('M"cker', "Möcker")

        return tuple([i.strip() for i in author.split(",")])

    def __iter__(self):
        return iter(self.__entries)


def main():
    parser = argparse.ArgumentParser("Read cti file.")
    parser.add_argument("cti", type=Path, help="input file (required)")
    args = parser.parse_args()

    CTI(args.cti)


def build_cti_statistics_parser():
    parser = argparse.ArgumentParser(
        prog="cti_statistics",
        description="List number of articles for each issue found in input file.",
    )
    parser.add_argument(
        "cti",
        type=Path,
        help="""input file, cti, frm, or zip file containing one of the  previous
(required)""",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser


def issue_key(a):
    month_sort = {
        "Januar": 1,
        "Februar": 2,
        "März": 3,
        "April": 4,
        "Mai": 5,
        "Juni": 6,
        "Juli": 7,
        "August": 8,
        "September": 9,
        "Oktober": 10,
        "November": 11,
        "Dezember": 12,
        "retro": 27,
        "ausblick": 27,
    }
    if isinstance(a, str):
        a = month_sort[a]
    return a


def cti_statistics():
    args = build_cti_statistics_parser().parse_args()
    cti = CTI(args.cti)

    data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for entry in cti:
        paper = "c't" if entry.info["paper"] == "c" else "iX"
        year, issue = entry.issue.split("/")
        issue = issue.strip()
        with suppress(ValueError):
            issue = int(issue)
        data[paper][int(year)][issue] += 1

    for paper in ("iX", "c't"):
        print(paper)
        years = sorted(data[paper].keys())
        for year in years:
            print(f"{year}")
            issues = sorted(data[paper][year].keys(), key=issue_key)
            s_issues = [f"{i}" for i in issues]
            s_issues = [f"{i:>{max(len(i),3)}}" for i in s_issues]
            print(" ".join(s_issues))
            print(
                " ".join(
                    f"{data[paper][year][i]:>{len(s)}}"
                    for i, s in zip(issues, s_issues)
                )
            )


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%:y/%02m/%02d %02H:%02M:%02S %u\""
# End:
