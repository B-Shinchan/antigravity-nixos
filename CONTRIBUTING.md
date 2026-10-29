# Contributing to Google Antigravity IDE NixOS Packaging

Thank you for helping maintain and improve the Google Antigravity IDE package for NixOS!

---

## Local Development & Testing

Before submitting a Pull Request, verify that all flake checks pass:

```bash
# 1. Run all Flake checks
nix flake check --print-build-logs

# 2. Build the package
nix build .#default --print-build-logs

# 3. Test updater script in dry-run mode
python3 scripts/update.py --dry-run

# 4. Run test suite
python3 -m unittest discover -s tests -v
```

---

## Guidelines

1. **Clean Separation**: Antigravity IDE is the code editor (`antigravity-ide`). It must never overwrite or collide with Antigravity Hub (`antigravity-hub`).
2. **Upstream Sources**: Hashes and platform URLs are tracked in `pkgs/antigravity-ide/sources.json`. Automated daily updates manage this file automatically.
3. **FHS Environment**: The application wraps VS Code and requires the FHS sandbox (`buildFHSEnv`) to ensure language server tools and extensions execute reliably.

---

## Upstream References

- Google Antigravity Official Site: <https://antigravity.google>
- Download Page: <https://antigravity.google/download>
- Nixpkgs Manual & Guidelines: <https://nixos.org/manual/nixpkgs/unstable/>
