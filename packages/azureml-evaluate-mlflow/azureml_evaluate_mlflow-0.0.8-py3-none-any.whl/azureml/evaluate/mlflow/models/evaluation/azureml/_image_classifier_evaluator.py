# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.evaluate.mlflow.aml import AMLClassifierModel, AzureMLInput
from azureml.evaluate.mlflow.models.evaluation.azureml._task_evaluator import TaskEvaluator
from azureml.evaluate.mlflow.models.evaluation.constants import (
    EvaluationSettingLiterals,
    EvaluationMiscLiterals
)

from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowException
from azureml.metrics import compute_metrics, constants

import ast
import numpy as np


class ImageClassifierEvaluator(TaskEvaluator):

    def evaluate(self,
                 model: AMLClassifierModel,
                 X_test: AzureMLInput,
                 y_test: AzureMLInput,
                 **kwargs):
        """ Evaluate the image classififr model on the given test data.

        :param model: The model to evaluate.
        :param X_test: The test data.
        :param y_test: The test labels.
        :param kwargs: Additional arguments to evaluate model ["multi_label", "batch_size", "threshold"]
        :return: The metrics and predictions.
        """
        if not isinstance(model, AMLClassifierModel):
            raise AzureMLMLFlowException(f"Model should be of type {str(AMLClassifierModel)}")

        y_pred = model.predict(X_test, **kwargs)[EvaluationMiscLiterals.IMAGE_OUTPUT_LABEL_COLUMN]
        multilabel = kwargs.get(EvaluationSettingLiterals.MULTI_LABEL)
        if multilabel:
            y_pred = [str(x) for x in y_pred]
            y_test = np.array(list(map(lambda x: ast.literal_eval(x), y_test)))
            y_pred = np.array(list(map(lambda x: ast.literal_eval(x), y_pred)))
        else:
            y_pred = self._convert_predictions(y_pred)
            y_test = self._convert_predictions(y_test)

        metrics = compute_metrics(task_type=constants.Tasks.CLASSIFICATION, y_test=y_test, y_pred=y_pred,
                                  **kwargs)
        return metrics, y_pred
