import unittest

from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from utils import theme_runtime, ui_kit


class UiKitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_card_flow_opens_one_card_per_section(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        flow = ui_kit.CardFlow(outer)

        flow.addWidget(ui_kit.section_label("First"))
        first = QCheckBox("One")
        flow.addWidget(first)
        row = QHBoxLayout()
        row.addWidget(QLabel("Row"))
        flow.addLayout(row)
        flow.addWidget(ui_kit.section_label("Second"))
        second = QCheckBox("Two")
        flow.addWidget(second)
        flow.addStretch(1)

        cards = page.findChildren(QFrame, "card")
        self.assertEqual(len(cards), 2)
        self.assertIs(first.parentWidget(), cards[0])
        self.assertIs(second.parentWidget(), cards[1])
        self.assertEqual(outer.count(), 5)

    def test_card_flow_keeps_buttons_at_their_own_width(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        flow = ui_kit.CardFlow(outer)
        button = QPushButton("Action")
        flow.addWidget(button)
        card = page.findChild(QFrame, "card")
        page.resize(600, 200)
        page.show()
        self.app.processEvents()
        self.addCleanup(page.close)
        self.assertLess(button.width(), card.width() / 2)

    def test_chip_tone_can_change_and_clear(self):
        label = ui_kit.chip("Status", "success")
        self.assertEqual(label.property("tone"), "success")
        ui_kit.set_chip(label, "Stopped")
        self.assertEqual(label.text(), "Stopped")
        self.assertEqual(label.property("tone"), "")

    def test_variant_is_exposed_to_the_stylesheet(self):
        button = ui_kit.set_variant(QPushButton("Go"), "primary")
        self.assertEqual(button.property("variant"), "primary")

    def test_toggle_tokens_resolve_to_existing_files(self):
        manager = theme_runtime.get_manager()
        rendered = manager.render('url(@RAM_TOGGLE_ON@) url(@RAM_TOGGLE_OFF@) url(@RAM_TOGGLE_DISABLED@)')
        self.assertNotIn('@RAM_', rendered)
        self.assertEqual(rendered.count('.svg'), 3)

    def test_initials_follow_word_boundaries(self):
        cases = {
            "NightOwl_22": "NO",
            "alt_account_5": "AA",
            "PurpleFox": "PF",
            "builder": "B",
            "12345": "1",
            "": "",
            "x-ray.Fan": "XR",
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                self.assertEqual(ui_kit.initials(name), expected)

    def test_empty_state_covers_the_list_and_follows_resizes(self):
        from PySide6.QtWidgets import QListWidget
        view = QListWidget()
        self.addCleanup(view.close)
        empty = ui_kit.EmptyState(view, "Nothing here", "Add something.")
        view.resize(300, 200)
        view.show()
        self.app.processEvents()
        self.assertFalse(empty.isVisible())
        empty.show()
        view.resize(420, 260)
        self.app.processEvents()
        self.assertEqual(empty.geometry(), view.viewport().rect())
        self.assertEqual(empty.title(), "Nothing here")
        empty.set_text("Other")
        self.assertEqual(empty.title(), "Other")

    def test_option_card_is_checkable_and_named_for_screen_readers(self):
        card = ui_kit.option_card("Password", "Asked at every start.", badge="Safest")
        self.assertTrue(card.isCheckable())
        self.assertEqual(card.accessibleName(), "Password")
        texts = [label.text() for label in card.findChildren(QLabel)]
        self.assertIn("Asked at every start.", texts)
        self.assertIn("Safest", texts)

    def test_avatar_placeholder_with_initials_is_cached_per_text(self):
        manager = theme_runtime.get_manager()
        plain = manager.placeholder_pixmap(24)
        lettered = manager.placeholder_pixmap(24, "AB")
        self.assertIsNot(plain, lettered)
        self.assertIs(lettered, manager.placeholder_pixmap(24, "AB"))

    def test_soft_status_tones_exist_for_every_theme_surface(self):
        colors = theme_runtime.colors()
        for role in ('SUCCESS', 'WARNING', 'ERROR'):
            self.assertRegex(colors[f'{role}_SOFT'], r'^#[0-9A-F]{6}$')


if __name__ == "__main__":
    unittest.main()
