import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QWidget

from utils import ui

LINKS = [
    ("PayPal", "One-time donation.", "https://paypal.me/example"),
    ("Ko-fi", "", "https://ko-fi.com/example"),
]


class DonationsPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def build(self, links):
        host = QWidget()
        self.addCleanup(host.deleteLater)
        with patch.object(ui, "DONATION_LINKS", links):
            return ui.AccountManagerUIQt._build_donations_panel(host)

    def buttons(self, panel, text):
        return [b for b in panel.findChildren(QPushButton) if b.text() == text]

    def test_the_page_is_hidden_until_a_link_is_configured(self):
        self.assertEqual(ui.SHOW_DONATIONS_PAGE, bool(ui.DONATION_LINKS))

    def test_each_link_gets_a_card_with_open_and_copy(self):
        panel = self.build(LINKS)
        titles = [label.text() for label in panel.findChildren(QLabel)]
        self.assertIn("PayPal", titles)
        self.assertIn("Ko-fi", titles)
        self.assertEqual(len(self.buttons(panel, "Open")), 2)
        self.assertEqual(len(self.buttons(panel, "Copy Link")), 2)

    def test_open_launches_the_browser_on_that_link(self):
        panel = self.build(LINKS)
        with patch.object(ui.webbrowser, "open") as browser:
            self.buttons(panel, "Open")[1].click()
        browser.assert_called_once_with("https://ko-fi.com/example")

    def test_copy_puts_the_link_on_the_clipboard(self):
        panel = self.build(LINKS)
        self.buttons(panel, "Copy Link")[0].click()
        self.assertEqual(QApplication.clipboard().text(), "https://paypal.me/example")


if __name__ == "__main__":
    unittest.main()
