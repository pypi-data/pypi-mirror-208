# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Named entity recognition dataset wrapper class."""

import logging
from typing import Optional
import numpy as np

import torch
from torch import nn
from torch.utils.data.dataset import Dataset
from transformers import PreTrainedTokenizer

from .constants import DataLiterals

logger = logging.getLogger(__name__)


class NerDatasetWrapper(Dataset):
    """This will be superseded by a framework-agnostic approach soon."""

    def __init__(
            self,
            data,
            tokenizer: PreTrainedTokenizer,
            labels: dict,
            max_seq_length: Optional[int] = None,
            tokenizer_config: dict = {},
    ):
        """Token classification dataset constructor func."""
        # data = data.replace("-DOCSTART- O\n\n", "")
        # self.data = data.split("\n\n")
        self.data = data
        self.tokenizer = tokenizer
        self.label_map = {labels[key]: key for key in labels}
        self.tokenizer_config = tokenizer_config
        self.max_seq_length = self.tokenizer_config.get("max_length", max_seq_length)

    def __len__(self):
        """Token classification dataset len func."""
        return len(self.data)

    def __getitem__(self, idx):
        """Token classification dataset getitem func."""
        tokens = self.data[idx].split(" ")
        # append label which will be used to align predictions only
        words = [item for item in tokens if item not in DataLiterals.NER_IGNORE_TOKENS]
        labels = ["O"] * len(words)
        tokenizer_config = {
            'max_length': self.max_seq_length,
            'padding': 'max_length',
            'truncation': True,
            'return_tensors': "pt",
            'is_split_into_words': True,
            **self.tokenizer_config
        }
        tokenized = self.tokenizer(words,
                                   None,
                                   **tokenizer_config)
        pad_id = nn.CrossEntropyLoss().ignore_index
        label_ids = np.full((self.max_seq_length), fill_value=pad_id, dtype=np.int32)

        token_idx = 1  # start with index 1 because 0 is a special token
        for label_idx in range(len(words)):

            if token_idx < self.max_seq_length:
                # set label at the starting index of the token
                label_ids[token_idx] = self.label_map[labels[label_idx]]

            # increment token index according to number of tokens generated for the 'word'
            # Note that BERT can create multiple tokens for single word in a language
            token_idx += len(self.tokenizer.tokenize(words[label_idx]))
            # TODO: Remove extra tokenization step if possible ^

        # this should only be added during Split.test once we stop return labels for test split
        tokenized["labels"] = torch.LongTensor([[np.long(item) for item in label_ids]])
        return tokenized
#
#
# class PyTorchClassificationDatasetWrapper(PyTorchDataset):
#     """
#     Class for obtaining dataset to be passed into model for multi-class classification.
#     This is based on the datasets.Dataset package from HuggingFace.
#     """
#
#     def __init__(self, dataframe: pd.DataFrame,
#                  tokenizer: PreTrainedTokenizerBase,
#                  max_seq_length: int):
#         """ Init function definition
#
#         :param dataframe: pd.DataFrame holding data to be passed
#         :param train_label_list: list of labels from training data
#         :param tokenizer: tokenizer to be used to tokenize the data
#         :param max_seq_length: dynamically computed max sequence length
#         :param label_column_name: name/title of the label column
#         """
#         self.tokenizer = tokenizer
#         self.data = dataframe
#         self.padding = "max_length"
#         self.max_seq_length = min(max_seq_length, self.tokenizer.model_max_length)
#
#     def __len__(self):
#         """Len function definition."""
#         return len(self.data)
#
#     def __getitem__(self, index):
#         """Getitem function definition."""
#         if isinstance(self.data, pd.DataFrame) or isinstance(self.data, pd.Series):
#             sample = self.data.iloc[index].astype(str).str.cat(sep=". ")
#         else:
#             sample = self.data[index]
#         tokenized = self.tokenizer(sample, padding=self.padding, max_length=self.max_seq_length,
#                                    truncation=True)
#         for tokenizer_key in tokenized:
#             tokenized[tokenizer_key] = torch.tensor(tokenized[tokenizer_key], dtype=torch.long)
#
#         return tokenized
