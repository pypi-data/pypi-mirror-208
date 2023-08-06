<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# The Specification Mini-Language

## Grouping stages for step-by-step execution

The specification mini-language may roughly be described as:

    expr ::= and_expr ["or" and_expr...]
    and_expr ::= not_expr ["and" not_expr...]
    not_expr ::= ["not"] atom
    atom ::= tag | keyword
    tag ::= "@" characters
    keyword ::= characters
    characters ::= [A-Za-z0-9_-]+

Thus, all of the following:

- `@check`
- `@check and @quick`
- `@tests and not examples`
- `not @tests`
- `pep8 or not @quick and @check`

...are valid expressions,
with the "not", "and", and "or" keywords having their usual precedence
(`pep8 or not @quick and @check` is parsed as
`pep8 or ((@not quick) and @check)`, but the mini-language does not
support parentheses yet).
