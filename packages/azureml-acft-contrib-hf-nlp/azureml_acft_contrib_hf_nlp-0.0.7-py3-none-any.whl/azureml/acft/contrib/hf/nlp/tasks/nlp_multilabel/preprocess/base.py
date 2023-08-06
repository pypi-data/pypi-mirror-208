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

import ast
from pathlib import Path
from functools import partial

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from sklearn.preprocessing import MultiLabelBinarizer

from ....constants.constants import (
    DatasetSplit,
    SaveFileConstants,
    AzuremlConstants,
    MLFlowHFFlavourConstants,
    PreprocessArgsTemplate,
    Tasks,
    MLFlowHFFlavourTasks,
    HfModelTypes,
    STRING_DTYPES,
    AutomlConstants,
)
from ....base_runner import BaseRunner

from ....utils.data_utils import AzuremlDataset
from ....utils.preprocess_utils import concat_text_columns
from ....utils.validation_utils import AzuremlValidatorMixin
from ....constants.constants import TaskConstants

from datasets.arrow_dataset import Dataset
from datasets import Sequence

import transformers
from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.data.data_collator import DataCollatorWithPadding
from transformers.hf_argparser import HfArgumentParser

from azureml.acft.accelerator.utils.logging_utils import get_logger_app
from azureml.acft.accelerator.utils.error_handling.exceptions import ValidationException
from azureml.acft.accelerator.utils.error_handling.error_definitions import PathNotFound, ValidationError
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore


logger = get_logger_app()


@dataclass
class NLPMultilabelPreprocessArgs(PreprocessArgsTemplate):
    # Specify the defaults for all new attributes of MultiLabelPreprocessArgs +
    # inhertied attributes from _PreprocessArgsTemplate here.
    # Otherwise, there will be issues related to ordering of default and
    # non-default attributes

    # extra args
    # Makesure the extra args don't overlap with names of PreprocessArgs Template
    sentence1_key: str = field(
        default=AutomlConstants.TEXT_CLASSIFICATION_COLUMN_NAME
    )
    sentence2_key: Optional[str] = field(
        default=None
    )
    label_key: Optional[str] = field(
        default=None
    )
    #
    problem_type: Optional[str] = field(
        default="multi_label_classification"
    )
    task_name: str = field(
        default=Tasks.NLP_MULTILABEL
    )
    batch_size: int = field(
        default=AutomlConstants.BATCH_SIZE
    )
    placeholder_label_column: str = field(
        default="label_key"
    )
    metric_for_best_model: str = field(
        default="f1"
    )
    greater_is_better: bool = field(
        default=True
    )
    mlflow_task_type: str = field(
        default=MLFlowHFFlavourTasks.MULTI_LABEL_CLASSIFICATION
    )
    pad_to_max_length: bool = field(
        default=True
    )
    max_seq_length: int = field(
        default=AutomlConstants.DEFAULT_SEQ_LEN
    )
    enable_long_range_text: bool = field(
        default=True
    )

    def __post_init__(self):
        # setting the defaults for mutable arguments will cause issue in case of multiple class
        # initializations. so, placeholders are set here
        self.placeholder_required_columns = ["sentence1_key", "sentence2_key", "label_key"]
        self.placeholder_required_column_dtypes = [
            STRING_DTYPES, STRING_DTYPES, STRING_DTYPES
        ]
        #
        if self.placeholder_required_columns is not None:
            for idx, col_name in enumerate(self.placeholder_required_columns):
                decoded_arg = getattr(self, col_name, None)
                if decoded_arg is not None:
                    self.required_columns.append(decoded_arg)
                    self.required_column_dtypes.append(self.placeholder_required_column_dtypes[idx])

        self.label_column = getattr(self, self.placeholder_label_column)


