from __future__ import annotations

from dataclasses import dataclass
import logging
import os
from typing import Optional

from tqdm import tqdm

from chateval.kernels.openai import OpenAIChat, OpenAIChatConfig
from chateval.metrics.metric import Metric, MetricConfig
from chateval.metrics.protocols.utils import PROTOCOLS_PATH
from chateval.utils.prompt_utils import format_necessary
from chateval.utils.py_util import (
    dict_to_str,
    get_answer_from_data,
    list_to_str,
    load_yaml,
    NO_ANSWER,
)

logging.basicConfig(level=logging.WARNING)


@dataclass
class GPTScoreConfig(MetricConfig):
    name: str
    protocol_config_path: str
    criteria: Optional[str] = None
    eval_model_config: OpenAIChatConfig = OpenAIChatConfig(
        model_name="gpt-3.5-turbo",
    )

    def __post_init__(self):
        self.protocol_config = load_yaml(self.protocol_config_path)


class GPTScore(Metric):
    def __init__(self, config: GPTScoreConfig):
        self.config = config
        self.evaluator = OpenAIChat(config.eval_model_config)

    def _get_instantiated_prompt(self, sample: dict, prediction: str) -> str:
        prompt = self.config.protocol_config["prompt"]
        prompt_args = {}
        # instantiate prompt with criteria
        if self.config.criteria is not None:
            if self.config.criteria not in self.config.protocol_config["criteria"]:
                raise ValueError(
                    f"Criteria {self.config.criteria} not found in protocol config."
                )
            criteria_content = self.config.protocol_config["criteria"][
                self.config.criteria
            ]
            # likert protocol
            if self.config.protocol_config["eval_type"] == "cot_likert":
                criteria_content = dict_to_str(criteria_content)
                prompt_args["choices"] = ", ".join(
                    list(self.config.protocol_config["choice_scores"].keys())
                )

            prompt_args["criteria"] = criteria_content
        # instantiate prompt with input and completion
        # TODO(pfliu-nlp): the for loop is problematic
        for input_slot_name, output_slot_name in self.config.protocol_config[
            "input_outputs"
        ].items():
            prompt_args[input_slot_name] = sample[input_slot_name]
            prompt_args[output_slot_name] = prediction

        instantiated_prompt = format_necessary(prompt, **prompt_args)

        return instantiated_prompt

    def _get_instantiated_prompt_pairwise(
        self,
        sample: dict,
        prediction_1: str,
        prediction_2: str,
    ) -> str:
        prompt = self.config.protocol_config["prompt"]
        prompt_args = {}
        # instantiate prompt with criteria
        if self.config.criteria is not None:
            if self.config.criteria not in self.config.protocol_config["criteria"]:
                raise ValueError(
                    f"Criteria {self.config.criteria} not found in protocol config."
                )

            criteria_content = self.config.protocol_config["criteria"][
                self.config.criteria
            ]
            prompt_args["criteria"] = criteria_content

        # instantiate prompt with input and completion
        # TODO(pfliu-nlp): the for loop is problematic

        for input_slot_name, output_slot_names in self.config.protocol_config[
            "input_outputs"
        ].items():
            prompt_args[input_slot_name] = sample[input_slot_name]
            prompt_args[output_slot_names[0]] = prediction_1
            prompt_args[output_slot_names[1]] = prediction_2

        prompt_instantiated = format_necessary(prompt, **prompt_args)

        return prompt_instantiated

    def compute_sample_batch(self, samples: list[dict], predictions: list[str]) -> dict:

        instantiated_prompts = [
            self._get_instantiated_prompt(sample, prediction)
            for sample, prediction in zip(samples, predictions)
        ]

        results = self.evaluator.execute_batch(
            [
                [
                    {"role": "user", "content": prompt},
                ]
                for prompt in instantiated_prompts
            ]
        )

        eval_infos = []
        for result, prompt in zip(results, instantiated_prompts):
            extracted_result = get_answer_from_data(
                result, list(self.config.protocol_config["choice_scores"].keys())
            )

            if extracted_result in self.config.protocol_config["choice_scores"]:
                eval_infos.append(
                    {
                        "value": self.config.protocol_config["choice_scores"][
                            extracted_result
                        ],
                        "detail": {
                            "prompt": prompt,
                            "judgment": result,
                        },
                    }
                )
            else:
                eval_infos.append(
                    {
                        "value": -1,
                        "detail": {
                            "prompt": prompt,
                            "judgment": result,
                        },
                    }
                )

        return eval_infos

    def compute(
        self, dataset: list[dict], predictions: list[str], batch_size: int = 10
    ) -> dict:

        # check if the dataset contains id filed, this is useful for debugging
        if not all([d.get("id") is not None for d in dataset]):
            for idx, d in enumerate(dataset):
                dataset[idx]["id"] = idx

        # batch samples
        batched_samples = []
        batched_predictions = []
        n_batch = len(dataset) // batch_size
        batched_ids = []
        for i in range(n_batch):
            batched_samples.append(dataset[i * batch_size : (i + 1) * batch_size])
            batched_predictions.append(
                predictions[i * batch_size : (i + 1) * batch_size]
            )
            batched_ids.append(
                [d["id"] for d in dataset[i * batch_size : (i + 1) * batch_size]]
            )
        if len(dataset) % batch_size != 0:
            batched_samples.append(dataset[n_batch * batch_size :])
            batched_predictions.append(predictions[n_batch * batch_size :])
            batched_ids.append([d["id"] for d in dataset[n_batch * batch_size :]])

        # compute
        results = []
        data_ids = []

        for samples, prediction, ids in zip(
            tqdm(batched_samples), batched_predictions, batched_ids
        ):
            try:
                eval_infos = self.compute_sample_batch(samples, prediction)
                results.extend(eval_infos)
            except Exception as e:
                logging.warning(f"Error in computing GPTScore: {e}")
                results.extend([None] * len(samples))
            data_ids.extend(ids)

        scores = [result["value"] if result is not None else None for result in results]
        details = [
            result["detail"] if result is not None else None for result in results
        ]

        value = 0
        no_score = 0
        for score in scores:
            if score is not None and score >= 0:
                value += score
            else:
                no_score += 1

        value = 0 if len(scores) - no_score == 0 else value / (len(scores) - no_score)
        return {
            "value": value,
            "no_score": no_score,
            "sample_values": scores,
            "details": details,
            "ids": data_ids,
        }

    def compare(
        self,
        dataset: list[dict],
        predictions_1: list[str],
        predictions_2: list[str],
        batch_size: int = 10,
    ) -> dict:

        # check if the dataset contains id filed, this is useful for debugging
        if not all([d.get("id") is not None for d in dataset]):
            for idx, d in enumerate(dataset):
                dataset[idx]["id"] = idx

        # batch samples
        batched_samples = []
        batched_predictions_1 = []
        batched_predictions_2 = []
        n_batch = len(dataset) // batch_size
        batched_ids = []
        for i in range(n_batch):
            batched_samples.append(dataset[i * batch_size : (i + 1) * batch_size])
            batched_predictions_1.append(
                predictions_1[i * batch_size : (i + 1) * batch_size]
            )
            batched_predictions_2.append(
                predictions_2[i * batch_size : (i + 1) * batch_size]
            )
            batched_ids.append(
                [d["id"] for d in dataset[i * batch_size : (i + 1) * batch_size]]
            )
        if len(dataset) % batch_size != 0:
            batched_samples.append(dataset[n_batch * batch_size :])
            batched_predictions_1.append(predictions_1[n_batch * batch_size :])
            batched_predictions_2.append(predictions_2[n_batch * batch_size :])
            batched_ids.append([d["id"] for d in dataset[n_batch * batch_size :]])

        # compute
        results = []
        data_ids = []

        for samples, prediction_1, prediction_2, ids in zip(
            tqdm(batched_samples),
            batched_predictions_1,
            batched_predictions_2,
            batched_ids,
        ):
            try:
                eval_infos = self.compare_sample_batch(
                    samples,
                    prediction_1,
                    prediction_2,
                )
                results.extend(eval_infos)
            except Exception as e:
                logging.warning(f"Error in computing GPTScore: {e}")
                results.extend([None] * len(samples))
            data_ids.extend(ids)

        scores = [result["value"] if result is not None else None for result in results]
        details = [
            result["detail"] if result is not None else None for result in results
        ]

        value = 0
        no_score = 0
        for score in scores:
            if score is not None:
                value += score
            else:
                no_score += 1

        value = 0 if len(scores) - no_score == 0 else value / (len(scores) - no_score)
        return {
            "value": value,
            "no_score": no_score,
            "sample_values": scores,
            "details": details,
            "ids": data_ids,
        }

    def compare_sample_batch(
        self, samples: dict, predictions_1: str, predictions_2: str
    ) -> dict:

        instantiated_prompts = [
            self._get_instantiated_prompt_pairwise(sample, prediction_1, prediction_2)
            for sample, prediction_1, prediction_2 in zip(
                samples, predictions_1, predictions_2
            )
        ]

        results = self.evaluator.execute_batch(
            [
                [
                    {"role": "user", "content": prompt},
                ]
                for prompt in instantiated_prompts
            ]
        )

        eval_infos = []
        for result, prompt in zip(results, instantiated_prompts):
            extracted_result = get_answer_from_data(
                result, list(self.config.protocol_config["choice_scores"].keys())
            )

            if extracted_result in self.config.protocol_config["choice_scores"]:
                eval_infos.append(
                    {
                        "value": self.config.protocol_config["choice_scores"][
                            extracted_result
                        ],
                        "detail": {
                            "prompt": prompt,
                            "judgment": result,
                        },
                    }
                )
            else:
                eval_infos.append(
                    {
                        "value": 0,
                        "detail": {
                            "prompt": prompt,
                            "judgment": result,
                        },
                    }
                )

        return eval_infos

    def rank(
        self,
        dataset: list[dict],
        predictions_list: list[list[str]],
    ) -> dict:
        results = []
        for sample, predictions in zip(tqdm(dataset), predictions_list):
            try:
                out = self.rank_sample(sample, predictions)
            except (ValueError, TypeError, RuntimeError) as e:
                logging.warning(f"Error in computing GPTScore: {e}")
                out = None
            results.append(out)
        scores = [result["value"] if result is not None else None for result in results]
        details = [
            result["detail"] if result is not None else None for result in results
        ]

        dict_sys_choice = {}
        no_score = 0
        for score in scores:
            if score is not None and score != NO_ANSWER:
                if score not in dict_sys_choice:
                    dict_sys_choice[score] = 1
                else:
                    dict_sys_choice[score] += 1
            else:
                no_score += 1

        # get the most frequent choice
        value = max(dict_sys_choice, key=dict_sys_choice.get)

        return {
            "value": value,
            "no_score": no_score,
            "sample_values": scores,
            "details": details,
        }

    def rank_sample(self, sample: dict, predictions: list[str]) -> dict:

        prompt = self.config.protocol_config["prompt"]
        prompt_args = {}
        # instantiate prompt with criteria
        if self.config.criteria is not None:
            if self.config.criteria not in self.config.protocol_config["criteria"]:
                raise ValueError(
                    f"Criteria {self.config.criteria} not found in protocol config."
                )

            criteria_content = self.config.protocol_config["criteria"][
                self.config.criteria
            ]
            prompt_args["criteria"] = criteria_content

        for input_slot_name, output_slot_name in self.config.protocol_config[
            "input_outputs"
        ].items():
            prompt_args[input_slot_name] = sample[input_slot_name]
            prompt_args[output_slot_name] = list_to_str(predictions)

        prompt_args["n"] = len(predictions)

        prompt_instantiated = format_necessary(prompt, **prompt_args)
        result = self.evaluator.execute(
            [
                {"role": "user", "content": prompt_instantiated},
            ]
        )

        choices = [str(i + 1) for i in range(len(predictions))]
        extracted_result = get_answer_from_data(result, choices)

        if extracted_result in choices:
            return {
                "value": extracted_result,
                "detail": {
                    "prompt": prompt_instantiated,
                    "judgment": result,
                },
            }
        else:
            return {
                "value": NO_ANSWER,
                "detail": {
                    "prompt": prompt_instantiated,
                    "judgment": result,
                },
            }


