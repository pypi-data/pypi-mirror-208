# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------

"""
NLP NER
"""

import os
import json
from pathlib import Path
from argparse import Namespace

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field

import torch.nn as nn

from ....nlp_auto.tokenizer import AzuremlAutoTokenizer
from ....nlp_auto.config import AzuremlAutoConfig
from ....constants.constants import (
    DatasetSplit,
    SaveFileConstants,
    AzuremlConstants,
    MLFlowHFFlavourConstants,
    PreprocessArgsTemplate,
    Tasks,
    MLFlowHFFlavourTasks,
    STRING_DTYPES,
    TaskConstants,
    AutomlConstants,
)
from ....base_runner import BaseRunner

from ....utils.data_utils import AzuremlDataset
from ....utils.validation_utils import AzuremlValidatorMixin

from datasets.arrow_dataset import Dataset
from datasets import Sequence

import transformers
from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.data.data_collator import DataCollatorForTokenClassification
from transformers.hf_argparser import HfArgumentParser

from azureml.acft.accelerator.utils.logging_utils import get_logger_app
from azureml.acft.accelerator.utils.error_handling.exceptions import ValidationException
from azureml.acft.accelerator.utils.error_handling.error_definitions import PathNotFound, ValidationError
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

logger = get_logger_app()


@dataclass
class NLPNerPreprocessArgs(PreprocessArgsTemplate):
    # Specify the defaults for all new attributes of NerPreprocessArgs + inhertied attributes from
    # _PreprocessArgsTemplate here. Otherwise, there will be issues related to ordering of default and
    # non-default attributes

    # extra args
    # default values for token_key and tag_key are from conll2003 dataset
    token_key: str = field(
        default=AutomlConstants.TEXT_NER_TOKEN_KEY
    )
    tag_key: str = field(
        default=AutomlConstants.TEXT_NER_TAG_KEY
    )
    label_all_tokens: bool = field(
        default=False
    )
    #
    problem_type: Optional[str] = field(
        default=None
    )
    task_name: str = field(
        default=Tasks.NLP_NER
    )
    batch_size: int = field(
        default=AutomlConstants.BATCH_SIZE
    )
    placeholder_label_column: str = field(
        default="tag_key"
    )
    metric_for_best_model: str = field(
        default="f1"
    )
    greater_is_better: bool = field(
        default=True
    )
    mlflow_task_type: str = field(
        default=MLFlowHFFlavourTasks.NAMED_ENTITY_RECOGNITION
    )
    pad_to_max_length: bool = field(
        default=True
    )
    max_seq_length: int = field(
        default=AutomlConstants.DEFAULT_SEQ_LEN
    )

    def __post_init__(self):
        # setting the defaults for mutable arguments will cause issue in case of multiple class
        # initializations. so, placeholders are set here
        self.placeholder_required_columns = ["token_key", "tag_key"]
        self.placeholder_required_column_dtypes = [STRING_DTYPES, STRING_DTYPES]
        #
        if self.placeholder_required_columns is not None:
            for idx, col_name in enumerate(self.placeholder_required_columns):
                decoded_arg = getattr(self, col_name, None)
                if decoded_arg is not None:
                    self.required_columns.append(decoded_arg)
                    self.required_column_dtypes.append(self.placeholder_required_column_dtypes[idx])

        self.label_column = getattr(self, self.placeholder_label_column)


