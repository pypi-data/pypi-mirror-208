# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from collections import UserDict

import numpy as np
import pandas as pd
import torch

_logger = logging.getLogger(__name__)


def _ensure_tensor_on_device(inputs, device):
    if isinstance(inputs, dict):
        return {name: _ensure_tensor_on_device(tensor, device) for name, tensor in inputs.items()}
    elif isinstance(inputs, UserDict):
        return UserDict({name: _ensure_tensor_on_device(tensor, device) for name, tensor in inputs.items()})
    elif isinstance(inputs, list):
        return [_ensure_tensor_on_device(item, device) for item in inputs]
    elif isinstance(inputs, tuple):
        return tuple([_ensure_tensor_on_device(item, device) for item in inputs])
    elif isinstance(inputs, torch.Tensor):
        if device == torch.device("cpu") and inputs.dtype in {torch.float16, torch.bfloat16}:
            inputs = inputs.float()
        return inputs.to(device)
    else:
        return inputs


def concat_data_columns(data, seperator):
    """
    Concatenating data
    Todo: Add more datatypes and handle series
    :param data: Incoming data to be processed
    :type data:  DF/Numpy
    :param seperator: separator to concat
    :type seperator: str
    :return: Processed data
    :rtype: list
    """
    if isinstance(data, pd.DataFrame):
        data = data.apply(lambda x: x.astype(str).str.cat(sep=seperator), axis=1).to_list()
    elif isinstance(data, pd.Series):
        data = data.to_list()
    elif isinstance(data, np.ndarray):
        data = list(map(lambda x: seperator.join(x), data))
    else:
        raise TypeError("Datatype not supported")
    return data


def process_text_pairs(data, keys):
    """
    Preprocess Text Pairs
    """
    if isinstance(data, pd.DataFrame):
        if len(keys) != 2:
            _logger.warning("Number of columns should be two. Using default processor")
            return None
        data.rename(columns={keys[0]: 'text', keys[1]: 'text_pair'}, inplace=True)
        data = data.to_dict(orient='records')
    elif isinstance(data, np.ndarray):
        if data.ndim != 2 or data.shape[1] != 2:
            _logger.warning("Array dimension not of required size. Using default processor")
            return None
        data = [{'text': val[0], 'text_pair': val[1]} for val in data]
    else:
        _logger.warning("Datatype not supported by TextProcessor. Using default processor")
        return None
    return data
