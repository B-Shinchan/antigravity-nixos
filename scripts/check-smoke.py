#!/usr/bin/env python3
"""Smoke test to verify that the packaged Antigravity IDE launches cleanly inside its FHS environment."""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "result" / "bin" / "antigravity-ide"


def main():
    if not BINARY.exists():
        print(f"Error: Binary {BINARY} does not exist. Run 'nix build' first.", file=sys.stderr)
        sys.exit(1)

    print(f"Executing runtime smoke test for: {BINARY}")
    env = os.environ.copy()
    # In headless CI or headless runner, disable gpu and set no-sandbox if needed
    proc = subprocess.Popen(
        [str(BINARY), "--no-sandbox", "--disable-gpu"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        start_new_session=True,
    )

    found = False
    start_time = time.time()
    collected_output = []

    try:
        # Give up to 20 seconds for the Electron onboarding server to announce itself
        while time.time() - start_time < 20:
            line = proc.stdout.readline()
            if line:
                collected_output.append(line.rstrip())
                print(f"[ide] {line.rstrip()}")
                if "Browser onboarding server started" in line or "Starting browser onboarding" in line:
                    found = True
                    break
            if proc.poll() is not None:
                break
            time.sleep(0.05)
    finally:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=5)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    if found:
        print("\n✅ Antigravity IDE runtime smoke test passed: Electron and FHS initialized successfully.")
        sys.exit(0)
    else:
        print("\n❌ Antigravity IDE failed to start properly within timeout.", file=sys.stderr)
        print("Collected logs:", file=sys.stderr)
        for line in collected_output[-30:]:
            print(f"  {line}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
