"""The browser used to add an account must not keep the CPU busy while it waits."""

import os
import tempfile
import unittest
from unittest import mock

from selenium.common.exceptions import JavascriptException, WebDriverException

from classes import account_manager as am


class FakeDriver:
    def __init__(self, states):
        self.states = list(states)
        self.scripts = []

    def execute_script(self, script, *args):
        self.scripts.append(script)
        if script.lstrip().startswith("return {href"):
            state = self.states.pop(0)
            if isinstance(state, Exception):
                raise state
            return state
        return None


def state(href, detected=False, alive=True):
    return {"href": href, "alive": alive, "detected": detected}


class WaitForLoginTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        patcher = mock.patch.object(am, "get_data_dir", return_value=folder.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.manager = am.RobloxAccountManager()
        self.sleep = mock.patch.object(am.time, "sleep").start()
        self.addCleanup(mock.patch.stopall)

    def state_calls(self, driver):
        return [s for s in driver.scripts if s.lstrip().startswith("return {href")]

    def test_waits_calmly_with_one_call_per_check(self):
        login = "https://www.roblox.com/login"
        driver = FakeDriver([state(login), state(login), state(login, detected=True)])
        self.assertTrue(self.manager.wait_for_login(driver, timeout=60))
        self.assertEqual(len(self.state_calls(driver)), 3)
        self.assertEqual([c.args[0] for c in self.sleep.call_args_list], [0.25, 0.25])

    def test_a_logged_in_page_is_enough(self):
        driver = FakeDriver([state("https://www.roblox.com/login"), state("https://www.roblox.com/home")])
        self.assertTrue(self.manager.wait_for_login(driver, timeout=60))

    def test_a_page_change_error_does_not_cancel_the_login(self):
        driver = FakeDriver([
            JavascriptException("document unloaded while waiting for result"),
            state("https://www.roblox.com/home"),
        ])
        self.assertTrue(self.manager.wait_for_login(driver, timeout=60))

    def test_a_closed_browser_stops_waiting(self):
        driver = FakeDriver([WebDriverException("no such window")])
        self.assertFalse(self.manager.wait_for_login(driver, timeout=60))

    def test_the_detector_is_injected_again_after_a_navigation(self):
        login = "https://www.roblox.com/login"
        driver = FakeDriver([state(login, alive=False), state(login, detected=True)])
        self.assertTrue(self.manager.wait_for_login(driver, timeout=60))
        injections = [s for s in driver.scripts if "window.browserDetect = {" in s]
        self.assertEqual(len(injections), 2)  # first load + after the page lost it

    def test_the_page_script_uses_slow_timers_only(self):
        driver = FakeDriver([state("https://www.roblox.com/home")])
        self.manager.wait_for_login(driver, timeout=60)
        detector = next(s for s in driver.scripts if "window.browserDetect = {" in s)
        self.assertNotIn("MutationObserver", detector)
        self.assertNotIn("debug.push", detector)
        self.assertNotRegex(detector, r"setInterval\([^)]*,\s*(\d{1,2}|1\d\d)\)")


class ChromeOptionsTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = folder.name
        patcher = mock.patch.object(am, "get_data_dir", return_value=folder.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.manager = am.RobloxAccountManager()
        self.driver_file = os.path.join(folder.name, "chromedriver.exe")
        open(self.driver_file, "w").close()

    def start_chrome(self, chrome):
        with mock.patch("selenium.webdriver.Chrome", chrome):
            result = self.manager.setup_browser_driver(browser="chrome")
        self.assertTrue(result, result)
        return chrome.call_args

    def fake_chrome(self):
        driver = mock.MagicMock()
        driver.service.path = self.driver_file
        return mock.MagicMock(return_value=driver)

    def test_chrome_keeps_gpu_and_background_throttling(self):
        call = self.start_chrome(self.fake_chrome())
        arguments = call.kwargs["options"].arguments
        for flag in ("--disable-gpu", "--disable-background-timer-throttling",
                     "--disable-renderer-backgrounding", "--disable-backgrounding-occluded-windows",
                     "--aggressive-cache-discard"):
            self.assertNotIn(flag, arguments)

    def test_later_browsers_reuse_the_driver_found_first(self):
        chrome = self.fake_chrome()
        first = self.start_chrome(chrome)
        self.assertNotIn("service", first.kwargs)
        second = self.start_chrome(chrome)
        self.assertEqual(second.kwargs["service"].path, self.driver_file)


if __name__ == "__main__":
    unittest.main()
