import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import update


MOCK_HTML_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Antigravity Download</title></head>
<body>
<a href="https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.5.4-4800000000000000/linux-x64/Antigravity%20IDE.tar.gz">Older</a>
<a href="https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.5.5-4923483625488384/linux-x64/Antigravity%20IDE.tar.gz">Linux x64</a>
<a href="https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.5.5-4923483625488384/linux-arm/Antigravity%20IDE.tar.gz">Linux ARM</a>
<a href="https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.5.5-4923483625488384/darwin-x64/Antigravity%20IDE.dmg">macOS x64</a>
<a href="https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.5.5-4923483625488384/darwin-arm/Antigravity%20IDE.dmg">macOS ARM</a>
</body>
</html>
"""

MOCK_HTML_NEWER = """
<!DOCTYPE html>
<html>
<body>
<a href="https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.6.0-5000000000000000/linux-x64/Antigravity%20IDE.tar.gz">Linux x64</a>
</body>
</html>
"""


class TestAntigravityUpdater(unittest.TestCase):

    def test_version_extraction_picks_highest(self):
        with patch("update.fetch_page", return_value=MOCK_HTML_PAGE):
            ver, build = update.get_latest_release()
            self.assertEqual(ver, "2.5.5")
            self.assertEqual(build, "4923483625488384")

    def test_version_extraction_newer_release(self):
        with patch("update.fetch_page", return_value=MOCK_HTML_NEWER):
            ver, build = update.get_latest_release()
            self.assertEqual(ver, "2.6.0")
            self.assertEqual(build, "5000000000000000")

    def test_malformed_page_raises_error(self):
        with patch("update.fetch_page", return_value="<html><body>No links here</body></html>"):
            with self.assertRaises(RuntimeError) as ctx:
                update.get_latest_release()
            self.assertIn("Failed to find Google edge delivery URLs", str(ctx.exception))

    def test_update_already_up_to_date(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_sources = Path(tmpdir) / "sources.json"
            tmp_sources.write_text(json.dumps({"version": "2.5.5", "build": "4923483625488384"}))
            with patch("update.SOURCES_FILE", tmp_sources), \
                 patch("update.fetch_page", return_value=MOCK_HTML_PAGE):
                has_update = update.update(dry_run=True)
                self.assertFalse(has_update)

    def test_update_applies_new_version(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_sources = Path(tmpdir) / "sources.json"
            tmp_sources.write_text(json.dumps({"version": "2.5.5", "build": "4923483625488384"}))
            with patch("update.SOURCES_FILE", tmp_sources), \
                 patch("update.fetch_page", return_value=MOCK_HTML_NEWER), \
                 patch("update.calculate_sri_hash", return_value="sha256-mockHash=="):
                has_update = update.update(dry_run=False)
                self.assertTrue(has_update)
                updated = json.loads(tmp_sources.read_text())
                self.assertEqual(updated["version"], "2.6.0")
                self.assertEqual(updated["build"], "5000000000000000")
                self.assertIn("x86_64-linux", updated["platforms"])
                self.assertEqual(updated["platforms"]["x86_64-linux"]["hash"], "sha256-mockHash==")


if __name__ == "__main__":
    unittest.main()
