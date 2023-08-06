#!/bin/sh
#
# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

set -e

cleanpy()
{
	find . -mindepth 1 -maxdepth 1 -type d \( \
		-name '.tox' \
		-or -name '.mypy_cache' \
		-or -name '.pytest_cache' \
		-or -name '.nox' \
		-or -name '.ruff_cache' \
	\) -exec rm -rf -- '{}' +
	find . -type d -name '__pycache__' -exec rm -rfv -- '{}' +
	find . -type f -name '*.pyc' -delete -print
	find . -mindepth 1 -maxdepth 2 -type d -name '*.egg-info' -exec rm -rfv -- '{}' +
}

for pyver in 38 39 310 311 312; do
	cleanpy
	printf -- '\n===== Running tests for %s\n\n\n' "$pyver"
	nix-shell --pure --arg py-ver "$pyver" nix/python-pytest.nix
	printf -- '\n===== Done with %s\n\n' "$pyver"
done