class NLPMultilabelDataset(AzuremlDataset, AzuremlValidatorMixin):

    def __init__(
        self,
        path_or_dict: Union[str, Path],
        dataset_args: Optional[Dict[str, Any]] = None,
        required_columns: Optional[List[str]] = None,
        required_column_dtypes: Optional[List[List[str]]] = None,
        label_column: Optional[str] = None,
        label_column_optional: bool = False,
        tokenizer: Optional[PreTrainedTokenizerBase] = None,
        preprocess: bool = True,
    ) -> None:
        # required_columns, required_column_dtypes are made optional to support loading the dataset
        # without the need for validation

        # special column is added for multi-label after the label_data is decoded and converted to list of string
        self.preprocess = preprocess
        new_label_column = None
        if label_column is not None and dataset_args is not None and required_columns is not None and required_column_dtypes is not None:
            new_label_column = label_column + TaskConstants.MULTI_LABEL_NEW_COLUMN_SUFFIX
            dataset_args["label_key"] = new_label_column
            self.label_list_column = new_label_column
            logger.info(f"Updated label column: {new_label_column}")

        # initialize the dataset class
        super().__init__(
            path_or_dict,
            label_column=label_column,
            label_column_optional=label_column_optional,
        )

        # initialze the validator mixin class
        super(AzuremlDataset, self).__init__(
            required_columns=required_columns,
            required_column_dtypes=required_column_dtypes
        )

        self.dataset_args = dataset_args
        self.tokenizer = tokenizer
        self.old_label_column = label_column

        # decode the old label column and populate the new one
        self.dataset = self.dataset.map(self.decode_label_column, batched=True)

        if preprocess:
            # text column concatenation
            # AutoML NLP Logic
            label_columns = [label_column, new_label_column]
            cols_to_remove = [col for col in self.dataset.column_names if (col not in label_columns)]
            self.dataset = self.dataset.map(
                partial(
                    concat_text_columns,
                    label_columns=label_columns
                ),
                batched=False,
                remove_columns=cols_to_remove,
            )

    def get_collation_function(self) -> Optional[Callable]:
        """Collation function for dynamic padding"""
        return DataCollatorWithPadding(self.tokenizer) if self.tokenizer is not None else None

    def encode_dataset(self, class_names_train_plus_valid: Optional[List[str]] = None):
        """
        datasets: HuggingFace datasets object
        tokenizer: HuggingFace tokenizer
        kwargs: max_seq_length, pad_to_max_length, sentence1_key, sentence2_key, label_key

        https://github.com/huggingface/notebooks/blob/main/examples/text_classification.ipynb
        """

        if self.tokenizer is None or self.dataset_args is None:
            raise

        def tokenize_func(examples):
            if self.tokenizer is None or self.dataset_args is None:
                raise

            # Tokenize text
            args = (
                (examples[sentence1_key],) if sentence2_key is None else (examples[sentence1_key], examples[sentence2_key])
            )
            result = self.tokenizer(
                *args,
                padding=self.dataset_args["padding"],
                max_length=self.dataset_args["max_length"],
                truncation=self.dataset_args["truncation"]
            )

            if label_key is not None:
                # format the label key using multi-label binarizer. It gets converted to 1-hot vector
                result["labels"] = []
                for labels_list in examples[label_key]:
                    result["labels"].append(mlb.transform([labels_list])[0])

            return result

        # sentence and label keys
        sentence1_key, sentence2_key = self.dataset_args["sentence1_key"], self.dataset_args["sentence2_key"]
        label_key = AzuremlConstants.DATASET_COLUMN_PREFIX + self.label_list_column

        # convert label column to string
        if label_key is not None:
            # initialize sklearn multi label binarizer
            mlb = MultiLabelBinarizer()
            mlb.fit([class_names_train_plus_valid])

        # tokenize the data
        self.dataset = self.dataset.map(
            tokenize_func,
            batched=True,
            remove_columns=[AzuremlConstants.DATASET_COLUMN_PREFIX + self.label_list_column],
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"]
        )

    def decode_label_column(self, examples: Dict[str, Any]) -> Dict[str, Any]:
        """
        The label column of multi-label is a list of class names encoded as string i.e. of type string of list of string
        This function encodes the old label column and populates the new label column
        :param examples
            Dictionary of dataset examples
        """
        if self.old_label_column is None:
            logger.info(f"label column is {self.old_label_column}. skipping label column decoding")
            return examples

        item_decode_list = []
        for item in examples[self.old_label_column]:
            item_decode = ast.literal_eval(item)
            if not (
                isinstance(item_decode, List) and
                (item_decode and isinstance(item_decode[0], str))
            ):
                raise ValueError("data is incorrectly formatted")
            item_decode_list.append(item_decode)

        # label column is created ONLY when old_label_column is present
        examples[self.label_list_column] = item_decode_list  # type: ignore

        return examples

    def update_dataset_columns_with_prefix(self):
        """Update the sentence1_key, sentece2_key and label_keys with prefix"""
        if self.dataset_args is not None:
            self.dataset_args["sentence1_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["sentence1_key"]
            if self.dataset_args["sentence2_key"] is not None:
                self.dataset_args["sentence2_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["sentence2_key"]
            if self.dataset_args["label_key"] is not None:
                self.dataset_args["label_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["label_key"]

        return super().update_dataset_columns_with_prefix()

    def load(self) -> Dataset:
        """
        Load the dataset and add a dummy column for the new column
        new column will a list of strings which will be a decoded column of string input
        """
        dataset = super().load()

        # add a dummy column with list of strings dtype
        if self.preprocess:
            dataset = dataset.add_column(
                name=self.label_list_column,
                column=[[""]] * len(dataset) 
            )
        
        return dataset
