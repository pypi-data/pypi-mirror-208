# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to multi-class and multi-label Text Classification task types."""

import logging
from typing import Any, Dict, List, Optional, Callable, Iterator, Union

import numpy as np
import pandas as pd
from sklearn.base import TransformerMixin
from sklearn.preprocessing import MultiLabelBinarizer

from azureml.metrics import _scoring, constants, utilities
from azureml.metrics.azureml_metrics import AzureMLMetrics

logger = logging.getLogger(__name__)


class AzureMLTextClassificationMetrics(AzureMLMetrics):
    """Class for AzureML text classification metrics."""

    def __init__(self,
                 metrics: Optional[List[str]] = None,
                 class_labels: Optional[np.ndarray] = None,
                 train_labels: Optional[np.ndarray] = None,
                 y_transformer: Optional[TransformerMixin] = None,
                 multilabel: Optional[bool] = False,
                 custom_dimensions: Optional[Dict[str, Any]] = None,
                 log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                                 Iterator[Optional[Any]]]] = None,
                 log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                                   Optional[bool], Optional[Any]], None]] = None
                 ) -> None:
        """
        Given the scored data, generate metrics for classification task.

        :param metrics: Classification metrics to compute point estimates
        :param class_labels: All classes found in the full dataset (includes train/valid/test sets).
            These should be transformed if using a y transformer.
        :param train_labels: Classes as seen (trained on) by the trained model. These values
            should correspond to the columns of y_pred_probs in the correct order.
        :param y_transformer: Used to inverse transform labels from `y_test`. Required for non-scalar metrics.
        :param multilabel: Indicate if it is multilabel classification.
        :param log_activity is a callback to log the activity with parameters
            :param logger: logger
            :param activity_name: activity name
            :param activity_type: activity type
            :param custom_dimensions: custom dimensions
        :param log_traceback is a callback to log exception traces. with parameters
            :param exception: The exception to log.
            :param logger: The logger to use.
            :param override_error_msg: The message to display that will override the current error_msg.
            :param is_critical: If is_critical, the logger will use log.critical, otherwise log.error.
            :param tb: The traceback to use for logging; if not provided,
                        the one attached to the exception is used.
        :return: None
        """
        default_metrics = constants.CLASSIFICATION_NLP_MULTILABEL_SET if multilabel \
            else constants.Metric.CLASSIFICATION_SET
        self.metrics = metrics if metrics else default_metrics
        self.class_labels = utilities.check_and_convert_to_np(class_labels)
        self.train_labels = utilities.check_and_convert_to_np(train_labels)

        if self.class_labels is None and self.train_labels is not None:
            self.class_labels = self.train_labels

        if self.train_labels is None and self.class_labels is not None:
            self.train_labels = self.class_labels

        self.y_transformer = y_transformer
        self.multilabel = multilabel
        self.__custom_dimensions = custom_dimensions
        super().__init__(log_activity, log_traceback)

    def compute(self, y_test: Union[np.ndarray, pd.DataFrame, List],
                y_pred: Optional[Union[np.ndarray, pd.DataFrame, List]] = None,
                y_pred_probs: Optional[Union[np.ndarray, pd.DataFrame, List]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Compute all metrics for classification task based on the config.

        :param y_test: Actual label values
        :param y_pred: Predicted values
        :param y_pred_probs: Predicted probablity values
        :return: Dict of computed metrics
        """
        y_test = utilities.check_and_convert_to_np(y_test)
        y_pred = utilities.check_and_convert_to_np(y_pred)
        y_pred_probs = utilities.check_and_convert_to_np(y_pred_probs)

        if y_test is not None and y_pred is not None and self.y_transformer is None:
            if y_test.dtype == "object" or y_pred.dtype == "object":
                if self.multilabel:
                    y_transformer = MultiLabelBinarizer()
                    y_test = np.array(y_transformer.fit_transform(y_test))
                    y_pred = np.array(y_transformer.transform(y_pred))
                    self.class_labels = np.array(list(range(len(y_test[0]))), dtype=y_test.dtype)

        if y_pred_probs is None and y_pred is not None and hasattr(y_pred, 'shape'):
            y_pred_probs = None if len(y_pred.shape) == 1 or y_pred.shape[1] == 1 else y_pred
        if y_pred_probs is not None:
            y_pred = None

        if self.class_labels is None:
            if self.train_labels is not None:
                self.class_labels = self.train_labels
            else:
                try:
                    if self.multilabel and self.y_transformer is not None:
                        L = len(self.y_transformer.classes_)
                        self.class_labels = np.arange(L)
                    elif not (y_pred is None and y_test is None and self.y_transformer is None):
                        self.class_labels = np.array(list({*np.unique(y_test), *np.unique(y_pred)}),
                                                     dtype=y_test.dtype)
                except Exception as e:
                    error_msg = "Error in creating class_labels. Pass as parameter."
                    raise Exception(error_msg + str(e))

        if self.train_labels is None:
            self.train_labels = self.class_labels

        scored_metrics = _scoring._score_classification(
            self._log_activity,
            self._log_traceback,
            y_test,
            y_pred,
            y_pred_probs,
            self.metrics,
            self.class_labels,
            self.train_labels,
            y_transformer=self.y_transformer,
            multilabel=self.multilabel,
        )
        return scored_metrics

    @staticmethod
    def list_metrics(multilabel: Optional[bool]):
        """Get the list of supported metrics.

            :param multilabel: Accepts a boolean parameter which indicates multilabel classification.
            :return: List of supported metrics.
        """
        supported_metrics = []

        if multilabel:
            supported_metrics = constants.CLASSIFICATION_NLP_MULTILABEL_SET
        else:
            supported_metrics = constants.Metric.CLASSIFICATION_SET

        return supported_metrics
