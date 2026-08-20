import unittest

from PIL import Image, ImageFilter

from clarification import Options, clarify, sharpness_score


class ClarificationTests(unittest.TestCase):
    def setUp(self):
        self.image = Image.new("RGBA", (32, 32), (100, 100, 100, 255))
        for x in range(32):
            self.image.putpixel((x, 16), (240, 240, 240, 128))
            self.image.putpixel((16, x), (240, 240, 240, 128))

    def test_preserves_dimensions_and_alpha(self):
        result = clarify(self.image)
        self.assertEqual(result.size, self.image.size)
        self.assertEqual(result.getpixel((16, 16))[3], 128)

    def test_increases_detail_score(self):
        soft = self.image.filter(ImageFilter.GaussianBlur(2.0))
        result = clarify(soft, Options(amount=1.5, contrast=10))
        self.assertGreaterEqual(sharpness_score(result), sharpness_score(soft))


if __name__ == "__main__":
    unittest.main()
