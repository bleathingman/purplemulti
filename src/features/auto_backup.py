"""
features/auto_backup.py
Regular password-protected account backups (.rambak) in a folder of the user's choice.

The account file itself may use DPAPI, which only this Windows account can open.
These backups use their own password instead, so they can be restored on any PC
with Import Accounts, including after Windows is reinstalled.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone

from classes.operation_result import OperationResult
from features import account_backup

PASSWORD_KEY = "auto_backup_password"  # secure setting, stored with the encrypted accounts
ENABLED_SETTING = "auto_backup_enabled"
FOLDER_SETTING = "auto_backup_folder"
INTERVAL_SETTING = "auto_backup_interval_days"
KEEP_SETTING = "auto_backup_keep"
LAST_SETTING = "auto_backup_last"

DEFAULT_INTERVAL_DAYS = 7
DEFAULT_KEEP = 5
INTERVAL_RANGE = (1, 90)
KEEP_RANGE = (1, 100)
FOLDER_NAME = "PurpleMulti Backups"
FILE_PREFIX = "PurpleMulti-accounts-"
FILE_SUFFIX = ".rambak"
_FILE_PATTERN = re.compile(
    re.escape(FILE_PREFIX) + r"\d{4}-\d{2}-\d{2}_\d{6}" + re.escape(FILE_SUFFIX) + r"$",
    re.IGNORECASE,
)


def _documents_dir() -> str:
    try:
        from win32com.shell import shell, shellcon

        # Follows a Documents folder moved to OneDrive or another drive.
        return shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
    except Exception:
        return os.path.join(os.path.expanduser("~"), "Documents")


def default_folder() -> str:
    return os.path.join(_documents_dir(), FOLDER_NAME)


def _clamped_int(value, default: int, bounds: tuple[int, int]) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(bounds[0], min(bounds[1], number))


def is_enabled(settings: dict) -> bool:
    return settings.get(ENABLED_SETTING) is True


def folder(settings: dict) -> str:
    chosen = settings.get(FOLDER_SETTING)
    return chosen if isinstance(chosen, str) and chosen.strip() else default_folder()


def interval_days(settings: dict) -> int:
    return _clamped_int(settings.get(INTERVAL_SETTING), DEFAULT_INTERVAL_DAYS, INTERVAL_RANGE)


def keep_count(settings: dict) -> int:
    return _clamped_int(settings.get(KEEP_SETTING), DEFAULT_KEEP, KEEP_RANGE)


def last_backup(settings: dict) -> datetime | None:
    value = settings.get(LAST_SETTING)
    if not isinstance(value, str):
        return None
    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def is_due(settings: dict, now: datetime | None = None) -> bool:
    if not is_enabled(settings):
        return False
    last = last_backup(settings)
    if last is None:
        return True
    now = now or datetime.now(timezone.utc)
    # A clock moved backwards must not postpone backups forever.
    return now < last or now - last >= timedelta(days=interval_days(settings))


def file_name(moment: datetime) -> str:
    return f"{FILE_PREFIX}{moment.astimezone():%Y-%m-%d_%H%M%S}{FILE_SUFFIX}"


def list_backups(target: str) -> list[str]:
    """Backups made by this feature in the folder, oldest first. Other files are ignored."""
    try:
        names = os.listdir(target)
    except OSError:
        return []
    return [os.path.join(target, name) for name in sorted(names) if _FILE_PATTERN.match(name)]


def prune(target: str, keep: int) -> list[str]:
    removed = []
    for path in list_backups(target)[:-keep] if keep > 0 else []:
        try:
            os.remove(path)
            removed.append(path)
        except OSError as exc:
            print(f"[WARNING] Could not remove old backup {path}: {exc}")
    return removed


def run_backup(accounts: dict, target: str, password: str, keep: int,
               now: datetime | None = None) -> OperationResult:
    """Write one backup into the folder, then keep only the newest `keep` backups."""
    now = now or datetime.now(timezone.utc)
    try:
        os.makedirs(target, exist_ok=True)
    except OSError as exc:
        return OperationResult.failure(
            "AUTO_BACKUP_FOLDER_UNAVAILABLE",
            "Backup Folder Unavailable",
            "The backup folder could not be created. Check that its drive is connected.",
            detail=f"{target}: {type(exc).__name__}: {exc}",
        )
    path = os.path.join(target, file_name(now))
    result = account_backup.export_accounts(accounts, path, password)
    if not result:
        return result
    removed = prune(target, keep)
    return OperationResult.success(
        f"Backed up {result.data['count']} account(s).",
        data={"path": path, "count": result.data["count"], "removed": removed,
              "time": now.isoformat(timespec="seconds")},
    )
