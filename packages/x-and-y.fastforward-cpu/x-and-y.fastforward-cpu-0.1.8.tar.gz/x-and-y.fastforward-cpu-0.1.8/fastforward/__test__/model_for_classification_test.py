import unittest
import os

from fastforward.model_for_sequence_classification import ModelForSequenceClassification


class ModelForEncodingTest(unittest.TestCase):

    base_path = os.path.dirname(os.path.abspath(__file__))

    def test_classification(self):
        model = ModelForSequenceClassification(f"{self.base_path}/dummy")
        self.assertTrue(model("The product is great!") is not None)

    def test_classification_batch(self):
        model = ModelForSequenceClassification(f"{self.base_path}/dummy")
        self.assertEqual(
            len(model(["The product is great!", "the product is bad!"])), 2)
