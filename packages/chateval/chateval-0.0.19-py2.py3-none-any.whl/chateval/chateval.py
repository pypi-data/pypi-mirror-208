from __future__ import annotations

import json
import warnings

import yaml

from chateval.constants.models import ModelType
from chateval.metrics import get_metric


class ChatEval:
    def __init__(self, config_directory: str = None, sub_scenario: str = None):
        self.config_directory = config_directory
        self.sub_scenario = sub_scenario
        self.config = self._config()
        self.dataset = self._dataset()
        self.metrics = self._metrics()

    def _config_name(self):
        raise NotImplementedError()

    def _config(self):
        return self.load_config(f"{self.config_directory}/config.yaml")

    def _dataset(self):

        sub_scenario = (
            self.config["default_setting"]
            if self.sub_scenario is None
            else self.sub_scenario
        )
        settings = self.config["settings"]
        data_path = settings[sub_scenario]["dataset"]

        return self.load_dataset(f"{self.config_directory}/{data_path}")

    def _metrics(self):

        metrics = {
            metric_config["name"]: get_metric(metric_config["name"])
            for metric_config in self.config["metrics"]
        }

        return metrics

    def get_default_setting_config(self):
        return self.config["settings"][self.config["default_setting"]]

    def inference_one_sample(self, sample: dict) -> str:
        raise NotImplementedError()

    def inference_batch_samples(self, samples: list[dict]) -> list[str]:
        raise NotImplementedError()

    def evaluate(
        self, model: str | list[str], model_type: ModelType = ModelType.output
    ) -> dict:

        if model_type == ModelType.metric:
            return {
                name: metric.compute(self.dataset, metric_model=model)
                for name, metric in self.metrics.items()
            }
        elif model_type == ModelType.output:
            return {
                name: metric.compute(self.dataset, predictions=model)
                for name, metric in self.metrics.items()
            }
        else:
            raise ValueError(
                "The predictions should be either a list of string or a string"
            )

    def load_config(self, path: str) -> dict:
        # judge if the file is yaml, raise error if not
        if not path.endswith(".yaml") and not path.endswith(".yml"):
            raise ValueError("The config file should be yaml file")

        with open(path, "r") as yaml_file:
            yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        return yaml_data

    def load_dataset(self, path: str) -> list[dict]:
        """
        Load the dataset from the path
        Args:
            path: it should be a jsonl file

        Returns:
            a list of dict, each dict is a sample
        """

        # judge if the file is jsonl, raise error if not
        if not path.endswith(".jsonl"):
            raise ValueError("The dataset file should be jsonl file")
        warnings.warn("Dataset loaded from " + path)
        with open(path, "r") as f:
            dataset = [json.loads(line) for line in f]
        return dataset
