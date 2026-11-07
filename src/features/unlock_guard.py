"""
features/unlock_guard.py
Growing wait after wrong passwords on the sign-in and lock screens.

This slows down someone guessing at the keyboard. It does not protect a copied
account file: that is the job of the password key derivation, and of the
Windows binding in "Password + Windows" mode.
"""

from __future__ import annotations

import time

FREE_ATTEMPTS = 2
MAX_DELAY_SECONDS = 60


def delay_after(failures: int) -> int:
    """Seconds to wait after this many consecutive failures: 0, 0, 2, 4, 8 ... up to 60."""
    if failures <= FREE_ATTEMPTS:
        return 0
    return min(MAX_DELAY_SECONDS, 2 ** (failures - FREE_ATTEMPTS))


class UnlockGuard:
    def __init__(self, clock=time.monotonic):
        self._clock = clock
        self.failures = 0
        self._ready_at = 0.0

    def remaining(self) -> int:
        """Whole seconds left before the next attempt is allowed."""
        left = self._ready_at - self._clock()
        return max(0, int(left + 0.999))

    def failed(self) -> int:
        self.failures += 1
        delay = delay_after(self.failures)
        self._ready_at = self._clock() + delay
        return delay

    def succeeded(self) -> None:
        self.failures = 0
        self._ready_at = 0.0


# Auto-lock settings (ui_settings.json)
AUTO_LOCK_MINUTES_SETTING = "auto_lock_minutes"
LOCK_ON_MINIMIZE_SETTING = "lock_on_minimize"
LOCK_ON_WINDOWS_LOCK_SETTING = "lock_on_windows_lock"
DEFAULT_AUTO_LOCK_MINUTES = 15
AUTO_LOCK_RANGE = (0, 240)  # 0 = never


def auto_lock_minutes(settings: dict) -> int:
    try:
        minutes = int(settings.get(AUTO_LOCK_MINUTES_SETTING, DEFAULT_AUTO_LOCK_MINUTES))
    except (TypeError, ValueError):
        return DEFAULT_AUTO_LOCK_MINUTES
    return max(AUTO_LOCK_RANGE[0], min(AUTO_LOCK_RANGE[1], minutes))


def lock_on_minimize(settings: dict) -> bool:
    return settings.get(LOCK_ON_MINIMIZE_SETTING, True) is not False


def lock_on_windows_lock(settings: dict) -> bool:
    return settings.get(LOCK_ON_WINDOWS_LOCK_SETTING, True) is not False


def idle_expired(last_activity: float, now: float, minutes: int) -> bool:
    return minutes > 0 and now - last_activity >= minutes * 60
