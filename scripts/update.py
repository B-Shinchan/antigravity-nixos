#!/usr/bin/env python3
"""Automated updater for Google Antigravity IDE packages.

Fetches the official Google download manifest, extracts version metadata
and edge delivery download URLs, calculates SRI hashes, and updates sources.json.
"""

import argparse
import base64
import gzip
import hashlib
import json
import os
import re
import sys
import urllib.request
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / "pkgs" / "antigravity-ide" / "sources.json"
DOWNLOAD_PAGE = "https://antigravity.google/download"

PLATFORMS = {
    "x86_64-linux": "linux-x64/Antigravity%20IDE.tar.gz",
    "aarch64-linux": "linux-arm/Antigravity%20IDE.tar.gz",
    "x86_64-darwin": "darwin-x64/Antigravity%20IDE.dmg",
    "aarch64-darwin": "darwin-arm/Antigravity%20IDE.dmg",
}

EDGE_PATTERN = re.compile(
    r"https://edgedl\.me\.gvt1\.com/edgedl/release2/j0qc3/antigravity/stable/([0-9.]+)-([0-9]+)/"
)


def fetch_page(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
            "Accept-Encoding": "gzip, deflate",
        },
    )
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
        encoding = resp.info().get("Content-Encoding")
        if encoding == "gzip":
            content = gzip.decompress(content)
        elif encoding == "deflate":
            content = zlib.decompress(content)
        return content.decode("utf-8", errors="replace")


def calculate_sri_hash(url: str) -> str:
    print(f"Streaming and calculating SHA-256 for: {url}")
    hasher = hashlib.sha256()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
        },
    )
    with urllib.request.urlopen(req) as resp:
        while chunk := resp.read(1024 * 1024):
            hasher.update(chunk)
    return "sha256-" + base64.b64encode(hasher.digest()).decode("utf-8")


def get_latest_release():
    html = fetch_page(DOWNLOAD_PAGE)
    matches = EDGE_PATTERN.findall(html)
    if not matches:
        raise RuntimeError("Failed to find Google edge delivery URLs on download page")

    # Find the version with the highest semver / build
    latest_version, latest_build = matches[0]
    for version, build in matches:
        if tuple(map(int, version.split("."))) > tuple(map(int, latest_version.split("."))):
            latest_version, latest_build = version, build

    return latest_version, latest_build


def update(dry_run: bool = False) -> bool:
    print(f"Fetching latest Antigravity IDE manifest from {DOWNLOAD_PAGE}...")
    latest_version, latest_build = get_latest_release()
    print(f"Detected latest upstream release: {latest_version} (build {latest_build})")

    current_sources = {}
    if SOURCES_FILE.exists():
        current_sources = json.loads(SOURCES_FILE.read_text())

    current_version = current_sources.get("version")
    current_build = current_sources.get("build")

    if current_version == latest_version and current_build == latest_build:
        print(f"Already up to date at version {latest_version} (build {latest_build}).")
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write("has_update=false\n")
        return False

    print(f"New version found: {current_version} -> {latest_version}")

    base_url = f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{latest_version}-{latest_build}"
    platforms_data = {}

    for platform_key, path in PLATFORMS.items():
        platform_url = f"{base_url}/{path}"
        sri_hash = calculate_sri_hash(platform_url)
        platforms_data[platform_key] = {
            "url": platform_url,
            "hash": sri_hash,
        }

    new_sources = {
        "version": latest_version,
        "build": latest_build,
        "platforms": platforms_data,
    }

    if not dry_run:
        SOURCES_FILE.parent.mkdir(parents=True, exist_ok=True)
        SOURCES_FILE.write_text(json.dumps(new_sources, indent=2) + "\n")
        print(f"Successfully wrote updated metadata to {SOURCES_FILE}")

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write("has_update=true\n")
            f.write(f"version={latest_version}\n")
            f.write(f"build={latest_build}\n")

    return True


def main():
    parser = argparse.ArgumentParser(description="Update Antigravity IDE package sources")
    parser.add_argument("--dry-run", action="store_true", help="Check for updates without modifying files")
    args = parser.parse_args()

    update(dry_run=args.dry_run)
    sys.exit(0)


if __name__ == "__main__":
    main()
