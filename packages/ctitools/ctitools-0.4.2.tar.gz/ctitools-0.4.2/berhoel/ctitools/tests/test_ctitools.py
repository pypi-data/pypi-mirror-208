#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for ctitools.
"""

# Standard library imports.
from pathlib import Path

# Third party library imports.
import toml
import pytest

# First party library imports.
from berhoel import ctitools

__date__ = "2022/08/01 16:00:56 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


@pytest.fixture
def base_path():
    "Return path to project base."
    return Path(__file__).parents[3]


@pytest.fixture
def py_project(base_path):
    "Return path of project `pyproject.toml`."
    return base_path / "pyproject.toml"


@pytest.fixture
def toml_inst(py_project):
    "Return `toml` instance of project `pyproject.toml`"
    return toml.load(py_project.open("r"))


def test_version(toml_inst):
    "Test for consistent version numbers."
    assert ctitools.__version__ == toml_inst["tool"]["poetry"]["version"]


# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%:y/%02m/%02d %02H:%02M:%02S %u\""
# End:
