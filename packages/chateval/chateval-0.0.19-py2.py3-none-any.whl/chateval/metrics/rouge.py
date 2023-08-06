from __future__ import annotations

from dataclasses import dataclass

import evaluate
import numpy as np

from chateval.metrics.metric import Metric, MetricConfig


@dataclass
class RougeConfig(MetricConfig):
    name = "rouge"
    variety: str = "rouge1"

    def to_metric(self) -> Rouge:
        return Rouge(self)


class Rouge(Metric):
    def __init__(self, config: RougeConfig):
        self.config = config
        self.evaluator = evaluate.load(self.config.name)

    def compute(self, dataset: list[dict], predictions: list[str]) -> dict:

        results = self.evaluator.compute(
            predictions=predictions,
            references=[sample["references"] for sample in dataset],
            use_aggregator=False,
            rouge_types=[self.config.variety],
        )

        return {
            "value": np.mean(results[self.config.variety]),
            "sample_values": results[self.config.variety],
        }