_GPT_METRICS: [str, Metric] = {
    "generic_bool/relevance": GPTScore(
        GPTScoreConfig(
            name="generic_bool/relevance",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_bool.yaml"),
            criteria="relevance",
        ),
    ),
    "generic_bool/coherence": GPTScore(
        GPTScoreConfig(
            name="generic_bool/coherence",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_bool.yaml"),
            criteria="coherence",
        ),
    ),
    "generic_bool/helpfulness": GPTScore(
        GPTScoreConfig(
            name="generic_bool/helpfulness",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_bool.yaml"),
            criteria="helpfulness",
        ),
    ),
    "generic_bool/grammar": GPTScore(
        GPTScoreConfig(
            name="generic_bool/grammar",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_bool.yaml"),
            criteria="grammar",
        ),
    ),
    "generic_bool/harmlessness": GPTScore(
        GPTScoreConfig(
            name="generic_bool/harmlessness",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_bool.yaml"),
            criteria="harmlessness",
        ),
    ),
    "blenderbot2_bool/relevance": GPTScore(
        GPTScoreConfig(
            name="blenderbot2_bool/relevance",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "blenderbot2_bool.yaml"),
            criteria="relevance",
        ),
    ),
    "blenderbot2_bool/helpfulness": GPTScore(
        GPTScoreConfig(
            name="blenderbot2_bool/helpfulness",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "blenderbot2_bool.yaml"),
            criteria="helpfulness",
        ),
    ),
    "blenderbot2_bool/factuality": GPTScore(
        GPTScoreConfig(
            name="blenderbot2_bool/factuality",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "blenderbot2_bool.yaml"),
            criteria="factuality",
        ),
    ),
    "generic_likert/helpfulness": GPTScore(
        GPTScoreConfig(
            name="generic_likert/helpfulness",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_likert.yaml"),
            criteria="helpfulness",
        ),
    ),
    "generic_likert/relevance": GPTScore(
        GPTScoreConfig(
            name="generic_likert/relevance",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_likert.yaml"),
            criteria="relevance",
        ),
    ),
    "generic_likert/coherence": GPTScore(
        GPTScoreConfig(
            name="generic_likert/coherence",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_likert.yaml"),
            criteria="coherence",
        ),
    ),
    "generic_likert/harmlessness": GPTScore(
        GPTScoreConfig(
            name="generic_likert/harmlessness",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_likert.yaml"),
            criteria="harmlessness",
        ),
    ),
    "generic_pairwise/helpfulness": GPTScore(
        GPTScoreConfig(
            name="generic_pairwise/coherence",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_pairwise.yaml"),
            criteria="helpfulness",
        ),
    ),
    "generic_pairwise/relevance": GPTScore(
        GPTScoreConfig(
            name="generic_pairwise/relevance",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_pairwise.yaml"),
            criteria="relevance",
        ),
    ),
    "generic_pairwise/coherence": GPTScore(
        GPTScoreConfig(
            name="generic_pairwise/coherence",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_pairwise.yaml"),
            criteria="coherence",
        ),
    ),
    "generic_pairwise/harmlessness": GPTScore(
        GPTScoreConfig(
            name="generic_pairwise/harmlessness",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_pairwise.yaml"),
            criteria="harmlessness",
        ),
    ),
    "generic_rank/helpfulness": GPTScore(
        GPTScoreConfig(
            name="generic_rank/helpfulness",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_rank.yaml"),
            criteria="helpfulness",
        ),
    ),
    "generic_rank/relevance": GPTScore(
        GPTScoreConfig(
            name="generic_rank/relevance",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_rank.yaml"),
            criteria="relevance",
        ),
    ),
    "generic_rank/coherence": GPTScore(
        GPTScoreConfig(
            name="generic_rank/coherence",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_rank.yaml"),
            criteria="coherence",
        ),
    ),
    "generic_rank/harmlessness": GPTScore(
        GPTScoreConfig(
            name="generic_rank/harmlessness",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "generic_rank.yaml"),
            criteria="harmlessness",
        ),
    ),
    "llama_likert/helpfulness": GPTScore(
        GPTScoreConfig(
            name="lama_likert/helpfulness",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "llama_likert.yaml"),
            criteria="helpfulness",
        ),
    ),
    "debate_overall/relevance": GPTScore(
        GPTScoreConfig(
            name="debate_overall/relevance",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "debate_overall.yaml"),
            criteria="relevance",
        ),
    ),
    "debate_overall/persuasiveness": GPTScore(
        GPTScoreConfig(
            name="debate_overall/persuasiveness",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "debate_overall.yaml"),
            criteria="persuasiveness",
        ),
    ),
    "debate_overall/responsiveness": GPTScore(
        GPTScoreConfig(
            name="debate_overall/responsiveness",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "debate_overall.yaml"),
            criteria="responsiveness",
        ),
    ),
    "debate_overall/coherence": GPTScore(
        GPTScoreConfig(
            name="debate_overall/coherence",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "debate_overall.yaml"),
            criteria="coherence",
        ),
    ),
    "generic_bool_safety/insult": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/insult",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="insult",
        ),
    ),
    "generic_bool_safety/physical_harm": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/physical_harm",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="physical_harm",
        ),
    ),
    "generic_bool_safety/unfairness_and_discrimination": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/unfairness_and_discrimination",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="unfairness_and_discrimination",
        ),
    ),
    "generic_bool_safety/mental_health": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/mental_health",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="mental_health",
        ),
    ),
    "generic_bool_safety/crimes_and_illegal_activities": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/crimes_and_illegal_activities",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="crimes_and_illegal_activities",
        ),
    ),
    "generic_bool_safety/privacy_and_property": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/privacy_and_property",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="privacy_and_property",
        ),
    ),
    "generic_bool_safety/ethics_and_morality": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/ethics_and_morality",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="ethics_and_morality",
        ),
    ),
    "generic_bool_safety/goal_hijacking": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/goal_hijacking",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="goal_hijacking",
        ),
    ),
    "generic_bool_safety/unsafe_instruction_topic": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/unsafe_instruction_topic",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="unsafe_instruction_topic",
        ),
    ),
    "generic_bool_safety/prompt_leaking": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/prompt_leaking",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="prompt_leaking",
        ),
    ),
    "generic_bool_safety/inquiry_with_unsafe_opinion": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/inquiry_with_unsafe_opinion",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="inquiry_with_unsafe_opinion",
        ),
    ),
    "generic_bool_safety/role_play_instruction": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/role_play_instruction",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="role_play_instruction",
        ),
    ),
    "generic_bool_safety/reverse_exposure": GPTScore(
        GPTScoreConfig(
            name="generic_bool_safety/reverse_exposure",
            protocol_config_path=os.path.join(
                PROTOCOLS_PATH, "generic_bool_safety.yaml"
            ),
            criteria="reverse_exposure",
        ),
    ),
    "lima_pairwise/helpfulness-gpt4": GPTScore(
        GPTScoreConfig(
            name="lima_pairwise/helpfulness-gpt4",
            protocol_config_path=os.path.join(PROTOCOLS_PATH, "lima_pairwise.yaml"),
            criteria="helpfulness",
            eval_model_config=OpenAIChatConfig(
                model_name="gpt-4",
                max_tokens=512,
                temperature=0,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                n=1,
            ),
        ),
    ),
}
