from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from chateval.metrics.gptscore import _GPT_METRICS
from chateval.metrics.metric import Metric, MetricConfig


@dataclass
class AccuracyConfig(MetricConfig):
    name = "accuracy"
    meta_eval: bool = False

    def to_metric(self) -> Accuracy:
        return Accuracy(self)


class Accuracy(Metric):
    def __init__(self, config: AccuracyConfig):
        self.config = config

    def compute(
        self,
        dataset: list[dict],
        predictions: Optional[list[str]] = None,
        metric_model: Optional[str] = None,
    ) -> dict:

        if predictions is None and metric_model is None:
            raise ValueError("Either predictions or metric_model must be provided.")

        detailed_infos = None
        if metric_model is not None:
            prediction_infos = _GPT_METRICS[metric_model].compute(
                dataset, [x["completion"] for x in dataset]
            )
            predictions = [x for x in prediction_infos["sample_values"]]
            detailed_infos = [x for x in prediction_infos["details"]]

        if len(dataset) != len(predictions):
            raise ValueError("The number of samples and predictions do not match.")
        if len(dataset) == 0:
            raise ValueError("No dataset to compute.")

        values = []

        for sample, pred in zip(dataset, predictions):
            # TODO: only consider the first reference
            values.append(int(sample["references"][0] == pred))

        return {
            "value": sum(values) / len(values),
            "sample_values": values,
            "detailed_infos": detailed_infos,
        }
