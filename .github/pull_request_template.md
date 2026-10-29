## Summary of Changes

Describe the problem solved or the feature/improvement introduced.

## Motivation & Context

Why is this change necessary? Link to any relevant issue (`Fixes #...`).

## Pre-submission Checklist

- [ ] Evaluated and passed local flake checks: `nix flake check --print-build-logs`
- [ ] Successfully built the derivation locally: `nix build .#default`
- [ ] Ran updater test suite: `python3 -m unittest discover -s tests -v`
- [ ] Verified dry-run update check: `python3 scripts/update.py --dry-run`
- [ ] Preserved FHS bubblewrap sandbox isolation for language servers and extensions
- [ ] Maintained strict separation between `antigravity-ide` and `antigravity-hub`
- [ ] No hardcoded user paths or machine-specific assumptions introduced
