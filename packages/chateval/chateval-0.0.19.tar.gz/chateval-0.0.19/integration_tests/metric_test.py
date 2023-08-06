import unittest

from chateval.metrics import get_metric
from chateval.metrics.rouge import Rouge, RougeConfig


class MyTestCase(unittest.TestCase):
    def test_ROUGE(self):

        dataset = [{"references": ["hello world"]}, {"references": ["hello world"]}]
        predictions = ["hello world", "hello world"]

        rouge = Rouge(RougeConfig(name="rouge", variety="rouge1"))

        result = rouge.compute(dataset, predictions)

        self.assertEqual(result["value"], 1.0)
        self.assertEqual(result["sample_values"], [1.0, 1.0])

    def test_get_metric(self):
        metric = get_metric("rouge1")
        self.assertIsInstance(metric, Rouge)

    def test_count(self):
        dataset = [{"references": ["hello world"]}, {"references": ["hello world"]}]
        predictions = ["hello world", "hello world"]

        metric = get_metric("count")
        result = metric.compute(dataset, predictions)

        self.assertEqual(result["value"], 2.0)
        self.assertEqual(result["sample_values"], [2.0, 2.0])

    def test_accuracy(self):
        dataset = [{"references": ["Yes"]}, {"references": ["Yes"]}]
        predictions = ["Yes", "No"]

        metric = get_metric("accuracy")
        result = metric.compute(dataset, predictions)

        print(result)

        self.assertEqual(result["value"], 0.5)
        self.assertEqual(result["sample_values"], [1, 0])


if __name__ == "__main__":
    unittest.main()
