# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""The hierarchy of classes representing an expression and its components."""

from __future__ import annotations

import abc
import dataclasses

from . import defs


@dataclasses.dataclass(frozen=True)
class BoolExpr(metaclass=abc.ABCMeta):
    """A boolean expression parsed out of a specification string."""

    @abc.abstractmethod
    def evaluate(self, obj: defs.TaggedFrozen | defs.Tagged) -> bool:
        """Evaluate the expression for the specified object."""
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class TagExpr(BoolExpr):
    """A tag to be checked against obj.tags."""

    tag: str
    """The tag to be matched exactly against the object's list of tags."""

    def evaluate(self, obj: defs.TaggedFrozen | defs.Tagged) -> bool:
        """Check whether the tag is present in the object's list of tags."""
        return self.tag in obj.tags


@dataclasses.dataclass(frozen=True)
class KeywordExpr(BoolExpr):
    """A tag to be checked against an object's name or list of tags."""

    keyword: str
    """The keyword to be matched as a substring of the object's keywords."""

    def evaluate(self, obj: defs.TaggedFrozen | defs.Tagged) -> bool:
        """Check whether the tag is present in the object's list of tags."""
        return any(self.keyword in item for item in obj.get_keyword_haystacks())


@dataclasses.dataclass(frozen=True)
class NotExpr(BoolExpr):
    """A negated boolean expression."""

    child: BoolExpr
    """The expression to be negated."""

    def evaluate(self, obj: defs.TaggedFrozen | defs.Tagged) -> bool:
        """Check whether the specified expression does not hold true."""
        return not self.child.evaluate(obj)


@dataclasses.dataclass(frozen=True)
class AndExpr(BoolExpr):
    """An "atom and atom [and atom...]" subexpression."""

    children: list[BoolExpr]
    """The subexpressions to be combined."""

    def evaluate(self, obj: defs.TaggedFrozen | defs.Tagged) -> bool:
        """Check whether all the specified expressions hold true."""
        return all(child.evaluate(obj) for child in self.children)


@dataclasses.dataclass(frozen=True)
class OrExpr(BoolExpr):
    """An "subexpr or subexpr [or subexpr...]" subexpression."""

    children: list[BoolExpr]
    """The subexpressions to be combined."""

    def evaluate(self, obj: defs.TaggedFrozen | defs.Tagged) -> bool:
        """Check whether any of the specified expressions hold(s) true."""
        return any(child.evaluate(obj) for child in self.children)
