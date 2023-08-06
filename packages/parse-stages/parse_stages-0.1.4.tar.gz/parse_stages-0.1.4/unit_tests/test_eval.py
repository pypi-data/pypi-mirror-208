# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Test the evaluation of some simple expressions."""

# This is a test suite, right?
# flake8: noqa: S101

from __future__ import annotations

import dataclasses

from typing import NamedTuple

import pytest

import parse_stages as pst


@dataclasses.dataclass(frozen=True)
class Environment(pst.TaggedFrozen):
    """Specify an environment to be matched by a spec (or not)."""


class Case(NamedTuple):
    """Specify a single test case: a string to parse, results."""

    spec: str
    matched: list[str]


_ALL = [
    Environment(name="t-black", tags=["check"]),
    Environment(name="t-black-reformat", tags=["do", "reformat"]),
    Environment(name="t-pep8", tags=["check"]),
    Environment(name="t-mypy", tags=["check"]),
    Environment(name="t-pylint", tags=["check"]),
    Environment(name="t-unit-tests", tags=["tests"]),
    Environment(name="t-runner-pep8", tags=["check", "runner"]),
]

_TESTS = [
    Case(spec="@check", matched=["t-black", "t-pep8", "t-mypy", "t-pylint", "t-runner-pep8"]),
    Case(spec="@tests", matched=["t-unit-tests"]),
    Case(spec="@check and not pep8", matched=["t-black", "t-mypy", "t-pylint"]),
    Case(spec="not pep8 and @check", matched=["t-black", "t-mypy", "t-pylint"]),
    Case(spec="@check and pep8 or @tests", matched=["t-pep8", "t-unit-tests", "t-runner-pep8"]),
    Case(spec="black", matched=["t-black", "t-black-reformat"]),
    Case(spec="black and not black-reformat", matched=["t-black"]),
    Case(spec="black and not black-reformat", matched=["t-black"]),
]


@pytest.mark.parametrize("case", _TESTS)
def test_basic(case: Case) -> None:
    """Make sure evaluation works more or less correctly."""
    expr = pst.parse_spec(case.spec)
    assert [env.name for env in _ALL if expr.evaluate(env)] == case.matched
