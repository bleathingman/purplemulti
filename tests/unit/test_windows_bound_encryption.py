"""Password encryption sealed to the Windows account, and password checks for the lock screen."""

import json
import os
import tempfile
import unittest
from unittest import mock

from classes import account_manager as am
from classes import encryption
from classes.encryption import (
    HardwareDecryptionError,
    PasswordDecryptionError,
    PasswordEncryption,
    WindowsBoundPasswordEncryption,
)

SALT = "ab" * 32
ACCOUNTS = {"alice": {"username": "alice", "cookie": "secret-cookie", "note": "", "cookie_valid": None}}


class WindowsBoundEncryptionTests(unittest.TestCase):
    def test_round_trip_needs_the_password(self):
        sealed = WindowsBoundPasswordEncryption("correct password", SALT).encrypt_data({"a": 1})
        self.assertEqual(sealed["format"], encryption.WINDOWS_BOUND_FORMAT)
        self.assertNotIn("ciphertext", sealed)
        reader = WindowsBoundPasswordEncryption("correct password", SALT)
        self.assertEqual(reader.decrypt_data(sealed), {"a": 1})
        self.assertFalse(reader.needs_rewrite)
        with self.assertRaises(PasswordDecryptionError):
            WindowsBoundPasswordEncryption("wrong password", SALT).decrypt_data(sealed)

    def test_another_windows_account_cannot_open_it(self):
        sealed = WindowsBoundPasswordEncryption("correct password", SALT).encrypt_data({"a": 1})
        with mock.patch.object(encryption.win32crypt, "CryptUnprotectData", side_effect=OSError("denied")):
            with self.assertRaises(HardwareDecryptionError):
                WindowsBoundPasswordEncryption("correct password", SALT).decrypt_data(sealed)

    def test_plain_password_data_is_read_then_marked_for_sealing(self):
        plain = PasswordEncryption("correct password", SALT).encrypt_data({"a": 1})
        reader = WindowsBoundPasswordEncryption("correct password", SALT)
        self.assertEqual(reader.decrypt_data(plain), {"a": 1})
        self.assertTrue(reader.needs_rewrite)

    def test_a_plain_password_reader_cannot_open_sealed_data(self):
        sealed = WindowsBoundPasswordEncryption("correct password", SALT).encrypt_data({"a": 1})
        with self.assertRaises(Exception):
            PasswordEncryption("correct password", SALT).decrypt_data(sealed)

    def test_matches_checks_the_password(self):
        encryptor = PasswordEncryption("correct password", SALT)
        self.assertTrue(encryptor.matches("correct password"))
        self.assertFalse(encryptor.matches("Correct password"))
        self.assertFalse(encryptor.matches(""))


class WindowsBoundManagerTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        patcher = mock.patch.object(am, "get_data_dir", return_value=self.folder.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.manager = am.RobloxAccountManager()
        self.manager.accounts = json.loads(json.dumps(ACCOUNTS))
        self.manager.save_accounts()

    def read_file(self, name="saved_accounts.json"):
        with open(os.path.join(self.folder.name, name), encoding="utf-8") as handle:
            return handle.read()

    def test_switching_seals_the_file_and_its_backup(self):
        self.manager.switch_encryption_method("password_windows", password="correct password", salt=SALT)
        self.assertEqual(self.manager.get_encryption_mode(), "password_windows")
        self.assertEqual(self.manager.get_encryption_method(), "password")
        for name in ("saved_accounts.json", "saved_accounts.json.bak"):
            text = self.read_file(name)
            self.assertIn(encryption.WINDOWS_BOUND_FORMAT, text)
            self.assertNotIn("secret-cookie", text)
        reopened = am.RobloxAccountManager("correct password")
        self.assertEqual(reopened.accounts, ACCOUNTS)
        self.assertIsInstance(reopened.encryptor, WindowsBoundPasswordEncryption)
        with self.assertRaises(am.AccountPasswordError):
            am.RobloxAccountManager("wrong password")

    def test_switching_back_to_plain_password_removes_the_seal(self):
        self.manager.switch_encryption_method("password_windows", password="correct password", salt=SALT)
        self.manager.switch_encryption_method("password", password="correct password", salt=SALT)
        self.assertEqual(self.manager.get_encryption_mode(), "password")
        self.assertNotIn(encryption.WINDOWS_BOUND_FORMAT, self.read_file())
        self.assertEqual(am.RobloxAccountManager("correct password").accounts, ACCOUNTS)

    def test_plain_password_files_are_sealed_on_open_once_bound(self):
        self.manager.switch_encryption_method("password", password="correct password", salt=SALT)
        config = self.manager.encryption_config
        config.config["bind_to_windows"] = True
        config.save_config()
        am.RobloxAccountManager("correct password")
        self.assertIn(encryption.WINDOWS_BOUND_FORMAT, self.read_file())
        self.assertIn(encryption.WINDOWS_BOUND_FORMAT, self.read_file("saved_accounts.json.bak"))

    def test_verify_password_only_in_password_modes(self):
        self.assertFalse(self.manager.verify_password("anything"))
        self.assertFalse(self.manager.uses_password())
        self.manager.switch_encryption_method("password_windows", password="correct password", salt=SALT)
        self.assertTrue(self.manager.uses_password())
        self.assertTrue(self.manager.verify_password("correct password"))
        self.assertFalse(self.manager.verify_password("wrong password"))


if __name__ == "__main__":
    unittest.main()
