# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Computation of AzureML model evaluation metrics."""
import logging
import numpy as np
import pandas as pd

from azureml.metrics import _scoring_utilities, _validation, constants, utilities
from azureml.metrics._forecasting import _NormalizedRegressorWrapper
from azureml.metrics._metric_base import NonScalarMetric
from azureml.metrics.constants import MetricExtrasConstants, Metric, ALL_TIME
from sklearn.base import TransformerMixin
from typing import Any, Callable, Dict, List, Iterator, Optional, Sequence, Tuple, Union


logger = logging.getLogger(__name__)


def _score_classification(
        log_activity: Callable[[logging.Logger, str, Optional[str],
                                Optional[Dict[str, Any]]], Iterator[Optional[Any]]],
        log_traceback: Callable[[BaseException, logging.Logger, Optional[str],
                                 Optional[bool], Optional[Any]], None],
        y_test: np.ndarray,
        y_pred: Optional[np.ndarray],
        y_pred_probs: Optional[np.ndarray],
        metrics: List[str],
        class_labels: np.ndarray,
        train_labels: np.ndarray,
        sample_weight: Optional[np.ndarray] = None,
        y_transformer: Optional[TransformerMixin] = None,
        use_binary: bool = False,
        multilabel: Optional[bool] = False,
        positive_label: Optional[Any] = None,
        ensure_contiguous: bool = False
) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute model evaluation metrics for a classification task.

    All class labels for y should come
    as seen by the fitted model (i.e. if the fitted model uses a y transformer the labels
    should also come transformed).

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if the calculation failed.

    :param y_test: The target values (Transformed if using a y transformer)
    :param y_pred: The predicted values (Transformed if using a y transformer)
    :param y_pred_probs: The predicted probabilities for all classes.
    :param metrics: Classification metrics to compute
    :param class_labels: All classes found in the full dataset (includes train/valid/test sets).
        These should be transformed if using a y transformer.
    :param train_labels: Classes as seen (trained on) by the trained model. These values
        should correspond to the columns of y_pred_probs in the correct order.
    :param sample_weight: Weights for the samples (Does not need
        to match sample weights on the fitted model)
    :param y_transformer: Used to inverse transform labels from `y_test`. Required for non-scalar metrics.
    :param use_binary: Compute metrics only on the true class for binary classification.
    :param positive_label: class designed as positive class in later binary classification metrics.
    :param multilabel: Indicate if it is multilabel classification.
    :param ensure_contiguous: Whether to pass contiguous NumPy arrays to the sklearn functions computing metrics.
    :return: A dictionary mapping metric name to metric score.
    """
    if not multilabel:
        y_test = _validation.format_1d(y_test, 'y_test')
        if y_pred is not None:
            y_pred = _validation.format_1d(y_pred, 'y_pred')

    _validation.validate_classification(y_test, y_pred, y_pred_probs, metrics,
                                        class_labels, train_labels,
                                        sample_weight, multilabel=multilabel)
    _validation.log_classification_debug(y_test, y_pred, y_pred_probs, class_labels,
                                         train_labels, sample_weight=sample_weight, multilabel=multilabel)

    scoring_dto = _scoring_utilities.ClassificationDataDto(y_test,
                                                           y_pred,
                                                           y_pred_probs,
                                                           class_labels,
                                                           train_labels,
                                                           sample_weight,
                                                           y_transformer,
                                                           multilabel=multilabel,
                                                           positive_label=positive_label)
    positive_label_encoded = scoring_dto.positive_label_encoded

    results = {}
    skipped_metrics = []
    computed_metrics = []
    for name in metrics:
        if y_pred_probs is None and name in Metric.CLASSIFICATION_PROB_REQUIRED_SET:
            skipped_metrics.append(name)
            continue
        try:
            metric_class = _scoring_utilities.get_metric_class(name)
            test_targets, pred_targets, labels, positive_label = scoring_dto.get_targets(
                encoded=utilities.is_scalar(name),
                classwise=utilities.is_classwise(name))

            metric = metric_class(
                test_targets, scoring_dto.y_pred_probs_padded, scoring_dto.y_test_bin,
                pred_targets, labels, sample_weight=sample_weight, use_binary=use_binary,
                positive_label_encoded=positive_label_encoded, multilabel=multilabel, y_transformer=y_transformer,
                ensure_contiguous=ensure_contiguous)

            results[name] = metric.compute()
            computed_metrics.append(name)
        except MemoryError:
            raise
        except Exception as e:
            safe_name = _scoring_utilities.get_safe_metric_name(name)
            logger.error("Scoring failed for classification metric {}".format(safe_name))
            log_traceback(e, logger, is_critical=False)
            if utilities.is_scalar(name):
                results[name] = np.nan
            else:
                results[name] = NonScalarMetric.get_error_metric()

    logger.info(f"Metrics computed:\n {computed_metrics}\n")

    if len(skipped_metrics) >= 1:
        logger.warning(f"Metrics skipped due to missing y_pred_proba:\n {skipped_metrics}")

    return utilities.segregate_scalar_non_scalar(results)


def _score_regression(
        log_activity: Callable[[logging.Logger, str, Optional[str],
                                Optional[Dict[str, Any]]], Iterator[Optional[Any]]],
        log_traceback: Callable[[BaseException, logging.Logger, Optional[str],
                                 Optional[bool], Optional[Any]], None],
        y_test: np.ndarray,
        y_pred: np.ndarray,
        metrics: List[str],
        y_max: Optional[float] = None,
        y_min: Optional[float] = None,
        y_std: Optional[float] = None,
        sample_weight: Optional[np.ndarray] = None,
        bin_info: Optional[Dict[str, float]] = None
) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute model evaluation metrics for a regression task.

    The optional parameters `y_min`, `y_min`, and `y_min` should be based on the
        target column y from the full dataset.

    - `y_max` and `y_min` should be used to control the normalization of
    normalized metrics. The effect will be division by max - min.
    - `y_std` is used to estimate a sensible range for displaying non-scalar
    regression metrics.

    If the metric is undefined given the input data, the score will show
        as nan in the returned dictionary.

    :param y_test: The target values.
    :param y_pred: The predicted values.
    :param metrics: List of metric names for metrics to calculate.
    :type metrics: list
    :param y_max: The max target value.
    :param y_min: The min target value.
    :param y_std: The standard deviation of targets value.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :param bin_info:
        The binning information for true values. This should be calculated from make_dataset_bins. Required for
        calculating non-scalar metrics.
    :return: A dictionary mapping metric name to metric score.
    """
    # Lenient on shape of y_test and y_pred
    y_test = _validation.format_1d(y_test, 'y_test')
    y_test = _validation.convert_decimal_to_float(y_test)
    y_pred = _validation.format_1d(y_pred, 'y_pred')

    _validation.validate_regression(y_test, y_pred, metrics)
    _validation.log_regression_debug(y_test, y_pred, y_min, y_max, sample_weight=sample_weight)

    y_min = np.min(y_test) if y_min is None else y_min
    y_max = np.max(y_test) if y_max is None else y_max
    y_std = np.std(y_test) if y_std is None else y_std

    results = {}
    for name in metrics:
        safe_name = _scoring_utilities.get_safe_metric_name(name)
        try:
            metric_class = _scoring_utilities.get_metric_class(name)
            metric = metric_class(y_test, y_pred, y_min=y_min, y_max=y_max, y_std=y_std,
                                  bin_info=bin_info, sample_weight=sample_weight)
            results[name] = metric.compute()

            if utilities.is_scalar(name) and np.isinf(results[name]):
                logger.error("Found infinite regression score for {}, setting to nan".format(safe_name))
                results[name] = np.nan
        except MemoryError:
            raise
        except Exception as e:
            logger.error("Scoring failed for regression metric {}".format(safe_name))
            log_traceback(e, logger, is_critical=False)
            if utilities.is_scalar(name):
                results[name] = np.nan
            else:
                results[name] = NonScalarMetric.get_error_metric()

    return utilities.segregate_scalar_non_scalar(results)


