{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs.python3Packages; [
            python
            pytest
            isort
            black

            pytest-cov-stub
            mock
            pillow
            tomli
            typeguard
            enlighten

            pkgs.beetsPackages.beets-minimal
          ];
        };
      }
    );
}
