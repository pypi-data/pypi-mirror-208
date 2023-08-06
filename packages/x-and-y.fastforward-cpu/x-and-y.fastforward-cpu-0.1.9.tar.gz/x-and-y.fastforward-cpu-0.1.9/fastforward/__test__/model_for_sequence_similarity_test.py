import unittest
import os
from fastforward.model_for_sequence_similarity import ModelForSequenceSimilarity


class ModelForSimilarityTest(unittest.TestCase):

    base_path = os.path.dirname(os.path.abspath(__file__))

    def test_encode(self):
        model = ModelForSequenceSimilarity(f"{self.base_path}/dummy")
        self.assertTrue(model(("A", "B")) is not None)

    def test_encode_batch(self):
        model = ModelForSequenceSimilarity(f"{self.base_path}/dummy")
        self.assertEqual(len(model([("A", "B"), ("A", "B")])), 2)
