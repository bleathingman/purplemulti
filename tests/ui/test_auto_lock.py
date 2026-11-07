"""Sign-in retries and the auto-lock screen."""

import ctypes
import time
import unittest
from ctypes import wintypes
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QDialog

from classes.account_manager import AccountPasswordError
from utils import ui


class UnlockFormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_wrong_passwords_lock_the_button_for_a_while(self):
        form = ui._UnlockForm("Locked", "Enter your password.")
        self.addCleanup(form.deleteLater)
        seen = []
        form.submitted.connect(seen.append)
        for _ in range(3):
            form.entry.setText("guess")
            form.button.click()
            form.reject_password()
        self.assertEqual(seen, ["guess"] * 3)
        self.assertFalse(form.button.isEnabled())
        self.assertTrue(form.button.text().startswith("Try again in"))
        self.assertEqual(form.error.text(), "Wrong password.")
        form.entry.setText("blocked")
        form._submit()
        self.assertEqual(len(seen), 3)

    def test_success_resets_the_form(self):
        form = ui._UnlockForm("Locked", "Enter your password.")
        self.addCleanup(form.deleteLater)
        form.reject_password()
        form.accept_password()
        self.assertEqual(form.guard.failures, 0)
        self.assertTrue(form.button.isEnabled())
        self.assertEqual(form.button.text(), "Unlock")
        self.assertEqual(form.error.text(), "")


class PasswordDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def submit(self, dialog, password):
        dialog.form.entry.setText(password)
        dialog.form.button.click()

    def test_a_wrong_password_can_be_retried_without_closing(self):
        attempts = []

        def opener(password):
            attempts.append(password)
            if password != "right password":
                raise AccountPasswordError("wrong")
            return "manager"

        dialog = ui._PasswordDialog(opener)
        self.addCleanup(dialog.deleteLater)
        self.submit(dialog, "wrong password")
        self.assertNotEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.assertEqual(dialog.form.error.text(), "Wrong password.")
        dialog.form.guard.succeeded()  # skip any wait
        self.submit(dialog, "right password")
        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.assertEqual(dialog.manager, "manager")
        self.assertIsNone(dialog.failure)
        self.assertEqual(attempts, ["wrong password", "right password"])

    def test_other_errors_close_the_dialog_and_are_reported(self):
        failure = RuntimeError("damaged file")

        def opener(_password):
            raise failure

        dialog = ui._PasswordDialog(opener)
        self.addCleanup(dialog.deleteLater)
        self.submit(dialog, "any password")
        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.assertIs(dialog.failure, failure)
        self.assertIsNone(dialog.manager)


class AutoLockWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def window(self, uses_password=True):
        manager = MagicMock()
        manager.accounts = {}
        manager.get_encryption_method.return_value = "password"
        manager.get_secure_setting.return_value = ""
        manager.uses_password.return_value = uses_password
        manager.verify_password.side_effect = lambda password: password == "right password"
        with patch.object(ui.QTimer, "singleShot"), \
                patch.object(ui.threading.Thread, "start"), \
                patch.object(ui.AccountManagerUIQt, "_setup_system_tray"), \
                patch.object(ui.EncryptionConfig, "is_setup_complete", return_value=True):
            window = ui.AccountManagerUIQt(manager)
        self.addCleanup(window.deleteLater)
        self.addCleanup(window.close)
        return window

    def unlock(self, window, password):
        window._lock_form.guard.succeeded()
        window._lock_form.entry.setText(password)
        window._lock_form.button.click()

    def test_locking_hides_everything_until_the_right_password(self):
        window = self.window()
        window._show_page(2)
        self.assertTrue(window._nav_lock_btn.isVisibleTo(window))
        self.assertTrue(window._lock_app("test"))
        self.assertIs(window._page_stack.currentWidget(), window._lock_page)
        self.assertFalse(window._nav_panel.isEnabled())
        self.assertTrue(window._activity_filter.eventFilter(window, QEvent(QEvent.Type.Shortcut)))

        self.unlock(window, "wrong password")
        self.assertTrue(window._locked)
        self.assertEqual(window._lock_form.error.text(), "Wrong password.")

        self.unlock(window, "right password")
        self.assertFalse(window._locked)
        self.assertEqual(window._page_stack.currentIndex(), 2)
        self.assertTrue(window._nav_panel.isEnabled())
        self.assertFalse(window._activity_filter.eventFilter(window, QEvent(QEvent.Type.Shortcut)))

    def test_without_a_password_there_is_nothing_to_lock(self):
        window = self.window(uses_password=False)
        self.assertFalse(window._nav_lock_btn.isVisibleTo(window))
        self.assertFalse(window._lock_app("test"))
        self.assertFalse(window._locked)

    def test_inactivity_locks_after_the_chosen_minutes(self):
        window = self.window()
        with patch.object(ui.actions, "load_ui_settings", return_value={"auto_lock_minutes": 15}):
            window._activity_filter.last_activity = time.monotonic() - 14 * 60
            window._check_auto_lock()
            self.assertFalse(window._locked)
            window._activity_filter.last_activity = time.monotonic() - 15 * 60
            window._check_auto_lock()
        self.assertTrue(window._locked)

    def test_a_never_setting_does_not_lock(self):
        window = self.window()
        with patch.object(ui.actions, "load_ui_settings", return_value={"auto_lock_minutes": 0}):
            window._activity_filter.last_activity = 0
            window._check_auto_lock()
        self.assertFalse(window._locked)


class SessionLockMessageTests(unittest.TestCase):
    def message(self, code, param):
        msg = wintypes.MSG()
        msg.message = code
        msg.wParam = param
        return msg

    def test_only_the_session_lock_notification_matches(self):
        locked = self.message(ui.WM_WTSSESSION_CHANGE, ui.WTS_SESSION_LOCK)
        unlocked = self.message(ui.WM_WTSSESSION_CHANGE, 0x8)
        other = self.message(0x0312, ui.WTS_SESSION_LOCK)
        self.assertTrue(ui._is_session_lock_message(ctypes.addressof(locked)))
        self.assertFalse(ui._is_session_lock_message(ctypes.addressof(unlocked)))
        self.assertFalse(ui._is_session_lock_message(ctypes.addressof(other)))
        self.assertFalse(ui._is_session_lock_message("not a pointer"))


if __name__ == "__main__":
    unittest.main()
