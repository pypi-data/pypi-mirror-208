# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Definitions for Language Modeling metrics."""
from abc import abstractmethod

import evaluate

from typing import Any, List, Optional
from azureml.metrics._metric_base import Metric, ScalarMetric


class Seq2SeqFillMaskMetric(Metric):
    """Base class for Sequence to Sequence fill mask metric"""

    def __init__(
        self,
        y_test: List[Any],
        y_pred: List[str],
        model_id: Optional[str],
        batch_size: Optional[int],
        add_start_token: Optional[bool],
    ) -> None:
        """
        :param y_test: Tokenized References in the test set
        :param y_pred: Tokenized Hypothesis predicted by language model
        :param model_id: model used for calculating Perplexity.
                            Perplexity can only be calculated for causal language models.
        :param batch_size (int): the batch size to run texts through the model. Defaults to 16.
        :param add_start_token (bool): whether to add the start token to the texts,
            so the perplexity can include the probability of the first word. Defaults to True.
        """
        self.y_test = y_test
        self.y_pred = y_pred
        self.model_id = model_id
        self.batch_size = batch_size
        self.add_start_token = add_start_token

    @abstractmethod
    def compute(self) -> Any:
        """Compute the score for the metric"""
        ...


class Perplexity(Seq2SeqFillMaskMetric, ScalarMetric):
    """Perplexity metric for Sequence to Sequence Language Modeling Tasks"""

    hf_perplexity = evaluate.load("perplexity")

    def compute(self) -> Any:
        """Compute the score for Perplexity metric"""
        perplexity_args = {
            "model_id": self.model_id,
            "batch_size": self.batch_size,
            "add_start_token": self.add_start_token,
        }
        result = self.hf_perplexity.compute(
            predictions=self.y_pred, **perplexity_args
        )
        return result["perplexities"]
