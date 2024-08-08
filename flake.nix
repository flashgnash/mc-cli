{
  description = "Minecraft server installer CLI";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, poetry2nix }: let
    systems = [ "x86_64-linux" "aarch64-linux" ];
    forAllSystems = f: builtins.listToAttrs (map (system: { name = system; value = f system; }) systems);

    mkPoetryAppFor = system: let
      pkgs = nixpkgs.legacyPackages.${system};
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
    in
      mkPoetryApplication { projectDir = ./.; };

    appsFor = system: {
      default = {
        type = "app";
        program = "${mkPoetryAppFor system}/bin/mc-installer";
      };
    };

    devShellFor = system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in pkgs.mkShell {
      packages = with pkgs; [
        nodePackages.prettier
        poetry
        python312Packages.pip
        linuxHeaders
        jre8
      ];
    };
  in
  {
    packages = forAllSystems (system: mkPoetryAppFor system);
    apps = forAllSystems appsFor;
    devShells = forAllSystems (system: {
      default = devShellFor system;
    });
  };
}
