import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from features import account_backup, auto_backup

NOW = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
ACCOUNTS = {"PurpleFox": {"username": "PurpleFox", "cookie": "secret-cookie", "user_id": 1}}
PASSWORD = "correct horse battery"


def settings(**values):
    return {auto_backup.ENABLED_SETTING: True, **values}


class ScheduleTests(unittest.TestCase):
    def test_nothing_is_due_while_disabled(self):
        self.assertFalse(auto_backup.is_due({}, NOW))
        self.assertFalse(auto_backup.is_due({auto_backup.ENABLED_SETTING: "yes"}, NOW))

    def test_the_first_backup_is_due_right_away(self):
        self.assertTrue(auto_backup.is_due(settings(), NOW))

    def test_the_next_backup_waits_for_the_interval(self):
        last = (NOW - timedelta(days=6, hours=23)).isoformat()
        self.assertFalse(auto_backup.is_due(settings(auto_backup_last=last), NOW))
        last = (NOW - timedelta(days=7)).isoformat()
        self.assertTrue(auto_backup.is_due(settings(auto_backup_last=last), NOW))
        last = (NOW - timedelta(days=1)).isoformat()
        self.assertTrue(auto_backup.is_due(settings(auto_backup_last=last, auto_backup_interval_days=1), NOW))

    def test_a_clock_moved_back_or_a_bad_date_does_not_block_backups(self):
        future = (NOW + timedelta(days=30)).isoformat()
        self.assertTrue(auto_backup.is_due(settings(auto_backup_last=future), NOW))
        self.assertTrue(auto_backup.is_due(settings(auto_backup_last="not a date"), NOW))

    def test_numbers_are_clamped_to_their_range(self):
        self.assertEqual(auto_backup.interval_days({"auto_backup_interval_days": 0}), 1)
        self.assertEqual(auto_backup.interval_days({"auto_backup_interval_days": "x"}), 7)
        self.assertEqual(auto_backup.keep_count({"auto_backup_keep": 1000}), 100)

    def test_the_default_folder_is_in_documents(self):
        self.assertTrue(auto_backup.default_folder().endswith(auto_backup.FOLDER_NAME))
        self.assertEqual(auto_backup.folder({"auto_backup_folder": "  "}), auto_backup.default_folder())
        self.assertEqual(auto_backup.folder({"auto_backup_folder": "D:/Backups"}), "D:/Backups")


class BackupFileTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = os.path.join(temporary.name, "nested", "backups")

    def test_a_backup_can_be_restored_with_its_password_only(self):
        result = auto_backup.run_backup(ACCOUNTS, self.folder, PASSWORD, keep=5, now=NOW)
        self.assertTrue(result, result)
        self.assertTrue(os.path.basename(result.data["path"]).startswith(auto_backup.FILE_PREFIX))
        restored = account_backup.read_backup(result.data["path"], PASSWORD)
        self.assertEqual(restored.data["accounts"], ACCOUNTS)
        self.assertFalse(account_backup.read_backup(result.data["path"], "wrong password"))
        with open(result.data["path"], encoding="utf-8") as handle:
            self.assertNotIn("secret-cookie", handle.read())

    def test_only_the_newest_backups_are_kept_and_other_files_are_left_alone(self):
        os.makedirs(self.folder)
        mine = os.path.join(self.folder, "notes.txt")
        manual = os.path.join(self.folder, "RAM-accounts.rambak")
        for path in (mine, manual):
            with open(path, "w") as handle:
                handle.write("keep me")
        for day in range(6):
            result = auto_backup.run_backup(ACCOUNTS, self.folder, PASSWORD, keep=3, now=NOW + timedelta(days=day))
            self.assertTrue(result, result)
        backups = auto_backup.list_backups(self.folder)
        self.assertEqual(len(backups), 3)
        self.assertEqual(backups[-1], result.data["path"])
        self.assertTrue(os.path.exists(mine))
        self.assertTrue(os.path.exists(manual))

    def test_a_short_password_or_no_accounts_writes_nothing(self):
        self.assertFalse(auto_backup.run_backup(ACCOUNTS, self.folder, "short", keep=5, now=NOW))
        self.assertFalse(auto_backup.run_backup({}, self.folder, PASSWORD, keep=5, now=NOW))
        self.assertEqual(auto_backup.list_backups(self.folder), [])

    def test_an_unusable_folder_is_reported(self):
        blocker = os.path.join(os.path.dirname(self.folder), "file")
        os.makedirs(os.path.dirname(blocker))
        with open(blocker, "w") as handle:
            handle.write("not a folder")
        result = auto_backup.run_backup(ACCOUNTS, os.path.join(blocker, "sub"), PASSWORD, keep=5, now=NOW)
        self.assertEqual(result.code, "AUTO_BACKUP_FOLDER_UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
