# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
File containing HF model related functions
"""
from pathlib import Path
from dataclasses import dataclass

from typing import Union, Optional, List, Tuple

import torch

from transformers.models.auto.modeling_auto import (
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoModelForSeq2SeqLM,
    AutoModelForQuestionAnswering
)
from transformers.utils import WEIGHTS_NAME
from transformers.modeling_utils import PreTrainedModel

from azureml.acft.accelerator.utils.logging_utils import get_logger_app

from .config import AzuremlAutoConfig


logger = get_logger_app()


class AzuremlAutoModelForSequenceClassification(AutoModelForSequenceClassification):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> Tuple[PreTrainedModel, str, List[str]]:
        """Apply model specific hacks before calling the Base tokenizer"""

        # Initialize the config
        problem_type = kwargs.pop("problem_type", None)
        num_labels = kwargs.pop("num_labels", None)
        label2id = kwargs.pop("label2id", None)
        id2label = kwargs.pop("id2label", None)

        config = AzuremlAutoConfig.from_pretrained(
            hf_model_name_or_path,
            problem_type=problem_type,
            num_labels=num_labels,
            id2label=id2label,
            label2id=label2id,
            output_attentions=False,
            output_hidden_states=False,
        )

        # Initialize the model
        resume_from_checkpoint = kwargs.get("resume_from_checkpoint", None)
        model_type = AzuremlAutoConfig.get_model_type(config)
        if resume_from_checkpoint:
            # First load the state dictionary to find the keys of pretrained weights
            # and delete it so that the memory is efficiently used
            weights_path = Path(hf_model_name_or_path, WEIGHTS_NAME)
            pretrained_weights_state_dict = torch.load(weights_path, map_location="cpu")
            pretrained_weights_keys = set(pretrained_weights_state_dict.keys())
            del pretrained_weights_state_dict

            # will load the model using resume_from_checkpoint of HF TrainingArgs
            # so instantiating model with random weights for now
            model = super().from_config(config=config)

            # find the newly initialized layers in the model
            missing_keys = set(model.state_dict().keys()).difference(pretrained_weights_keys)

            return model, model_type, list(missing_keys)
        else:
            model, model_loading_metadata = super().from_pretrained(
                hf_model_name_or_path,
                config=config,
                ignore_mismatched_sizes=kwargs.pop("ignore_mismatched_sizes", False),
                output_loading_info=True,
            )

            return model, model_type, model_loading_metadata["missing_keys"]


class AzuremlAutoModelForTokenClassification(AutoModelForTokenClassification):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> Tuple[PreTrainedModel, str, List[str]]:
        """Apply model specific hacks before calling the Base tokenizer"""

        # Initialize the config
        problem_type = kwargs.pop("problem_type", None)
        num_labels = kwargs.pop("num_labels", None)
        label2id = kwargs.pop("label2id", None)
        id2label = kwargs.pop("id2label", None)

        config = AzuremlAutoConfig.from_pretrained(
            hf_model_name_or_path,
            problem_type=problem_type,
            num_labels=num_labels,
            id2label=id2label,
            label2id=label2id,
            output_attentions=False,
            output_hidden_states=False,
        )

        # Initialize the model
        resume_from_checkpoint = kwargs.get("resume_from_checkpoint", None)
        model_type = AzuremlAutoConfig.get_model_type(config)
        if resume_from_checkpoint:
            # First load the state dictionary to find the keys of pretrained weights
            # and delete it so that the memory is efficiently used
            weights_path = Path(hf_model_name_or_path, WEIGHTS_NAME)
            pretrained_weights_state_dict = torch.load(weights_path, map_location="cpu")
            pretrained_weights_keys = set(pretrained_weights_state_dict.keys())
            del pretrained_weights_state_dict

            # will load the model using resume_from_checkpoint of HF TrainingArgs
            # so instantiating model with random weights for now
            model = super().from_config(config=config)

            # find the newly initialized layers in the model
            missing_keys = set(model.state_dict().keys()).difference(pretrained_weights_keys)

            return model, model_type, list(missing_keys)
        else:
            model, model_loading_metadata = super().from_pretrained(
                hf_model_name_or_path,
                config=config,
                ignore_mismatched_sizes=kwargs.pop("ignore_mismatched_sizes", False),
                output_loading_info=True,
            )
            return model, model_type, model_loading_metadata["missing_keys"]


class AzuremlAutoModelForSummarization(AutoModelForSeq2SeqLM):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> Tuple[PreTrainedModel, str, List[str]]:
        """Apply model specific hacks before calling the Base tokenizer"""

        # Initialize the config
        problem_type = kwargs.pop("problem_type", None)
        label2id = kwargs.pop("label2id", None)
        id2label = kwargs.pop("id2label", None)
        # not None for t5 models
        tok_prefix = kwargs.pop("tok_prefix", None)

        config_params = {
            "problem_type": problem_type,
            "id2label": id2label,
            "label2id": label2id,
            "output_attentions": False,
            "output_hidden_states": False,
        }

        if tok_prefix is not None:
            config_params["prefix"] = tok_prefix

        config = AzuremlAutoConfig.from_pretrained(hf_model_name_or_path, **config_params)

        # summarization task specific params
        task_specific_key = "summarization"
        task_specific_params = {
            "early_stopping": False,
            "length_penalty": 1.0,
            "min_length": 0,
            "no_repeat_ngram_size": 0,
            "num_beams": 1,
        }

        if config.task_specific_params is None:
            config.task_specific_params = {}

        if task_specific_key in config.task_specific_params:
            config.task_specific_params[task_specific_key].update(task_specific_params)
        else:
            config.task_specific_params[task_specific_key] = task_specific_params

        # Initialize the model
        resume_from_checkpoint = kwargs.get("resume_from_checkpoint", None)
        model_type = AzuremlAutoConfig.get_model_type(config)
        if resume_from_checkpoint:
            # First load the state dictionary to find the keys of pretrained weights
            # and delete it so that the memory is efficiently used
            weights_path = Path(hf_model_name_or_path, WEIGHTS_NAME)
            pretrained_weights_state_dict = torch.load(weights_path, map_location="cpu")
            pretrained_weights_keys = set(pretrained_weights_state_dict.keys())
            del pretrained_weights_state_dict

            # will load the model using resume_from_checkpoint of HF TrainingArgs
            # so instantiating model with random weights for now
            model = super().from_config(config=config)

            # find the newly initialized layers in the model
            missing_keys = set(model.state_dict().keys()).difference(pretrained_weights_keys)

            return model, model_type, list(missing_keys)
        else:
            model, model_loading_metadata = super().from_pretrained(
                hf_model_name_or_path,
                config=config,
                ignore_mismatched_sizes=kwargs.pop("ignore_mismatched_sizes", False),
                output_loading_info=True,
            )
            return model, model_type, model_loading_metadata["missing_keys"]


class AzuremlAutoModelForTranslation(AutoModelForSeq2SeqLM):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> Tuple[PreTrainedModel, str, List[str]]:
        """Apply model specific hacks before calling the Base tokenizer"""

        # Initialize the config
        problem_type = kwargs.pop("problem_type", None)
        label2id = kwargs.pop("label2id", None)
        id2label = kwargs.pop("id2label", None)
        source_lang = kwargs.pop("source_lang", None)
        target_lang = kwargs.pop("target_lang", None)
        # not None for t5 models
        tok_prefix = kwargs.pop("tok_prefix", None)
        # not None for Mbart models
        decoder_start_token_id = kwargs.pop("decoder_start_token_id", None)

        config_params = {
            "problem_type": problem_type,
            "id2label": id2label,
            "label2id": label2id,
            "output_attentions": False,
            "output_hidden_states": False,
        }

        if tok_prefix is not None:
            config_params["prefix"] = tok_prefix
        if decoder_start_token_id is not None:
            config_params["decoder_start_token_id"] = decoder_start_token_id

        config = AzuremlAutoConfig.from_pretrained(hf_model_name_or_path, **config_params)

        task_specific_key = f"translation_{source_lang}_to_{target_lang}"
        task_specific_params = {
            "early_stopping": False,
            "num_beams": 1,
        }

        if config.task_specific_params is None:
            config.task_specific_params = {}

        if task_specific_key in config.task_specific_params:
            config.task_specific_params[task_specific_key].update(task_specific_params)
        else:
            config.task_specific_params[task_specific_key] = task_specific_params

        # Initialize the model
        resume_from_checkpoint = kwargs.get("resume_from_checkpoint", None)
        model_type = AzuremlAutoConfig.get_model_type(config)
        if resume_from_checkpoint:
            # First load the state dictionary to find the keys of pretrained weights
            # and delete it so that the memory is efficiently used
            weights_path = Path(hf_model_name_or_path, WEIGHTS_NAME)
            pretrained_weights_state_dict = torch.load(weights_path, map_location="cpu")
            pretrained_weights_keys = set(pretrained_weights_state_dict.keys())
            del pretrained_weights_state_dict

            # will load the model using resume_from_checkpoint of HF TrainingArgs
            # so instantiating model with random weights for now
            model = super().from_config(config=config)

            # find the newly initialized layers in the model
            missing_keys = set(model.state_dict().keys()).difference(pretrained_weights_keys)

            return model, model_type, list(missing_keys)
        else:
            model, model_loading_metadata = super().from_pretrained(
                hf_model_name_or_path,
                config=config,
                ignore_mismatched_sizes=kwargs.pop("ignore_mismatched_sizes", False),
                output_loading_info=True,
            )
            return model, model_type, model_loading_metadata["missing_keys"]


class AzuremlAutoModelForQnA(AutoModelForQuestionAnswering):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> Tuple[PreTrainedModel, str, List[str]]:
        """Apply model specific hacks before calling the Base tokenizer"""

        # Initialize the config
        problem_type = kwargs.pop("problem_type", None)
        label2id = kwargs.pop("label2id", None)
        id2label = kwargs.pop("id2label", None)

        config = AzuremlAutoConfig.from_pretrained(
            hf_model_name_or_path,
            problem_type=problem_type,
            # id2label=id2label,
            # label2id=label2id,
            output_attentions=False,
            output_hidden_states=False,
        )

        # Initialize the model
        resume_from_checkpoint = kwargs.get("resume_from_checkpoint", None)
        model_type = AzuremlAutoConfig.get_model_type(config)
        if resume_from_checkpoint:
            # First load the state dictionary to find the keys of pretrained weights
            # and delete it so that the memory is efficiently used
            weights_path = Path(hf_model_name_or_path, WEIGHTS_NAME)
            pretrained_weights_state_dict = torch.load(weights_path, map_location="cpu")
            pretrained_weights_keys = set(pretrained_weights_state_dict.keys())
            del pretrained_weights_state_dict

            # will load the model using resume_from_checkpoint of HF TrainingArgs
            # so instantiating model with random weights for now
            model = super().from_config(config=config)

            # find the newly initialized layers in the model
            missing_keys = set(model.state_dict().keys()).difference(pretrained_weights_keys)

            return model, model_type, list(missing_keys)
        else:
            model, model_loading_metadata = super().from_pretrained(
                hf_model_name_or_path,
                config=config,
                ignore_mismatched_sizes=kwargs.pop("ignore_mismatched_sizes", False),
                output_loading_info=True,
            )
            return model, model_type, model_loading_metadata["missing_keys"]
