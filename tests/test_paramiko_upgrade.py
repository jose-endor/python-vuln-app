"""Regression tests for the paramiko 3.5.1 upgrade (GHSA-45x7-px36-x8w8)."""
from __future__ import annotations

import os
import tempfile
import unittest
from importlib import metadata
from pathlib import Path

# Repo root so tests can read the pin without depending on cwd.
ROOT = Path(__file__).resolve().parents[1]


class ParamikoPinTests(unittest.TestCase):
    def test_requirements_pins_paramiko_3_5_1(self) -> None:
        # Direct pin is the UIA-selected fix; keep it from drifting back to 2.12.0.
        text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^paramiko==3\.5\.1$")

    def test_installed_paramiko_meets_fixed_version(self) -> None:
        # Fail if the active env still has the vulnerable 2.x series.
        parts = metadata.version("paramiko").split(".")
        installed = tuple(int(p) for p in parts[:3])
        self.assertGreaterEqual(installed, (3, 5, 1))


class ParamikoHostKeyTests(unittest.TestCase):
    def test_paramiko_host_key_returns_hex_fingerprint(self) -> None:
        # Call site used by GET /integrations/run?k=sftp_host_key.
        from bookstore.services.vendor_adapters import paramiko_host_key

        fingerprint = paramiko_host_key()
        # Adapter returns the first 20 chars of the MD5 fingerprint hex.
        self.assertEqual(len(fingerprint), 20)
        self.assertRegex(fingerprint, r"^[0-9a-f]{20}$")

    def test_rsa_key_generate_and_fingerprint_survive_major_bump(self) -> None:
        # paramiko 3.x still exposes the RSAKey APIs the adapter calls.
        import paramiko

        key = paramiko.RSAKey.generate(1024)
        digest = key.get_fingerprint()
        self.assertTrue(hasattr(digest, "hex"))
        self.assertGreaterEqual(len(digest.hex()), 20)


class SftpHostKeyRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Isolate sqlite so create_app() does not touch the developer inventory db.
        cls._tmpdir = tempfile.TemporaryDirectory()
        os.environ["INVENTORY_DB_PATH"] = str(Path(cls._tmpdir.name) / "test.db")
        from bookstore.app import create_app

        cls.app = create_app()
        cls.app.config["TESTING"] = True

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmpdir.cleanup()

    def test_sftp_host_key_requires_staff(self) -> None:
        client = self.app.test_client()
        resp = client.get("/integrations/run?k=sftp_host_key")
        self.assertEqual(resp.status_code, 403)

    def test_sftp_host_key_returns_fingerprint_for_staff(self) -> None:
        client = self.app.test_client()
        # vendor_hooks.staff_session only checks session["role"] == "admin".
        with client.session_transaction() as sess:
            sess["role"] = "admin"
        resp = client.get("/integrations/run?k=sftp_host_key")
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload["k"], "sftp_host_key")
        self.assertRegex(payload["out"], r"^[0-9a-f]{20}$")


if __name__ == "__main__":
    unittest.main()
