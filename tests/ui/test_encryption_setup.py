"""First-run password setup saves only the KDF salt and encryption settings."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QMainWindow

from classes.account_manager import RobloxAccountManager
from utils import ui


class EncryptionSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def open_setup(self, directory):
        self.enterContext(patch.object(ui, "get_data_dir", return_value=directory))
        self.enterContext(patch("classes.account_manager.get_data_dir", return_value=directory))
        self.enterContext(patch.object(ui, "_show_info"))
        window = QMainWindow()
        self.addCleanup(self.close_window, window)
        window._on_setup_complete = Mock()
        window.manager = RobloxAccountManager()
        window.manager.accounts = {"demo": {"cookie": "synthetic-cookie"}}
        window.manager.save_accounts()
        window.setCentralWidget(ui.AccountManagerUIQt._build_setup_panel(window))
        return window

    def confirm_password(self, window, password):
        window._setup_continue_btn.click()
        self.assertEqual(window._setup_stack.currentIndex(), 1)
        window._setup_pw_entry1.setText(password)
        window._setup_pw_entry2.setText(password)
        window._setup_pw_confirm_btn.click()
        window._on_setup_complete.assert_called_once_with()

    def test_password_confirmation_creates_a_config_without_a_fast_verifier(self):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        window = self.open_setup(directory)
        window._setup_pw_btn.click()
        password = "test-password-中文"
        self.confirm_password(window, password)
        config = json.loads((Path(directory) / "encryption_config.json").read_text(encoding="utf-8"))
        self.assertNotIn("password_hash", config)
        self.assertTrue(config["salt"])
        self.assertEqual(config["encryption_method"], "password")
        self.assertNotIn("bind_to_windows", config)
        self.assertEqual(RobloxAccountManager(password).accounts["demo"]["cookie"], "synthetic-cookie")

    def test_the_default_choice_seals_to_windows_and_encrypts_right_away(self):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        window = self.open_setup(directory)
        self.assertTrue(window._setup_pwwin_btn.isChecked())
        password = "test-password"
        self.confirm_password(window, password)
        config = json.loads((Path(directory) / "encryption_config.json").read_text(encoding="utf-8"))
        self.assertTrue(config["bind_to_windows"])
        self.assertEqual(window.manager.get_encryption_mode(), "password_windows")
        # The file already open in this session is re-encrypted, not left in plain text.
        for name in ("saved_accounts.json", "saved_accounts.json.bak"):
            self.assertNotIn("synthetic-cookie", (Path(directory) / name).read_text(encoding="utf-8"))
        self.assertEqual(RobloxAccountManager(password).accounts["demo"]["cookie"], "synthetic-cookie")

    def close_window(self, window):
        window.close()
        window.deleteLater()
        self.app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
