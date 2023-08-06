from __future__ import annotations

import abc
import dataclasses
from dataclasses import dataclass
from typing import Any


@dataclass
class KernelConfig:
    @abc.abstractmethod
    def to_kernel(self) -> Kernel:
        return Kernel(self)

    @classmethod
    def from_dict(cls, data_dict: dict) -> Kernel:
        field_names = set(f.name for f in dataclasses.fields(cls))
        return cls(**{k: v for k, v in data_dict.items() if k in field_names})


class Kernel:
    def __init__(self, config: Any):
        self.config = config
