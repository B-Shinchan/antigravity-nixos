# Security Policy

## Supported Versions

Only the latest release published on the `main` branch of this repository is supported.

| Version | Supported |
| :--- | :--- |
| Latest `main` release | :white_check_mark: |
| Older commits | :x: |

---

## Reporting a Vulnerability

If you discover a security vulnerability in this repository:

1. **Do not create a public issue**.
2. Open a private [Security Advisory](https://github.com/B-Shinchan/antigravity-nixos/security/advisories/new) on GitHub or contact the maintainer directly.
3. Include details of the vulnerability, reproduction steps, and any potential impact.

---

## Binary Provenance & Verification

- Binaries are downloaded exclusively from official Google release CDNs (`https://edgedl.me.gvt1.com/edgedl/release2/...`).
- Downloads are verified using SHA-256 SRI hashes recorded in `pkgs/antigravity-ide/sources.json`.
- Sandboxing is enforced at runtime via bubblewrap (`buildFHSEnv`).
