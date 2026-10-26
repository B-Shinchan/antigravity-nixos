{
  description = "Always-up-to-date Nix Flake packaging of Google's official Antigravity IDE";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];

      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;

      nixpkgsFor = forAllSystems (
        system:
        import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [ self.overlays.default ];
        }
      );
    in
    {
      overlays.default = final: prev: {
        antigravity-ide = final.callPackage ./pkgs/antigravity-ide { };
        antigravity = final.antigravity-ide;
      };

      packages = forAllSystems (system: {
        default = nixpkgsFor.${system}.antigravity-ide;
        antigravity-ide = nixpkgsFor.${system}.antigravity-ide;
        antigravity = nixpkgsFor.${system}.antigravity;
      });

      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = "${self.packages.${system}.antigravity-ide}/bin/antigravity-ide";
          meta = {
            description = "Google Antigravity IDE";
          };
        };
      });

      checks = forAllSystems (system: {
        updater = nixpkgsFor.${system}.runCommand "updater-tests" {
          nativeBuildInputs = [ nixpkgsFor.${system}.python3 ];
        } ''
          cp -r ${./tests} ./tests
          cp -r ${./scripts} ./scripts
          cp -r ${./pkgs} ./pkgs
          python3 -m unittest discover -s tests -v
          touch $out
        '';
      });

      nixosModules.default =
        {
          config,
          lib,
          pkgs,
          ...
        }:
        let
          cfg = config.programs.antigravity-ide;
        in
        {
          options.programs.antigravity-ide = {
            enable = lib.mkEnableOption "Google Antigravity IDE";
            package = lib.mkPackageOption pkgs "antigravity-ide" {
              default = [ "antigravity-ide" ];
            };
          };

          config = lib.mkIf cfg.enable {
            nixpkgs.overlays = [ self.overlays.default ];
            environment.systemPackages = [ cfg.package ];
          };
        };

      homeManagerModules.default =
        {
          config,
          lib,
          pkgs,
          ...
        }:
        let
          cfg = config.programs.antigravity-ide;
        in
        {
          options.programs.antigravity-ide = {
            enable = lib.mkEnableOption "Google Antigravity IDE";
            package = lib.mkPackageOption pkgs "antigravity-ide" {
              default = [ "antigravity-ide" ];
            };
          };

          config = lib.mkIf cfg.enable {
            home.packages = [ cfg.package ];
          };
        };
    };
}
