# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

{ pkgs ? import <nixpkgs> { }
, py-ver ? 311
}:
let
  python-name = "python${toString py-ver}";
  python = builtins.getAttr python-name pkgs;
  python-pkgs = python.withPackages (p: with p;
    [
      mkdocs
      mkdocs-material
      mkdocstrings
      mkdocstrings-python
    ]
  );
in
pkgs.mkShell {
  buildInputs = [ python-pkgs ];
  shellHook = ''
    set -e
    rm -rf site
    mkdocs build
    exit
  '';
}
