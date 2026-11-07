import unittest

from features import unlock_guard


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class UnlockGuardTests(unittest.TestCase):
    def test_the_wait_grows_after_the_free_attempts_and_is_capped(self):
        delays = [unlock_guard.delay_after(n) for n in range(1, 11)]
        self.assertEqual(delays, [0, 0, 2, 4, 8, 16, 32, 60, 60, 60])

    def test_remaining_counts_down_and_success_resets(self):
        clock = Clock()
        guard = unlock_guard.UnlockGuard(clock)
        guard.failed()
        guard.failed()
        self.assertEqual(guard.remaining(), 0)
        self.assertEqual(guard.failed(), 2)
        self.assertEqual(guard.remaining(), 2)
        clock.now += 1.2
        self.assertEqual(guard.remaining(), 1)
        clock.now += 1
        self.assertEqual(guard.remaining(), 0)
        guard.succeeded()
        self.assertEqual(guard.failures, 0)
        self.assertEqual(guard.failed(), 0)


class AutoLockSettingsTests(unittest.TestCase):
    def test_defaults_and_bounds(self):
        self.assertEqual(unlock_guard.auto_lock_minutes({}), 15)
        self.assertEqual(unlock_guard.auto_lock_minutes({"auto_lock_minutes": 0}), 0)
        self.assertEqual(unlock_guard.auto_lock_minutes({"auto_lock_minutes": 9999}), 240)
        self.assertEqual(unlock_guard.auto_lock_minutes({"auto_lock_minutes": "x"}), 15)
        self.assertTrue(unlock_guard.lock_on_minimize({}))
        self.assertFalse(unlock_guard.lock_on_minimize({"lock_on_minimize": False}))
        self.assertTrue(unlock_guard.lock_on_windows_lock({}))

    def test_idle_expiry(self):
        self.assertFalse(unlock_guard.idle_expired(0, 899, 15))
        self.assertTrue(unlock_guard.idle_expired(0, 900, 15))
        self.assertFalse(unlock_guard.idle_expired(0, 10**9, 0))


if __name__ == "__main__":
    unittest.main()
