{
  description = "Python Click CLI development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { nixpkgs, ... }:
    let
      systems = [
        "aarch64-darwin"
        "aarch64-linux"
        "x86_64-darwin"
        "x86_64-linux"
      ];

      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
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
        {
          default = pkgs.mkShell {
            packages = [
              devAgent
              pythonEnv
            ];

            shellHook = ''
              export PYTHONPATH="$PWD/src''${PYTHONPATH:+:$PYTHONPATH}"
              echo "Python Click CLI dev shell ready"
              echo "Try: dev-agent --help"
            '';
          };
        }
      );

      formatter = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        pkgs.nixfmt-rfc-style
      );
    };
}
