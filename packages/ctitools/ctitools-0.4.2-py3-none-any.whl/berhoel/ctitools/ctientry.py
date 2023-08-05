#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Base class for cti (c't iX) entries.
"""

# Standard library imports.
from typing import Dict, Tuple
from dataclasses import dataclass

__date__ = "2022/09/08 11:57:16 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


@dataclass
class CTIEntry:
    """Store information from input file."""

    shorttitle: str
    title: str
    author: Tuple[str]
    pages: int
    issue: int
    info: Dict[str, str]
    journaltitle: str
    date: str
    references: str
    keywords: str

    def __hash__(self):
        return hash(
            (
                self.shorttitle,
                self.title,
                self.author,
                self.pages,
                self.issue,
                "".join(f"{i}{j}" for i, j in self.info.items()),
                self.journaltitle,
                self.date,
                self.references,
                self.keywords,
            )
        )


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%:y/%02m/%02d %02H:%02M:%02S %u\""
# End:
