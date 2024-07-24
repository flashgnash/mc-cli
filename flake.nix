# file: flake.nix
{
  description = "Macros for dragon block C";


  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, poetry2nix }:
    let
      system = "x86_64-linux";

      pkgs = nixpkgs.legacyPackages.${system};
      # create a custom "mkPoetryApplication" API function that under the hood uses
      # the packages and versions (python3, poetry etc.) from our pinned nixpkgs above:
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      myPythonApp = mkPoetryApplication { projectDir = ./.; };
    in
    {
      apps.${system} = {
        default = {
          type = "app";
          # replace <script> with the name in the [tool.poetry.scripts] section of your pyproject.toml
          program = "${myPythonApp}/bin/mc-installer";
        };      
      };
           
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          nodePackages.prettier
          poetry

          linuxHeaders

          jre8
        ];
      };
      
    };
}
