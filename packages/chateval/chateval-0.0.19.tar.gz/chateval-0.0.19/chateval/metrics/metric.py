from __future__ import annotations

import abc
from dataclasses import dataclass


@dataclass
class MetricConfig:
    name: str

    @abc.abstractmethod
    def to_metric(self) -> Metric:
        return Metric(self)


class Metric:
    def compute(self, predictions: list[str], dataset: list[dict]) -> dict:
        raise NotImplementedError()
