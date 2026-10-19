import unittest
from color_tool import Color, TEXT


class ColorTests(unittest.TestCase):
    def test_rgb_limits(self):
        self.assertEqual(Color(-20, 300, 16).to_hex(), "#00FF10")

    def test_full_hex_normalizes(self):
        self.assertEqual(Color.from_hex(" #aB09fF ").to_hex(), "#AB09FF")

    def test_short_hex_with_or_without_hash(self):
        for text in ("#a3f", "a3f"):
            self.assertEqual(Color.from_hex(text), Color(170, 51, 255))

    def test_invalid_characters_and_lengths(self):
        for value in ("", "#", "#12", "#1234", "#12345", "#1234567", "#12GG00", "#²²0000", "#１２0000", "red", "#12 345"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Color.from_hex(value)

    def test_rgb_round_trip_boundaries(self):
        for red in (0, 1, 127, 254, 255):
            for green in (0, 128, 255):
                for blue in (0, 128, 255):
                    color = Color(red, green, blue)
                    self.assertEqual(Color.from_hex(color.to_hex()), color)

    def test_translation_keys_match(self):
        self.assertEqual(set(TEXT["pl"]), set(TEXT["en"]))


if __name__ == "__main__":
    unittest.main()