def _score_forecasting(
        log_activity: Callable[[logging.Logger, str, Optional[str],
                                Optional[Dict[str, Any]]], Iterator[Optional[Any]]],
        log_traceback: Callable[[BaseException, logging.Logger, Optional[str],
                                 Optional[bool], Optional[Any]], None],
        y_test: np.ndarray,
        y_pred: np.ndarray,
        horizons: np.ndarray,
        X_test: pd.DataFrame,
        metrics: List[str],
        time_column_name: str,
        time_series_id_column_names: List[str],
        aggregation_method: Callable[[Sequence[float]], float] = np.mean,
        origin_column_name: Optional[str] = None,
        y_min_dict: Dict[Union[str, Tuple[str]], float] = None,
        y_max_dict: Dict[Union[str, Tuple[str]], float] = None,
        y_std: Optional[float] = None,
        sample_weight: Optional[np.ndarray] = None,
        X_train: Optional[pd.DataFrame] = None,
        y_train: Optional[np.ndarray] = None,
) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute model evaluation metrics for a forecasting task.

    The optional parameters `y_min`, `y_min`, and `y_min` should be based on the
        target column y from the full dataset.

    - `y_max` and `y_min` should be used to control the normalization of
    normalized metrics. The effect will be division by max - min.
    - `y_std` is used to estimate a sensible range for displaying non-scalar
    regression metrics.

    If the metric is undefined given the input data, the score will show
        as nan in the returned dictionary.

    :param log_activity is a callback to log the activity with parameters
    :param log_traceback is a callback to log exception traces. with parameters
    :param y_test: The target values.
    :param y_pred: The predicted values.
    :param horizons: The integer horizon aligned to each y_test. These values should be computed
            by the timeseries transformer. If the timeseries transformer does not compute a horizon,
            ensure all values are the same (ie. every y_test should be horizon 1.)
    :param metrics: List of metric names for metrics to calculate.
    :param time_column_name: The time column name.
    :param time_series_id_column_names: The time series id column names also known as
                                        grain column names.
    :param origin_column_name: The origin time column name.
    :param y_min_dict: The dictionary, with minimum target values per time series ID, time series ID
                       is used as a key.
    :param y_max_dict: The dictionary, with maximum target values per time series ID, time series ID
                       is used as a key.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :param X_train: The inputs which were used to train the model.
    :param y_train: The targets which were used to train the model.
    :param aggregation_method: The function used to aggregate by grain metrics.
    :return: A dictionary mapping metric name to metric score.
    """
    # Lenient on shape of y_test and y_pred
    y_test = _validation.format_1d(y_test, 'y_test')
    y_test = _validation.convert_decimal_to_float(y_test)
    y_pred = _validation.format_1d(y_pred, 'y_pred')
    if y_train is not None:
        y_train = _validation.format_1d(y_train, 'y_train')
        y_train = _validation.convert_decimal_to_float(y_train)

    _validation.validate_forecasting(y_test, y_pred, metrics)

    if y_min_dict is None:
        y_min_dict = {}
    if y_max_dict is None:
        y_max_dict = {}
    y_min = np.min(y_test) if not y_min_dict else np.min(list(y_min_dict.values()))
    y_max = np.max(y_test) if not y_max_dict else np.max(list(y_max_dict.values()))
    _validation.log_forecasting_debug(y_test, y_pred, y_min, y_max, sample_weight=sample_weight)

    y_std = np.std(y_test) if y_std is None else y_std

    results = {}
    for name in metrics:
        safe_name = _scoring_utilities.get_safe_metric_name(name)
        try:
            metric_class = _scoring_utilities.get_metric_class(name)
            if name in constants.FORECASTING_NONSCALAR_SET:
                metric = metric_class(
                    y_test=y_test,
                    y_pred=y_pred,
                    horizons=horizons,
                    y_min=y_min,
                    y_max=y_max,
                    y_std=y_std,
                    sample_weight=sample_weight,
                    X_test=X_test,
                    X_train=X_train,
                    y_train=y_train,
                    time_series_id_column_names=time_series_id_column_names,
                    time_column_name=time_column_name,
                    origin_column_name=origin_column_name,
                    y_min_dict=y_min_dict,
                    y_max_dict=y_max_dict
                )
            elif name in constants.REGRESSION_NORMALIZED_SET:
                # Calculate the metrics by grain/time_series_id.
                metric = _NormalizedRegressorWrapper(
                    y_test=y_test,
                    y_pred=y_pred,
                    horizons=horizons,
                    y_min_dict=y_min_dict,
                    y_max_dict=y_max_dict,
                    sample_weight=sample_weight,
                    X_test=X_test,
                    time_series_id_column_names=time_series_id_column_names,
                    time_column_name=time_column_name,
                    metric_class=metric_class,
                    aggregation_function=aggregation_method)
            else:
                # Other regression metrics, which do not require normalization.
                metric = metric_class(y_test, y_pred, y_min=y_min, y_max=y_max, y_std=y_std,
                                      sample_weight=sample_weight)
            results[name] = metric.compute()

            if utilities.is_scalar(name) and np.isinf(results[name]):
                logger.error("Found infinite forecasting score for {}, setting to nan".format(safe_name))
                results[name] = np.nan
        except MemoryError:
            raise
        except Exception as e:
            logger.error("Scoring failed for forecasting metric {}".format(safe_name))
            log_traceback(e, logger, is_critical=False)
            if utilities.is_scalar(name):
                results[name] = np.nan
            else:
                results[name] = NonScalarMetric.get_error_metric()

    return utilities.segregate_scalar_non_scalar(results)


def _score_text_ner(
        log_activity: Callable[[logging.Logger, str, Optional[str],
                                Optional[Dict[str, Any]]], Iterator[Optional[Any]]],
        log_traceback: Callable[[BaseException, logging.Logger, Optional[str],
                                 Optional[bool], Optional[Any]], None],
        y_test: Union[List[List[str]], np.ndarray],
        y_pred: Union[List[List[str]], np.ndarray],
        metrics: List[str]
) -> Dict[str, Union[float, Dict[str, Any]]]:
    # We are using seqeval to calculate metrics instead of sklearn for other classification problem
    # because seqeval supports evaluation at entity-level

    _validation.validate_ner(y_test, y_pred, metrics)
    _validation.log_ner_debug(y_test, y_pred)

    results = {}
    for name in metrics:
        if name in constants.CLASSIFICATION_NLP_NER_SET:
            try:
                metric_class = _scoring_utilities.get_metric_class_text_ner(name)
                metric = metric_class(y_test, y_pred)
                results[name] = metric.compute()
            except MemoryError:
                raise
            except Exception as e:
                safe_name = _scoring_utilities.get_safe_metric_name(name)
                logger.error("Scoring failed for NER metric {}".format(safe_name))
                log_traceback(e, logger, is_critical=False)
                if utilities.is_scalar(name):
                    results[name] = np.nan
                else:
                    results[name] = NonScalarMetric.get_error_metric()
    return utilities.segregate_scalar_non_scalar(results)


def _score_translation(
        log_activity: Callable[[logging.Logger, str, Optional[str],
                                Optional[Dict[str, Any]]], Iterator[Optional[Any]]],
        log_traceback: Callable[[BaseException, logging.Logger, Optional[str],
                                 Optional[bool], Optional[Any]], None],
        y_test: List[Any],
        y_pred: List[str],
        metrics: List[str],
        tokenizer: Any,
        smoothing: bool):
    """
    Compute model evaluation metrics for a translation task.

    y_test should be a list of list of string references (even if there is only one reference)
    y_pred should be a list of string predictions
    tokenizer could be any function that takes input a string, and returns a list of tokens

    :param y_test: Actual list of list of references
    :param y_pred: Actual list of predictions
    :param metrics: List of metric names for metrics to calculate.
    :param tokenizer: function that takes input a string, and returns a list of tokens
    :param smoothing: boolean to indicate if smoothing is required for bleu score
    """
    _validation.validate_translation(y_test, y_pred, metrics, tokenizer, smoothing)
    _validation.log_translation_debug(y_test, y_pred, tokenizer, smoothing)

    results = {}
    for name in metrics:
        safe_name = _scoring_utilities.get_safe_metric_name(name)
        max_ngram = constants.Metric.TRANSLATION_NGRAM_MAP[name]
        try:
            metric_class = _scoring_utilities.get_metric_class(name)
            metric = metric_class(y_test, y_pred, tokenizer, max_ngram, smoothing)
            results[name] = metric.compute()
        except MemoryError:
            raise
        except Exception as e:
            logger.error("Scoring failed for translation metric {}".format(safe_name))
            log_traceback(e, logger, is_critical=False)
            results[name] = np.nan
    return utilities.segregate_scalar_non_scalar(results)


def _score_summarization(
        log_activity: Callable[[logging.Logger, str, Optional[str],
                                Optional[Dict[str, Any]]], Iterator[Optional[Any]]],
        log_traceback: Callable[[BaseException, logging.Logger, Optional[str],
                                 Optional[bool], Optional[Any]], None],
        y_test: List[Any],
        y_pred: List[str],
        metrics: List[str],
        tokenizer: Any,
        aggregator: bool,
        stemmer: bool):
    """
    Compute model evaluation metrics for a summarization task.

    y_test should be a list of string references
    y_pred should be a list of string predictions
    tokenizer could be any function that takes input a string, and returns a list of tokens

    :param y_test: Actual list of list of references
    :param y_pred: Actual list of predictions
    :param metrics: List of metric names for metrics to calculate.
    :param tokenizer: function that takes input a string, and returns a list of tokens
    :params aggregator: Boolean to indicate whether to aggregate scores
    :params stemmer: Boolean to indicate whether to use Porter stemmer for word suffixes
    """
    _validation.validate_summarization(y_test, y_pred, metrics, tokenizer, aggregator, stemmer)
    _validation.log_summarization_debug(y_test, y_pred, tokenizer, aggregator, stemmer)

    results = {}
    safe_names = []
    for name in metrics:
        safe_names.append(_scoring_utilities.get_safe_metric_name(name))
    safe_names = ', '.join(safe_names)

    try:
        # NOTE: This will only work if all metrics are Rouge for summarization
        metric_class = _scoring_utilities.get_metric_class(list(metrics)[0])
        metric = metric_class(y_test, y_pred, metrics, tokenizer, aggregator, stemmer)
        results = metric.compute()
    except MemoryError:
        raise
    except Exception as e:
        logger.error("Scoring failed for summarization metrics {}".format(safe_names))
        log_traceback(e, logger, is_critical=False)
        for name in metrics:
            results[name] = np.nan
    return utilities.segregate_scalar_non_scalar(results)


def _score_text_generation(
        log_activity: Callable[[logging.Logger, str, Optional[str],
                                Optional[Dict[str, Any]]], Iterator[Optional[Any]]],
        log_traceback: Callable[[BaseException, logging.Logger, Optional[str],
                                 Optional[bool], Optional[Any]], None],
        y_test: List[Any],
        y_pred: List[str],
        metrics: List[str],
        tokenizer: Any,
        smoothing: bool,
        aggregator: bool,
        stemmer: bool):
    """
    Compute model evaluation metrics for a text generation task.

    y_test should be a list of list of string references
    y_pred should be a list of string predictions
    tokenizer could be any function that takes input a string, and returns a list of tokens

    :param y_test: Actual list of list of references
    :param y_pred: Actual list of predictions
    :param metrics: List of metric names for metrics to calculate.
    :param tokenizer: function that takes input a string, and returns a list of tokens
    :params smoothing: Boolean to indicate whether to smooth out the bleu score
    :params aggregator: Boolean to indicate whether to aggregate scores
    :params stemmer: Boolean to indicate whether to use Porter stemmer for word suffixes
    """
    _validation.validate_text_generation(y_test, y_pred, metrics, tokenizer,
                                         smoothing, aggregator, stemmer)
    _validation.log_text_generation_debug(y_test, y_pred, tokenizer,
                                          smoothing, aggregator, stemmer)

    results = {}
    for name in metrics:
        safe_name = _scoring_utilities.get_safe_metric_name(name)
        max_ngram = constants.Metric.TRANSLATION_NGRAM_MAP.get(name, None)
        try:
            metric_class = _scoring_utilities.get_metric_class(name)
            if max_ngram is not None:
                metric = metric_class(y_test, y_pred, tokenizer, max_ngram, smoothing)
            else:
                metric = metric_class(y_test, y_pred, [name], tokenizer, aggregator, stemmer)
            computed_result = metric.compute()
            results[name] = computed_result.get(name, None) \
                if isinstance(computed_result, dict) else computed_result
        except MemoryError:
            raise
        except Exception as e:
            logger.error("Scoring failed for text generation metric {}".format(safe_name))
            log_traceback(e, logger, is_critical=False)
            results[name] = np.nan
    return utilities.segregate_scalar_non_scalar(results)


def _score_qa(
        log_activity: Callable[[logging.Logger, str, Optional[str],
                                Optional[Dict[str, Any]]], Iterator[Optional[Any]]],
        log_traceback: Callable[[BaseException, logging.Logger, Optional[str],
                                 Optional[bool], Optional[Any]], None],
        y_test: List[Any],
        y_pred: List[str],
        metrics: List[str],
        tokenizer: Any,
        regexes_to_ignore: List[str],
        ignore_case: bool,
        ignore_punctuation: bool,
        ignore_numbers: bool):
    """
    Compute model evaluation metrics for a QA task.

    y_test should be a list of string references
    y_pred should be a list of string predictions
    tokenizer could be any function that takes input a string, and returns a
    list of tokens

    :param y_test: Actual list of list of references
    :param y_pred: Actual list of predictions
    :param metrics: List of metric names for metrics to calculate.
    :param tokenizer: function that takes input a string, and returns a list of tokens
    :params regexes_to_ignore: List of string regular expressions to ignore
    :params ignore_case: Boolean to indicate whether to ignore case
    :params ignore_punctuation: Boolean to indicate whether to ignore punctuation
    :params ignore_numbers: Boolean to indicate whether to ignore numbers
    """
    _validation.validate_qa(y_test, y_pred, metrics, tokenizer, regexes_to_ignore,
                            ignore_case, ignore_punctuation, ignore_numbers)
    _validation.log_qa_debug(y_test, y_pred, tokenizer, regexes_to_ignore,
                             ignore_case, ignore_punctuation, ignore_numbers)

    results = {}
    for name in metrics:
        safe_name = _scoring_utilities.get_safe_metric_name(name)
        try:
            metric_class = _scoring_utilities.get_metric_class(name)
            metric = metric_class(y_test, y_pred, tokenizer, regexes_to_ignore,
                                  ignore_case, ignore_punctuation, ignore_numbers)
            results[name] = metric.compute()
        except MemoryError:
            raise
        except Exception as e:
            logger.error("Scoring failed for QA metric {}".format(safe_name))
            log_traceback(e, logger, is_critical=False)
            results[name] = np.nan
    return utilities.segregate_scalar_non_scalar(results)


def _score_fill_mask(
        log_activity: Callable[[logging.Logger, str, Optional[str],
                                Optional[Dict[str, Any]]], Iterator[Optional[Any]]],
        log_traceback: Callable[[BaseException, logging.Logger, Optional[str],
                                 Optional[bool], Optional[Any]], None],
        y_test: List[Any],
        y_pred: List[str],
        metrics: List[str],
        model_id: Optional[str],
        batch_size: Optional[int],
        add_start_token: Optional[bool],):
    """
    Compute model evaluation metrics for a LM task.

    y_test should be a list of string references
    y_pred should be a list of string predictions

    :param y_test: Actual list of list of references
    :param y_pred: Actual list of predictions
    :param metrics: List of metric names for metrics to calculate.
    :param metrics: Language Modeling metrics to compute point estimates
    :param model_id: model used for calculating Perplexity.
                        Perplexity can only be calculated for causal language models.
    :param batch_size (int): the batch size to run texts through the model. Defaults to 16.
    :param add_start_token (bool): whether to add the start token to the texts,
        so the perplexity can include the probability of the first word. Defaults to True.
    """
    _validation.validate_fill_mask(y_test, y_pred, metrics, model_id, batch_size,
                                   add_start_token)
    _validation.log_fill_mask_debug(y_test, y_pred, model_id, batch_size,
                                    add_start_token)

    results = {}
    for name in metrics:
        safe_name = _scoring_utilities.get_safe_metric_name(name)
        try:
            metric_class = _scoring_utilities.get_metric_class(name)
            metric = metric_class(y_test, y_pred, model_id,
                                  batch_size, add_start_token)
            results[name] = metric.compute()
        except MemoryError:
            raise
        except Exception as e:
            logger.error("Scoring failed for Fill Mask metric {}".format(safe_name))
            log_traceback(e, logger, is_critical=False)
            results[name] = np.nan
    return utilities.segregate_scalar_non_scalar(results)


def _aggregate_scores(
        log_activity: Callable[[logging.Logger, str, Optional[str],
                                Optional[Dict[str, Any]]], Iterator[Optional[Any]]],
        log_traceback: Callable[[BaseException, logging.Logger, Optional[str],
                                 Optional[bool], Optional[Any]], None],
        scores: List[Dict[str, Dict[str, Any]]],
        metrics: List[str]
) -> Dict[str, Dict[str, Union[float, Dict[str, Any]]]]:
    """
    Compute mean scores across validation folds.

    :param scores: List of results from scoring functions.
    :param metrics: List of metrics to aggregate.
    :return: Dictionary containing the aggregated scores.
    """

    scores = [utilities.amalgamate_scalar_non_scalar(score) for score in scores]

    means = {}  # type: Dict[str, Union[float, Dict[str, Any]]]
    for name in metrics:
        if name not in scores[0]:
            logger.warning("Tried to aggregate metric {}, but {} was not found in scores".format(name, name))
            continue

        split_results = [score[name] for score in scores if name in score]
        _validation.log_failed_splits(split_results, name)
        metric_class = _scoring_utilities.get_metric_class(name)
        try:
            means[name] = metric_class.aggregate(split_results)
        except Exception as e:
            safe_name = _scoring_utilities.get_safe_metric_name(name)
            logger.error("Score aggregation failed for metric {}".format(safe_name))
            log_traceback(e, logger, is_critical=False)
            means[name] = NonScalarMetric.get_error_metric()

        try:
            name_extras = MetricExtrasConstants.MetricExtrasFormat.format(name)
            split_results_extras = [score[name_extras] for score in scores if name_extras in score]

            if len(split_results_extras) > 0:
                means_name_extras = {}  # type: Dict[str, List[float]]

                stats = split_results_extras[0].keys()
                for stat in stats:
                    means_name_extras[stat] = \
                        metric_class.aggregate([score[stat] for score in split_results_extras])

                means[name_extras] = means_name_extras

        except Exception as e:
            safe_name = _scoring_utilities.get_safe_metric_name(name)
            logger.error("Score aggregation failed for metric extras {}".format(safe_name))
            log_traceback(e, logger, is_critical=False)

    for train_type in ALL_TIME:
        train_times = [res[train_type] for res in scores if train_type in res]
        if train_times:
            means[train_type] = float(np.mean(train_times))

    return utilities.segregate_scalar_non_scalar(means)
