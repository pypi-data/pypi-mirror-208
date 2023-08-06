from __future__ import annotations

from chateval.metrics.accuracy import Accuracy, AccuracyConfig
from chateval.metrics.count import Count, CountConfig
from chateval.metrics.gptscore import _GPT_METRICS
from chateval.metrics.metric import Metric
from chateval.metrics.rouge import Rouge, RougeConfig

_METRICS: [str, Metric] = {
    "rouge1": Rouge(RougeConfig(name="rouge", variety="rouge1")),
    "rouge2": Rouge(RougeConfig(name="rouge", variety="rouge2")),
    "rougeL": Rouge(RougeConfig(name="rouge", variety="rougeL")),
    "count": Count(CountConfig(name="count")),
    "accuracy": Accuracy(AccuracyConfig(name="accuracy")),
}

_METRICS.update(_GPT_METRICS)


def get_metric(name: str) -> Metric:
    return _METRICS[name]
