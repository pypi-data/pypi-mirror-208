#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Export cti as BiBTeX for Zotero.
"""

# Standard library imports.
import re
import argparse
from pathlib import Path

# Local library imports.
from .. import CTI, __version__

__date__ = "2022/12/15 20:51:37 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


class BiBTeXEntry:
    def __init__(self, entry):
        """Intitalize

        :param `entry`:
        :type entry:
        """
        self.entry = entry

    @staticmethod
    def fix_title(inp):
        upper = re.compile(r"([A-Z])")
        return upper.sub(r"{\1}", inp)

    def __str__(
        self,
    ):
        """Return string for entry"""
        authors = " and ".join(
            ", ".join(j[::-1] for j in i[::-1].split(maxsplit=1))
            for i in self.entry.author
        )
        papershort = {"c't magazin für computertechnik": "c't"}.get(
            self.entry.journaltitle, self.entry.journaltitle
        )
        keywords = ",".join(
            s for i in self.entry.keywords.split(",") if (s := i.strip())
        )
        res = f"""\
@article{{{self.entry.pages}|{papershort}_{self.entry.issue.replace(' ', '_')},
  title = {{{self.fix_title(self.entry.title)}}},"""
        if self.entry.shorttitle is not None:
            res = f"""{res}
  shorttitle = {{{self.fix_title(self.entry.shorttitle)}}},"""
        return f"""{res}
  author = {{{authors}}},
  date = {{{self.entry.date}}},
  journaltitle = {{{self.entry.journaltitle}}},
  pages = {{{self.entry.pages}}},
  issue = {{{self.entry.issue}}},
  keywords = {{{keywords}}},
}}
"""


def build_parser():
    "Build cli parser."
    parser = argparse.ArgumentParser(
        prog="cti2bibtex",
        description="Read a cti file and generate a BiBTeX file.",
    )
    parser.add_argument(
        "cti",
        type=Path,
        help="""input file, cti, frm, or zip file containing one of the  previous
(required)""",
    )
    parser.add_argument(
        "bibtex",
        type=Path,
        nargs="?",
        default=None,
        help="output file (name will be derived from input file, if not given)",
    )
    parser.add_argument(
        "--limit-year",
        type=int,
        default=None,
        help="limit output to given year (default: all years in input file)",
    )
    parser.add_argument(
        "--limit-issue",
        type=int,
        default=None,
        help="limit output to given issue (default: all issues in input file)",
    )
    parser.add_argument(
        "--limit-journal",
        type=str,
        default=None,
        help="limit output to given magazine ('i' for iX, or 'c'  for c't) "
        "(default: both magazines)",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    cti = CTI(
        args.cti,
        args.limit_year,
        args.limit_issue,
        args.limit_journal,
    )

    out = args.cti.with_suffix(".bib") if args.bibtex is None else args.bibtex

    with out.open("w") as outp:
        for entry in cti:
            outp.write(str(BiBTeXEntry(entry)))


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%:y/%02m/%02d %02H:%02M:%02S %u\""
# End:
