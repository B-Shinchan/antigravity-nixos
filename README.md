# Google Antigravity IDE on NixOS & Flakes

<p align="center">
  <img src="assets/antigravity.png" alt="Google Antigravity IDE" width="128" height="128">
</p>

<p align="center">
  <strong>Production-grade Nix packaging of Google's agent-first development environment built on VS Code.</strong>
</p>

<p align="center">
  <a href="https://github.com/B-Shinchan/antigravity-nixos/actions/workflows/ci.yml"><img src="https://github.com/B-Shinchan/antigravity-nixos/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
  <a href="https://github.com/B-Shinchan/antigravity-nixos/releases"><img src="https://img.shields.io/github/v/release/B-Shinchan/antigravity-nixos?include_prereleases&sort=semver&logo=google" alt="Latest Release"></a>
  <a href="https://builtwithnix.org"><img src="https://builtwithnix.org/badge.svg" alt="Built With Nix"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue.svg" alt="License"></a>
</p>

---

## 🌟 Features

- 🚀 **Official Google CDN Upstream:** Directly tracks Google's official edge releases (`https://edgedl.me.gvt1.com`).
- 🤖 **Agent-First Workflow:** Full Google Antigravity IDE features out-of-the-box (autonomous agent execution, inline AI generation `Ctrl+I`, workspace browser, terminal assistance, code lenses).
- 📦 **Nixpkgs FHS Integration:** Wrapped inside a hardened FHS bubblewrap sandbox—pre-compiled language servers (Python pyright/pylance, Rust rust-analyzer, Go gopls, C/C++ clangd, Node) and VS Code extensions run seamlessly with zero ELF patching.
- 🎨 **Wayland & X11 Auto-Detection:** Automatically leverages native Wayland under compositors like GNOME, Niri, Hyprland, and Sway via `--ozone-platform-hint=auto`.
- 🔄 **Fully Automated Upstream CI/CD:** Scheduled GitHub Actions poll Google's official manifest every 6 hours, verify SRI hashes, test builds, and release updates automatically.
- 💻 **Cross-Platform:** Supports `x86_64-linux`, `aarch64-linux`, `x86_64-darwin`, and `aarch64-darwin`.

---

## 🚀 Quick Start (No Installation Needed)

Launch Antigravity IDE immediately using Nix Flakes:

```bash
nix run github:B-Shinchan/antigravity-nixos
```

Or test a specific file or workspace directory:

```bash
nix run github:B-Shinchan/antigravity-nixos -- ~/my-project
```

---

## 📥 Installation

### Option 1: NixOS Flake Configuration

Add `antigravity-nixos` to your `/etc/nixos/flake.nix`:

```nix
{
  description = "NixOS Configuration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    antigravity-nixos.url = "github:B-Shinchan/antigravity-nixos";
  };

  outputs = { self, nixpkgs, antigravity-nixos, ... }@inputs: {
    nixosConfigurations.myhostname = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix

        # Method A: Use the included NixOS module
        antigravity-nixos.nixosModules.default
        {
          programs.antigravity-ide.enable = true;
        }

        # OR Method B: Add directly to systemPackages
        # ({ pkgs, ... }: {
        #   environment.systemPackages = [
        #     inputs.antigravity-nixos.packages.${pkgs.system}.default
        #   ];
        # })
      ];
    };
  };
}
```

Then rebuild your system:

```bash
sudo nixos-rebuild switch --flake /etc/nixos#myhostname
```

---

### Option 2: Home Manager (Flakes)

In your `home.nix`:

```nix
{ pkgs, inputs, ... }:

{
  # Method A: Direct package inclusion
  home.packages = [
    inputs.antigravity-nixos.packages.${pkgs.system}.default
  ];

  # OR Method B: Home Manager module
  # imports = [ inputs.antigravity-nixos.homeManagerModules.default ];
  # programs.antigravity-ide.enable = true;
}
```

---

### Option 3: Traditional Nix (Non-Flakes)

You can install `antigravity-ide` directly into your user environment without flakes:

```bash
nix-env -i -f "https://github.com/B-Shinchan/antigravity-nixos/archive/main.tar.gz"
```

Or enter a temporary development shell:

```bash
nix-shell -p '(import (fetchTarball "https://github.com/B-Shinchan/antigravity-nixos/archive/main.tar.gz")).packages.x86_64-linux.default' --run antigravity-ide
```

---

## 🧩 Overlay Usage

You can easily overlay Antigravity IDE into `pkgs`:

```nix
{
  nixpkgs.overlays = [
    inputs.antigravity-nixos.overlays.default
  ];
}
```

This makes `pkgs.antigravity-ide` available in standard package lists.

---

## 🔍 Antigravity IDE vs. Antigravity Hub

Google provides two distinct applications under the Antigravity brand:

- **Google Antigravity IDE** (this repository): Google's agent-first code editor built on VS Code. Executable: `antigravity-ide`.
- **Google Antigravity Hub**: Google's standalone agent orchestration mission control and command center. Executable: `antigravity-hub`. Packaged separately at [B-Shinchan/antigravity-hub-nixos](https://github.com/B-Shinchan/antigravity-hub-nixos).

Both applications can be installed and executed simultaneously on the same machine without window, dock, or state collisions.

---

## 🤖 Companion Applications

This package is part of a suite of official vendor AI applications packaged for NixOS:

| Application | Command | Repository |
| :--- | :--- | :--- |
| **Google Antigravity IDE** | `antigravity-ide` | [antigravity-nixos](https://github.com/B-Shinchan/antigravity-nixos) |
| **Google Antigravity Hub** | `antigravity-hub` | [antigravity-hub-nixos](https://github.com/B-Shinchan/antigravity-hub-nixos) |
| **ChatGPT Desktop** | `chatgpt` | [chatgpt-desktop-nixos](https://github.com/B-Shinchan/chatgpt-desktop-nixos) |
| **Claude Desktop** | `claude-desktop` | [claude-desktop-nixos](https://github.com/B-Shinchan/claude-desktop-nixos) |

---

## ⚙️ Repository Layout

```text
antigravity-nixos/
├── .github/
│   └── workflows/
│       ├── ci.yml            # CI build & flake evaluation
│       └── update.yml        # Scheduled Google edge release tracker
├── assets/
│   ├── antigravity.png       # 1024x1024 official high-resolution icon
│   ├── antigravity.svg       # Vector icon
│   └── antigravity-ide.desktop   # FreeDesktop application desktop entry
├── pkgs/
│   └── antigravity-ide/
│       ├── default.nix       # Primary Nix expression (FHS sandbox wrapper)
│       └── sources.json      # Pinned version, CDN URLs, and SRI hashes
├── scripts/
│   └── update.py             # Automated updater for Google CDN releases
├── flake.nix                 # Flake entry point (packages, apps, modules, overlays)
├── flake.lock                # Pinned nixpkgs inputs
├── LICENSE                   # Apache-2.0 License
└── README.md                 # Documentation
```

---

## 🛠️ Automated Maintenance

This repository requires zero manual version bumping:

1. **Automated Discovery:** A GitHub Actions cron job triggers every 6 hours (`.github/workflows/update.yml`) and runs `python3 scripts/update.py`.
2. **Decompressed Stream Hashing:** The updater queries `https://antigravity.google/download`, identifies new builds, streams the binaries from `https://edgedl.me.gvt1.com`, and calculates SRI SHA-256 hashes.
3. **Verification:** The CI runner builds the flake locally to guarantee derivation health.
4. **Automated Tag & Release:** On success, a new version commit, Git tag, and GitHub Release are generated.

To manually trigger a release check locally:

```bash
python3 scripts/update.py --dry-run
```

---

## 📄 License

Packaging code, derivations, and configurations are licensed under the [Apache License 2.0](LICENSE).  
Google Antigravity IDE and all associated trademarks and proprietary assets are the property of Google LLC.