class NLPNerDataset(AzuremlDataset, AzuremlValidatorMixin):

    def __init__(
        self,
        path_or_dict: Union[str, Path, Dict],
        dataset_args: Optional[Dict[str, Any]] = None,
        required_columns: Optional[List[str]] = None,
        required_column_dtypes: Optional[List[List[str]]] = None,
        label_column: Optional[str] = None,
        label_column_optional: bool = False,
        tokenizer: Optional[PreTrainedTokenizerBase] = None,
    ) -> None:
        # required_columns, required_column_dtypes are made optional to support loading the dataset
        # without the need for validation

        # initialize the dataset class
        super().__init__(
            path_or_dict,
            label_column=label_column,
            label_column_optional=label_column_optional,
        )

        # no need for 'id' column in nlp ner datasets
        if 'id' in self.dataset.features:
            self.dataset = self.dataset.remove_columns('id')

        # initialze the validator mixin class
        super(AzuremlDataset, self).__init__(
            required_columns=required_columns,
            required_column_dtypes=required_column_dtypes
        )

        self.dataset_args = dataset_args
        self.tokenizer = tokenizer

    def get_collation_function(self) -> Optional[Callable]:
        """Collation function for dynamic padding"""
        return DataCollatorForTokenClassification(self.tokenizer) if self.tokenizer is not None else None

    def encode_dataset(self, class_names_train_plus_valid: Optional[List[str]] = None):
        """
        datasets: HuggingFace datasets object
        kwargs: max_seq_length, pad_to_max_length, token_key, tag_key, label_all_tokens

        https://github.com/huggingface/notebooks/blob/main/examples/token_classification.ipynb
        """

        if self.tokenizer is None or self.dataset_args is None:
            raise

        def tokenize_and_align_labels(examples):
            # is_split_into_words=True as the input is already a list of words
            if self.tokenizer is None or self.dataset_args is None:
                raise
            tokenized_inputs = self.tokenizer(
                examples[token_key],
                truncation=self.dataset_args["truncation"],
                is_split_into_words=True,
                padding=self.dataset_args["padding"],
                max_length=self.dataset_args["max_length"],
            )

            if tag_key is not None:
                extended_tags = []
                for i, str_tags in enumerate(examples[tag_key]):
                    word_ids = tokenized_inputs.word_ids(batch_index=i)  # Map tokens to their respective word.
                    previous_word_idx = None
                    int_tags = []
                    for word_idx in word_ids:  # Set the special tokens to -100.
                        if word_idx is None:
                            int_tags.append(TaskConstants.NER_IGNORE_INDEX)
                        elif word_idx != previous_word_idx:  # Only label the first token of a given word.
                            int_tags.append(label2id[str_tags[word_idx]])
                        else:
                            int_tags.append(label2id[str_tags[word_idx]] if label_all_tokens else TaskConstants.NER_IGNORE_INDEX)
                        previous_word_idx = word_idx
                    extended_tags.append(int_tags)

                tokenized_inputs["labels"] = extended_tags

            return tokenized_inputs

        def tags_to_id(example):
            example[tag_key] = [label2id[tag] for tag in example[tag_key]]
            return example

        # token and tag keys
        token_key, tag_key = self.dataset_args["token_key"], self.dataset_args["tag_key"]
        label_all_tokens = self.dataset_args["label_all_tokens"]
        # convert label column using class label
        if tag_key is not None and class_names_train_plus_valid is not None:
            # Currently, the examples are casted from string to integers using `datasets.ClassLabel`
            # This is time consuming as it takes a backup of all the existing data and updates the feature
            # and the arrow table metadata. Additionally we are not using all the features of ClassLabel
            # self.convert_label_column_using_classlabel(class_names=class_names_train_plus_valid)
            label2id = {label: idx for idx, label in enumerate(class_names_train_plus_valid)}
        else:
            logger.info("Skipping data casting from string -> int")

        self.dataset = self.dataset.map(
            tokenize_and_align_labels,
            batched=True,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"]
        )
        self.dataset = self.dataset.map(tags_to_id, batched=False)

    def update_dataset_columns_with_prefix(self):
        """Update the token_key, tag_key with prefix"""
        if self.dataset_args is not None:
            self.dataset_args["token_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["token_key"]
            if self.dataset_args["tag_key"] is not None:
                self.dataset_args["tag_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["tag_key"]

        return super().update_dataset_columns_with_prefix()
