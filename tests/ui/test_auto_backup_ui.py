import threading
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from classes.operation_result import OperationResult
from utils import ui


class RunNow:
    def __init__(self, *args, **kwargs):
        self.target = kwargs.get("target")

    def start(self):
        self.target()


class AutoBackupTickTests(unittest.TestCase):
    def setUp(self):
        self.manager = SimpleNamespace(
            _accounts_lock=threading.Lock(),
            accounts={"PurpleFox": {"cookie": "x"}},
            get_secure_setting=MagicMock(return_value="backup password"),
        )
        self.window = SimpleNamespace(
            manager=self.manager,
            _auto_backup_running=False,
            _bridge=SimpleNamespace(auto_backup_done=MagicMock()),
        )
        self.settings = {"auto_backup_enabled": True, "auto_backup_folder": "D:/Backups", "auto_backup_keep": 4}
        self.enterContext(patch.object(ui.actions, "load_ui_settings", side_effect=lambda: self.settings))
        self.enterContext(patch.object(ui.threading, "Thread", RunNow))
        self.run = self.enterContext(patch.object(
            ui.auto_backup, "run_backup", return_value=OperationResult.success(data={})
        ))

    def tick(self, force=False):
        ui.AccountManagerUIQt._auto_backup_tick(self.window, force=force)

    def test_a_due_backup_runs_with_the_saved_password_folder_and_count(self):
        self.tick()
        self.run.assert_called_once_with(
            self.manager.accounts, "D:/Backups", "backup password", 4
        )
        self.window._bridge.auto_backup_done.emit.assert_called_once()

    def test_nothing_runs_when_not_due_unless_forced(self):
        self.settings["auto_backup_last"] = "2999-01-01T00:00:00+00:00"
        with patch.object(ui.auto_backup, "is_due", return_value=False):
            self.tick()
            self.run.assert_not_called()
            self.tick(force=True)
        self.run.assert_called_once()

    def test_nothing_runs_without_a_password_accounts_or_while_one_is_running(self):
        self.manager.get_secure_setting.return_value = ""
        self.tick()
        self.manager.get_secure_setting.return_value = "backup password"
        self.manager.accounts = {}
        self.tick()
        self.manager.accounts = {"a": {}}
        self.window._auto_backup_running = True
        self.tick()
        self.run.assert_not_called()

    def test_success_records_the_time_and_failure_does_not(self):
        window = SimpleNamespace(_auto_backup_running=True, _refresh_auto_backup_status=MagicMock())
        with patch.object(ui.actions, "save_ui_setting") as save:
            ok = OperationResult.success(data={"time": "2026-11-07T12:00:00+00:00", "path": "p", "count": 1})
            ui.AccountManagerUIQt._on_auto_backup_done(window, ok)
            save.assert_called_once_with("auto_backup_last", "2026-11-07T12:00:00+00:00")
            failed = OperationResult.failure("AUTO_BACKUP_FOLDER_UNAVAILABLE", "t", "Drive missing.")
            ui.AccountManagerUIQt._on_auto_backup_done(window, failed)
            save.assert_called_once()
        window._refresh_auto_backup_status.assert_called_with("Drive missing.")
        self.assertFalse(window._auto_backup_running)


if __name__ == "__main__":
    unittest.main()
