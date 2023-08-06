# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Definitions for Question/Answering metrics."""
import re
import string
from abc import abstractmethod
from collections import Counter
from typing import Any, List

import evaluate
import numpy as np

from azureml.metrics._metric_base import Metric, ScalarMetric


class Seq2SeqQAMetric(Metric):
    """Base class for Sequence to Sequence Question Answering metric"""

    def __init__(
        self,
        y_test: List[Any],
        y_pred: List[str],
        tokenizer: Any,
        regexes_to_ignore: List[str],
        ignore_case: bool,
        ignore_punctuation: bool,
        ignore_numbers: bool,
    ) -> None:
        """
        :param y_test: Tokenized References in the test set
        :param y_pred: Tokenized Hypothesis predicted by language model
        :param tokenizer: function that takes input a string, and returns a list of tokens
        :params regexes_to_ignore: List of string regular expressions to ignore
        :params ignore_case: Boolean to indicate whether to ignore case
        :params ignore_punctuation: Boolean to indicate whether to ignore punctuation
        :params ignore_numbers: Boolean to indicate whether to ignore numbers
        """
        self.y_test = y_test
        self.y_pred = y_pred
        self.tokenizer = tokenizer
        self.regexes_to_ignore = regexes_to_ignore
        self.ignore_case = ignore_case
        self.ignore_punctuation = ignore_punctuation
        self.ignore_numbers = ignore_numbers

    @abstractmethod
    def compute(self) -> Any:
        """Compute the score for the metric"""
        ...

    """
    Function is same as normalize_answer(s) with name changed to normalize_text(self, text)
    Modified from
    https://github.com/huggingface/evaluate/blob/main/metrics/squad_v2/compute_score.py
    """

    def normalize_text(self, text) -> str:
        """Lower text and remove punctuation, articles and extra whitespace."""

        def remove_articles(text):
            return re.sub(r"\b(a|an|the)\b", " ", text)

        def white_space_fix(text):
            return " ".join(text.split())

        def remove_punc(text):
            exclude = set(string.punctuation)
            return "".join(ch for ch in text if ch not in exclude)

        def lower(text):
            return text.lower()

        return white_space_fix(remove_articles(remove_punc(lower(text))))


class ExactMatch(Seq2SeqQAMetric, ScalarMetric):
    """ExactMatch metric for Sequence to Sequence Question Answering Tasks"""

    hf_exact_match = evaluate.load("exact_match")

    def compute(self) -> Any:
        """Compute the score for ExactMatch metric"""
        exact_match_args = {
            "regexes_to_ignore": self.regexes_to_ignore,
            "ignore_case": self.ignore_case,
            "ignore_punctuation": self.ignore_punctuation,
            "ignore_numbers": self.ignore_numbers,
        }
        res = self.hf_exact_match.compute(
            predictions=self.y_pred, references=self.y_test, **exact_match_args
        )
        return res["exact_match"]


class F1Score(Seq2SeqQAMetric, ScalarMetric):
    """F1 score metric for Sequence to Sequence Question Answering Tasks"""

    """
    Function is similar to compute_f1(a_gold, a_pred) with modifications
    Modified from
    https://github.com/huggingface/evaluate/blob/main/metrics/squad_v2/compute_score.py
    """

    def compute(self) -> Any:
        """Compute the score for F1 score metric"""

        f1_score_list = []
        for reference, prediction in zip(self.y_test, self.y_pred):

            prediction_tokens = self.normalize_text(prediction)
            reference_tokens = self.normalize_text(reference)
            prediction_tokens = self.tokenizer(prediction_tokens)
            reference_tokens = self.tokenizer(reference_tokens)

            common_tokens = Counter(prediction_tokens) & Counter(reference_tokens)
            num_common_tokens = sum(common_tokens.values())

            if num_common_tokens == 0:
                f1_score_list.append(0)
                continue

            precision = 1.0 * num_common_tokens / len(prediction_tokens)
            recall = 1.0 * num_common_tokens / len(reference_tokens)

            f1_score = (2 * precision * recall) / (precision + recall)

            f1_score_list.append(f1_score)

        return np.mean(f1_score_list)


class SquadV2(Seq2SeqQAMetric, ScalarMetric):
    """Squad_v2 metrics for Question Answering Tasks"""

    hf_squadv2 = evaluate.load("squad_v2")

    def compute(self) -> Any:
        """Compute score for Squad_v2 metrics"""

        squad_v2_args = {"predictions": self.y_pred, "references": self.y_test}
        res = self.hf_squadv2.compute(
            predictions=self.y_pred, references=self.y_test, **squad_v2_args
        )

        return res
