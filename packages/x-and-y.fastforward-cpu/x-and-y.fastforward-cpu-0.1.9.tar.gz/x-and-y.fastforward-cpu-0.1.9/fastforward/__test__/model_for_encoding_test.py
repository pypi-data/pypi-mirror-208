import unittest
import os
from fastforward.model_for_encoding import ModelForEncoding


class ModelForEncodingTest(unittest.TestCase):

    base_path = os.path.dirname(os.path.abspath(__file__))

    def test_encode(self):
        encoder = ModelForEncoding(f"{self.base_path}/dummy")
        self.assertTrue(encoder("A") is not None)

    def test_encode_batch(self):
        encoder = ModelForEncoding(f"{self.base_path}/dummy")
        self.assertEqual(len(encoder(["A", "B C D"])), 2)
