# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Test some basic parsing functionality."""

# This is a test suite, right?
# flake8: noqa: S101

from __future__ import annotations

from typing import NamedTuple

import pytest

import parse_stages as pst


class Case(NamedTuple):
    """Specify a single test case: a string to parse, results."""

    spec: str
    res: pst.BoolExpr


class IdCase(NamedTuple):
    """Specify a single test case for stage IDs: a string to parse, results."""

    spec: str
    res: list[int]
    empty_set_specs: list[str] | None


_DEFS = [
    Case(spec="@check", res=pst.TagExpr(tag="check")),
    Case(spec="pep8", res=pst.KeywordExpr(keyword="pep8")),
    Case(spec="not @check", res=pst.NotExpr(child=pst.TagExpr(tag="check"))),
    Case(
        spec="@check and not pep8",
        res=pst.AndExpr(
            children=[
                pst.TagExpr(tag="check"),
                pst.NotExpr(child=pst.KeywordExpr(keyword="pep8")),
            ]
        ),
    ),
    Case(
        spec="not pep8 and @check or @tests or something",
        res=pst.OrExpr(
            children=[
                pst.AndExpr(
                    children=[
                        pst.NotExpr(child=pst.KeywordExpr(keyword="pep8")),
                        pst.TagExpr(tag="check"),
                    ]
                ),
                pst.TagExpr(tag="tests"),
                pst.KeywordExpr(keyword="something"),
            ]
        ),
    ),
    Case(
        spec="black and not black-reformat",
        res=pst.AndExpr(
            children=[
                pst.KeywordExpr(keyword="black"),
                pst.NotExpr(child=pst.KeywordExpr(keyword="black-reformat")),
            ]
        ),
    ),
]

_IDS = [
    IdCase(spec="", res=[], empty_set_specs=None),
    IdCase(spec="0", res=[], empty_set_specs=None),
    IdCase(spec="none", res=[], empty_set_specs=None),
    IdCase(spec="empty", res=[], empty_set_specs=["", "empty"]),
    IdCase(spec="1", res=[0], empty_set_specs=None),
    IdCase(spec="2,6,4", res=[1, 5, 3], empty_set_specs=None),
    IdCase(spec="1-3,4-6", res=[0, 1, 2, 3, 4, 5], empty_set_specs=None),
    IdCase(spec="1-3,5-6", res=[0, 1, 2, 4, 5], empty_set_specs=None),
    IdCase(spec="1-3,7-10,4", res=[0, 1, 2, 6, 7, 8, 9, 3], empty_set_specs=None),
]


@pytest.mark.parametrize("case", _DEFS)
def test_basic(case: Case) -> None:
    """Make sure we parse a specification correctly."""
    assert pst.parse_spec(case.spec) == case.res


@pytest.mark.parametrize("case", _IDS)
def test_ids_basic(case: IdCase) -> None:
    """Make sure we parse a set of stage IDs correctly."""
    assert pst.parse_stage_ids(case.spec, empty_set_specs=case.empty_set_specs) == case.res
