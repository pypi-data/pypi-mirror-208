# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Common definitions for the parse-stages library."""

# Some of this library's consumers need to be able to use typedload on
# Python versions < 3.9, so we cannot use the generic types.
# pylint: disable=deprecated-typing-alias

import dataclasses
from typing import List


@dataclasses.dataclass(frozen=True)
class TaggedFrozen:
    """A base class for representing a constant object that has some tags."""

    name: str
    """The name of the object, e.g. the name of the Tox test environment."""

    tags: List[str]
    """The tags specified for this object."""

    def get_keyword_haystacks(self) -> List[str]:
        """Get the strings to look for keywords in.

        Default: the object's `name` attribute.
        """
        return [self.name]


@dataclasses.dataclass
class Tagged:
    """A base class for representing an object that has some tags."""

    name: str
    """The name of the object, e.g. the name of the Tox test environment."""

    tags: List[str]
    """The tags specified for this object."""

    def get_keyword_haystacks(self) -> List[str]:
        """Get the strings to look for keywords in.

        Default: the object's `name` attribute.
        """
        return [self.name]


VERSION = "0.1.4"
