from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from chateval.metrics.metric import Metric, MetricConfig


@dataclass
class CountConfig(MetricConfig):
    name = "count"

    def to_metric(self) -> Count:
        return Count(self)


class Count(Metric):
    def __init__(self, config: CountConfig):
        self.config = config

    def compute(self, dataset: list[dict], predictions: list[str]) -> dict:

        # TODO(pfliu-nlp): we should use the tokenizer to get the number of tokens
        sample_lengths = [len(hypo.split(" ")) for hypo in predictions]

        return {"value": np.mean(sample_lengths), "sample_values": sample_lengths}
