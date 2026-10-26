#!/usr/bin/env python3
"""Smoke test to verify that the packaged Antigravity IDE launches cleanly inside its FHS environment."""

import os
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "result" / "bin" / "antigravity-ide"


def main():
    if not BINARY.exists():
        print(f"Error: Binary {BINARY} does not exist. Run 'nix build' first.", file=sys.stderr)
        sys.exit(1)

    # If running headless without DISPLAY or WAYLAND_DISPLAY, re-exec under xvfb-run if available
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    if not has_display:
        xvfb = shutil.which("xvfb-run")
        if xvfb:
            print("No active display detected; re-executing under xvfb-run...")
            dbus_conf = ROOT / "tests" / "dbus-session.conf"
            cmd = [xvfb, "-a"]
            if shutil.which("dbus-run-session") and dbus_conf.exists():
                cmd += ["dbus-run-session", f"--config-file={dbus_conf}", "--"]
            cmd += [sys.executable, str(Path(__file__).resolve())] + sys.argv[1:]
            sys.exit(subprocess.call(cmd))
        else:
            print("Error: Neither DISPLAY nor WAYLAND_DISPLAY is set, and xvfb-run is not installed.", file=sys.stderr)
            sys.exit(1)

    with tempfile.TemporaryDirectory(prefix="antigravity-smoke-") as temp_dir:
        temp_path = Path(temp_dir)
        user_data = temp_path / "user-data"
        extensions = temp_path / "extensions"
        user_data.mkdir(parents=True, exist_ok=True)
        extensions.mkdir(parents=True, exist_ok=True)

        env = os.environ.copy()
        env["ELECTRON_ENABLE_LOGGING"] = "1"
        env["DISABLE_UPDATE_CHECK"] = "1"
        if "XDG_RUNTIME_DIR" not in env or not Path(env["XDG_RUNTIME_DIR"]).exists():
            runtime_dir = temp_path / "runtime"
            runtime_dir.mkdir(parents=True, exist_ok=True)
            runtime_dir.chmod(0o700)
            env["XDG_RUNTIME_DIR"] = str(runtime_dir)

        print(f"Executing runtime smoke test for: {BINARY} on DISPLAY={env.get('DISPLAY', '<none>')}")
        proc = subprocess.Popen(
            [
                str(BINARY),
                "--no-sandbox",
                "--disable-gpu",
                f"--user-data-dir={user_data}",
                f"--extensions-dir={extensions}",
            ],
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
            # Poll for the onboarding server or Electron startup signal within 20s
            while time.time() - start_time < 20:
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
