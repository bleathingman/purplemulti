import unittest

from features import color_themes as ct

PURPLE_DEFAULTS = {
    "BG": "#0E0B16", "PANEL": "#15111F", "INPUT": "#1C1729", "TEXT": "#F2EFF9",
    "MUTED": "#A59DBB", "LINE": "#2A2339", "SELECT": "#2C2342", "NOTE": "#CDB8FF",
    "ACCENT": "#7C3AED",
    "HOVER": "#3A3546", "PRESSED": "#14101F", "RAISED": "#2B2638",
    "ACCENT_HOVER": "#9058F0", "ACCENT_PRESSED": "#6931C9", "ACCENT_BRIGHT": "#894EEF",
    "ACCENT_SOFT": "#4A258C", "ACCENT_TEXT": "#B793F5", "ACCENT_DEEP": "#1D1234",
}


class ResolveColorsTests(unittest.TestCase):
    def test_default_theme_is_the_purple_palette(self):
        colors = ct.resolve_colors({})
        for key, value in PURPLE_DEFAULTS.items():
            with self.subTest(key=key):
                self.assertEqual(colors[key], value)
        self.assertEqual(colors["ON_ACCENT"], "#FFFFFF")

    def test_missing_unknown_or_invalid_settings_fall_back_to_the_default(self):
        default = ct.resolve_colors({})
        for settings in (None, "text", {"color_theme": "no-such-theme"}, {"color_theme": 5},
                         {"color_theme": None}, {"accent_color": "red"}, {"accent_color": "#12345"},
                         {"accent_color": 7}):
            with self.subTest(settings=settings):
                self.assertEqual(ct.resolve_colors(settings), default)

    def test_every_preset_defines_every_key_as_a_valid_colour(self):
        for name in ct.PRESETS:
            colors = ct.resolve_colors({"color_theme": name})
            self.assertEqual(set(colors), set(ct.KEYS))
            for key, value in colors.items():
                with self.subTest(theme=name, key=key):
                    self.assertTrue(ct.is_hex_color(value), value)

    def test_presets_are_different_from_each_other(self):
        backgrounds = [ct.resolve_colors({"color_theme": name})["BG"] for name in ct.PRESETS]
        self.assertEqual(len(set(backgrounds)), len(backgrounds))

    def test_choices_start_with_the_default_and_have_labels(self):
        choices = ct.theme_choices()
        self.assertEqual(choices[0], ("default", "Purple"))
        self.assertTrue(all(label for _, label in choices))

    def test_custom_accent_replaces_the_accent_and_its_variants(self):
        colors = ct.resolve_colors({"color_theme": "default", "accent_color": "#e5557f"})
        self.assertEqual(colors["ACCENT"], "#E5557F")
        for key in ct.DERIVED_ACCENT:
            with self.subTest(key=key):
                self.assertNotEqual(colors[key], PURPLE_DEFAULTS[key])
        self.assertEqual(colors["BG"], PURPLE_DEFAULTS["BG"])
        self.assertEqual(colors["HOVER"], PURPLE_DEFAULTS["HOVER"])

    def test_custom_accent_works_on_every_preset(self):
        for name in ct.PRESETS:
            colors = ct.resolve_colors({"color_theme": name, "accent_color": "#FFD400"})
            self.assertEqual(colors["ACCENT"], "#FFD400")
            self.assertEqual(colors["ON_ACCENT"], "#101010")

    def test_settings_are_not_modified(self):
        settings = {"color_theme": "nord", "accent_color": "#112233"}
        ct.resolve_colors(settings)
        self.assertEqual(settings, {"color_theme": "nord", "accent_color": "#112233"})


class ReadabilityTests(unittest.TestCase):
    def all_themes(self):
        for name in ct.PRESETS:
            yield name, ct.resolve_colors({"color_theme": name})
        for accent in ("#FF0000", "#00FF00", "#0000FF", "#FFFFFF", "#000000", "#808080", "#FFD400"):
            yield f"default+{accent}", ct.resolve_colors({"accent_color": accent})

    def check(self, first, second, minimum):
        for name, colors in self.all_themes():
            with self.subTest(theme=name, pair=f"{first}/{second}"):
                self.assertGreaterEqual(ct.contrast_ratio(colors[first], colors[second]), minimum)

    def test_body_text_is_easy_to_read(self):
        for background in ("BG", "PANEL", "INPUT", "SELECT"):
            self.check("TEXT", background, 7.0)

    def test_muted_and_note_text_pass_the_normal_text_minimum(self):
        for background in ("BG", "PANEL", "INPUT"):
            self.check("MUTED", background, 4.5)
            self.check("NOTE", background, 4.5)

    def test_accent_text_is_readable_on_the_background(self):
        self.check("ACCENT_TEXT", "BG", 4.5)

    def test_text_on_accent_buttons_is_readable(self):
        self.check("ON_ACCENT", "ACCENT", 4.4)


class ColourMathTests(unittest.TestCase):
    def test_mix(self):
        self.assertEqual(ct.mix("#000000", "#FFFFFF", 0.5), "#808080")
        self.assertEqual(ct.mix("#102030", "#102030", 0.7), "#102030")
        self.assertEqual(ct.mix("#000000", "#FFFFFF", 0), "#000000")
        self.assertEqual(ct.mix("#000000", "#FFFFFF", 1), "#FFFFFF")

    def test_contrast_ratio_extremes(self):
        self.assertAlmostEqual(ct.contrast_ratio("#000000", "#FFFFFF"), 21.0, places=1)
        self.assertAlmostEqual(ct.contrast_ratio("#777777", "#777777"), 1.0, places=3)

    def test_is_hex_color(self):
        for good in ("#000000", "#aBcDeF"):
            self.assertTrue(ct.is_hex_color(good))
        for bad in ("000000", "#00000", "#0000000", "#GG0000", "", None, 5):
            self.assertFalse(ct.is_hex_color(bad))


if __name__ == "__main__":
    unittest.main()
