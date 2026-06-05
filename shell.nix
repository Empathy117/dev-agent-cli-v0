{ pkgs ? import <nixpkgs> { } }:

let
  python = pkgs.python312;
  pythonEnv = python.withPackages (
    ps: with ps; [
      build
      click
      pip
      pytest
      ruff
      setuptools
      wheel
    ]
  );
in
pkgs.mkShell {
  packages = [
    pythonEnv
  ];

  shellHook = ''
    export PYTHONPATH="$PWD/src''${PYTHONPATH:+:$PYTHONPATH}"
    echo "Python Click CLI dev shell ready"
    echo "Try: python -m dev_agent_cli --help"
  '';
}
