import unittest

from clarification.ai import AIOptions


class AIProfileTests(unittest.TestCase):
    def test_portrait_eye_detail_profile(self):
        options = AIOptions.portrait()
        self.assertEqual(options.tile, 128)
        self.assertEqual(options.upscale, 4)
        self.assertAlmostEqual(options.face_weight, 0.50)
        self.assertAlmostEqual(options.eye_blend, 0.65)

    def test_default_options_are_safe_to_construct(self):
        options = AIOptions()
        self.assertAlmostEqual(options.face_weight, 0.50)
        self.assertGreaterEqual(options.eye_blend, 0.0)


if __name__ == '__main__':
    unittest.main()
