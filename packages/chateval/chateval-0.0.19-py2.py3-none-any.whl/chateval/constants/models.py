"""Definition of different types of models."""
from __future__ import annotations

from enum import Enum


class ModelType(str, Enum):
    """Model types available in this tool."""

    api = "api"
    metric = "metric"
    output = "output"

    @staticmethod
    def list() -> list[str]:
        """Obtains string representations of all values.
        Returns:
            List of all values in str.
        """
        return list(map(lambda c: c.value, ModelType))
