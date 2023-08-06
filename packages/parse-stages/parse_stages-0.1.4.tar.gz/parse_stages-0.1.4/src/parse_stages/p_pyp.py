# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Parse an expression using the `pyparsing` library."""

# Let's make sure that the parsed tokens are exactly as we expect them to be
# flake8: noqa: S101

from __future__ import annotations

import pyparsing as pyp

from . import expr


EMPTY_SET_SPECS = ["", "0", "none"]
"""The list of exact strings that `parse_stage_ids()` will return an empty list for."""


_p_ws = pyp.White()[...]

_p_tag = pyp.Char("@").suppress() + pyp.Word(pyp.alphanums + "_-")

_p_keyword = pyp.Word(pyp.alphanums + "_-")

_p_atom = _p_tag | _p_keyword

_p_not_atom = pyp.Literal("not").suppress() + _p_ws.suppress() + _p_atom

_p_and_expr = (_p_not_atom | _p_atom) + (
    _p_ws.suppress() + pyp.Literal("and").suppress() + _p_ws.suppress() + (_p_not_atom | _p_atom)
)[...]

_p_or_expr = (
    _p_and_expr
    + (_p_ws.suppress() + pyp.Literal("or").suppress() + _p_ws.suppress() + _p_and_expr)[...]
)

_p_spec = _p_ws.suppress() + _p_or_expr


@_p_tag.set_parse_action
def _parse_tag(tokens: pyp.ParseResults) -> expr.TagExpr:
    """Parse a tag name."""
    assert len(tokens) == 1 and isinstance(tokens[0], str), repr(tokens)
    return expr.TagExpr(tag=tokens[0])


@_p_keyword.set_parse_action
def _parse_keyword(tokens: pyp.ParseResults) -> expr.KeywordExpr:
    """Parse a keyword."""
    assert len(tokens) == 1 and isinstance(tokens[0], str), repr(tokens)
    return expr.KeywordExpr(keyword=tokens[0])


@_p_atom.set_parse_action
def _parse_atom(tokens: pyp.ParseResults) -> expr.BoolExpr:
    """Parse an atom (a tag or a keyword)."""
    assert len(tokens) == 1 and isinstance(tokens[0], (expr.TagExpr, expr.KeywordExpr))
    return tokens[0]


@_p_not_atom.set_parse_action  # type: ignore[misc]
def _parse_not_atom(tokens: pyp.ParseResults) -> expr.NotExpr:
    """Parse a "not @tag" or "not keyword" element."""
    assert len(tokens) == 1 and isinstance(tokens[0], expr.BoolExpr)
    return expr.NotExpr(child=tokens[0])


@_p_and_expr.set_parse_action  # type: ignore[misc]
def _parse_and_expr(tokens: pyp.ParseResults) -> expr.BoolExpr:
    """Parse a "atom [and atom...]" subexpression."""
    children: list[expr.BoolExpr] = tokens.as_list()
    assert children and all(isinstance(item, expr.BoolExpr) for item in children)
    if len(children) == 1:
        return children[0]

    return expr.AndExpr(children=children)


@_p_or_expr.set_parse_action  # type: ignore[misc]
def _parse_or_expr(tokens: pyp.ParseResults) -> expr.BoolExpr:
    """Parse a "subexpr [or subexpr...]" subexpression."""
    children: list[expr.BoolExpr] = tokens.as_list()
    assert children and all(isinstance(item, expr.BoolExpr) for item in children)
    if len(children) == 1:
        return children[0]

    return expr.OrExpr(children=children)


_p_complete = _p_spec.leave_whitespace()


def parse_spec(spec: str) -> expr.BoolExpr:
    """Parse an expression using the `pyparsing` library."""
    res = _p_complete.parse_string(spec, parse_all=True).as_list()
    assert len(res) == 1 and isinstance(res[0], expr.BoolExpr), repr(res)
    return res[0]


_p_stage_id = pyp.Word(pyp.srange("[1-9]"), pyp.srange("[0-9]"))

_p_stage_range = _p_stage_id + pyp.Opt(pyp.Literal("-").suppress() + _p_stage_id)

_p_stage_ids = _p_stage_range + (pyp.Literal(",").suppress() + _p_stage_range)[...]


@_p_stage_id.set_parse_action
def _parse_stage_id(tokens: pyp.ParseResults) -> int:
    """Parse a single stage ID, return it as a zero-based index."""
    assert len(tokens) == 1 and isinstance(tokens[0], str), repr(tokens)
    res = int(tokens[0]) - 1
    assert res >= 0, repr((tokens, res))
    return res


@_p_stage_range.set_parse_action
def _parse_stage_range(tokens: pyp.ParseResults) -> list[int]:
    """Parse a range of stage IDs (possibly only containing a single one)."""
    if len(tokens) == 1:
        assert isinstance(tokens[0], int), repr(tokens)
        return [tokens[0]]

    # The magic value will go away once we can use Python 3.10 structural matching
    assert (
        len(tokens) == 2  # pylint: disable=magic-value-comparison
        and isinstance(tokens[0], int)
        and isinstance(tokens[1], int)
        and tokens[0] < tokens[1]
    ), repr(tokens)
    return list(range(tokens[0], tokens[1] + 1))


_p_stage_ids_complete = _p_stage_ids.leave_whitespace()


def parse_stage_ids(spec: str, *, empty_set_specs: list[str] | None = None) -> list[int]:
    """Parse a list of stage ranges, return them as zero-based indices.

    As a special case, the exact strings "" (an empty string), "0", and "none" will
    produce an empty list. Note that none of these strings are considered valid
    stage ranges, so they cannot be combined with any others (e.g. "0,3" is invalid).

    The default list of strings that signify an empty set ("", "0", "none") may be
    overridden by the `empty_set_specs` parameter.
    """
    if empty_set_specs is None:
        empty_set_specs = EMPTY_SET_SPECS
    if spec in empty_set_specs:
        return []

    res: list[int] = _p_stage_ids_complete.parse_string(spec, parse_all=True).as_list()
    assert all(isinstance(item, int) and item >= 0 for item in res), repr(res)
    return res
