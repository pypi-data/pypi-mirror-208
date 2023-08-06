# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

{ pkgs ? import <nixpkgs> { }
, py-ver ? 311
}:
let
  python-name = "python${toString py-ver}";
  python = builtins.getAttr python-name pkgs;
  python-pkgs = python.withPackages (p: with p; [ pyparsing pytest ]);
in
pkgs.mkShell {
  buildInputs = [ python-pkgs ];
  shellHook = ''
    set -e
    PYTHONPATH="$(pwd)/src" python3 -m pytest -v unit_tests
    exit
  '';
}
