#!/usr/bin/env python3
"""Smoke test to verify that the packaged Antigravity IDE launches cleanly inside its FHS environment."""

import os
import select
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
    env["ELECTRON_ENABLE_LOGGING"] = "1"

    proc = subprocess.Popen(
        [str(BINARY), "--no-sandbox", "--disable-gpu"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
        start_new_session=True,
    )

    found = False
    start_time = time.time()
    collected_output = []

    try:
        while time.time() - start_time < 15:
            # Use non-blocking select with 1s timeout to prevent hanging on pipes
            rlist, _, _ = select.select([proc.stdout], [], [], 1.0)
            if rlist:
                line = proc.stdout.readline()
                if line:
                    stripped = line.rstrip()
                    collected_output.append(stripped)
                    print(f"[ide] {stripped}", flush=True)
                    if "Browser onboarding server started" in stripped or "Starting browser onboarding" in stripped:
                        found = True
                        break
            if proc.poll() is not None:
                break
    finally:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=3)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    if found:
        print("\n✅ Antigravity IDE runtime smoke test passed: Electron and FHS initialized successfully.", flush=True)
        sys.exit(0)
    else:
        print("\n❌ Antigravity IDE failed to start properly within timeout.", file=sys.stderr, flush=True)
        print("Collected logs:", file=sys.stderr)
        for line in collected_output[-30:]:
            print(f"  {line}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
