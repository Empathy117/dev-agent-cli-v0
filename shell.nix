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
  devAgent = pkgs.writeShellApplication {
    name = "dev-agent";
    runtimeInputs = [
      pythonEnv
    ];
    text = ''
      export PYTHONPATH="$PWD/src''${PYTHONPATH:+:$PYTHONPATH}"
      exec python -m dev_agent_cli "$@"
    '';
  };
in
pkgs.mkShell {
  packages = [
    devAgent
    pythonEnv
  ];

  shellHook = ''
    export PYTHONPATH="$PWD/src''${PYTHONPATH:+:$PYTHONPATH}"
    echo "Python Click CLI dev shell ready"
    echo "Try: dev-agent --help"
  '';
}
