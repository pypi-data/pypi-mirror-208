import unittest
import os

from fastforward.model_for_cross_encoding import ModelForCrossEncoding


class ModelForCrossEncodingTest(unittest.TestCase):

    base_path = os.path.dirname(os.path.abspath(__file__))

    def test_encode(self):
        encoder = ModelForCrossEncoding(
            f"{self.base_path}/dummy", use_sigmoid=True)
        self.assertTrue(encoder(("A", "B")) is not None)
        self.assertTrue(encoder(("A", "B")) is not None)

    def test_encode_batch(self):
        encoder = ModelForCrossEncoding(
            f"{self.base_path}/dummy", use_sigmoid=True)
        self.assertEqual(len(encoder([("A", "B"), ("A", "B")])), 2)
        self.assertEqual(len(encoder([("A", "B"), ("A", "B")])), 2)

    def test_encode_batch_with_different_sequence_lengths(self):
        encoder = ModelForCrossEncoding(
            f"{self.base_path}/dummy", use_sigmoid=True)
        self.assertEqual(len(encoder([("A", "B"), ("A", "B")])), 2)
        self.assertEqual(len(encoder([("A", "B C"), ("A", "B C D E")])), 2)
