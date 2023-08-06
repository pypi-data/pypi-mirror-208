<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Changelog

All notable changes to the parse-stages project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2023-05-13

### Additions

- Documentation:
    - add a [ReadTheDocs mirror](https://parse-stages.readthedocs.io/)
- Main source:
    - `parse_stage_ids()`: allow an empty set to be specified by the exact
      strings "", "0", or "none"

### Other changes

- Build system:
    - drop the obsolete `tool.setuptools.*` sections from the `pyproject.toml` file
- Documentation:
    - bump the version of `mkdocstrings-python` with no changes
- Test suite:
    - Ruff:
        - use Ruff 0.0.267, enable the `FLY` checks area

## [0.1.3] - 2023-05-07

### Fixes

- Add a blank line to a docstring section (ruff D214).
- Drop the text in a `NotImplementedError` raised in an abstract method;
  it should be obvious (ruff EM101)

### Additions

- Add a `.gitignore` file, mostly so that `reuse` can be run at any time
- Add a "Home, GitLab, PyPI" navigational line to the documentation
  index page and to the `README.md` file

### Other changes

- Main source:
    - reformat the import sections using Ruff's `isort` implementation
- Build system:
    - switch to `hatch` / `hatchling` for the PEP517 build
- Documentation:
    - use the `default_handler` configuration option of `mkdocstrings`
      instead of specifying `handler: python` for each class!
    - bump the versions of `mkdocstrings` and `mkdocstrings-python` with
      no changes
- Test suite:
    - specify 4.1 as the Tox minimum version and switch to the Tox 4.x
      format for the multiline list of files
    - rename the `black` Tox environment to `format` and
      the `black-reformat` one to `reformat`, since they also run
      Ruff's `isort` now
    - Ruff:
        - use Ruff 0.0.265, enable the `INT` checks area although
          we do not use gettext
        - enable all ruff check areas in `config/ruff-most/`, let
          the `config/ruff-base/` files take care of the ignored ones
        - no longer disable the "relative imports" check, it does not
          complain about our source code
    - Pylint:
        - reenable the "empty comment" plugin; we should have no
          trouble with it since switching to SPDX license tags
    - Bump the versions of `flake8-implicit-str-concat`, `flake8-simplify`,
      `pylint`, and `triceratops` with no code changes

## [0.1.2] - 2023-03-10

### Semi-incompatible changes

- Drop Python 3.7 support.

### Fixes

- Fix the 0.1.1 release URL in the changelog file.
- Do not run the `pyupgrade` Tox environment automatically.
- Add a docstring to the unit test suite's `__init__.py` file instead of
  overriding a linter check.

### Additions

- Start some MkDocs-based documentation.
- Add the `reuse` Tox test environment to run the REUSE tool manually.

### Other changes

- Rework the Ruff invocation Tox targets a bit:
    - drop the `ruff-all-unchained` test environment; at this point in
      Ruff's development we are bound to specific versions anyway
    - move the config files to a `config/` directory, not `.config/`
    - move the "normal" Ruff invocation configuration to `config/ruff-most/`
    - use Ruff 0.0.254 with no code changes
    - activate all of Ruff 0.0.254's liners in the "normal" invocation
- Switch to SPDX license tags.
- Specify the supported Python version in the configuration of the pylint and
  black tools.
- Move the changelog file into the documentation directory.
- In the packaging metadata, point to the Ringlet homepage generated from
  the newly-added documentation.

## [0.1.1] - 2023-02-05

### Fixes

- Use "precedence" instead of "priority" when discussing operators in
  the README file.
- Do not use the `list` generic type in the definition of the `TaggedFrozen` and
  `Tagged` classes; library consumers may try to use `typing.get_type_hints()` on
  them or on derived classes, and Python < 3.9 would have a problem with that.
- Fill in the module docstring using the text of the README file.
- Fix some problems reported by `ruff`:
    - fix the order of some `import` statements
    - fix the formatting of some docstrings

### Other changes

- Add the `ruff-all` test environment that enables all the checks of the `ruff`
  tool for a certain locked version of `ruff`.
- Add the `tool.test-stages` section in the `pyproject.toml` file to specify
  the order that Tox environments should be run during development using
  the `tox-stages` tool from the `test-stages` Python library.
- Add a lot of `flake8` plugins to the Tox `pep8` test environment
- Use ruff 0.0.241, pylint 2.16.x, and black 23.x.

## [0.1.0] - 2023-01-25

### Started

- First public release.

[Unreleased]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.4...main
[0.1.4]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.3...release%2F0.1.4
[0.1.3]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.2...release%2F0.1.3
[0.1.2]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.1...release%2F0.1.2
[0.1.1]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.0...release%2F0.1.1
[0.1.0]: https://gitlab.com/ppentchev/parse-stages/-/tags/release%2F0.1.0
