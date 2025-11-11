{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
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
        packages.default = pkgs.callPackage ./nix/package.nix { };

        devShell = pkgs.mkShell {
          buildInputs = with pkgs.python3Packages; [
            python
            pytest

            pytest-cov-stub
            typeguard
            enlighten

            beets-minimal
          ];
        };
      }
    );
}
