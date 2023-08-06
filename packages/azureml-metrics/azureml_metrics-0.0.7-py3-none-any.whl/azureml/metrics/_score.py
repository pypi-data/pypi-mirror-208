# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Computation of AzureML model evaluation metrics."""
import logging
from typing import Any, Dict, Optional, Union, List

import numpy as np
import pandas as pd
import ast

from azureml.metrics import constants, utilities
from azureml.metrics.azureml_classification_metrics import AzureMLClassificationMetrics
from azureml.metrics.azureml_forecasting_metrics import AzureMLForecastingMetrics
from azureml.metrics.azureml_regression_metrics import AzureMLRegressionMetrics
from azureml.metrics.azureml_translation_metrics import AzureMLTranslationMetrics
from azureml.metrics.azureml_summarization_metrics import AzureMLSummarizationMetrics
from azureml.metrics.azureml_qa_metrics import AzureMLQAMetrics
from azureml.metrics.azureml_text_ner_metrics import AzureMLTextNERMetrics
from azureml.metrics.azureml_fill_mask_metrics import AzureMLFillMaskMetrics
from azureml.metrics.azureml_text_generation_metrics import AzureMLTextGenerationMetrics
from azureml.metrics.azureml_od_is_metrics import AzureMLODISMetrics, AzureMLODMetrics, AzureMLISMetrics

logger = logging.getLogger(__name__)


def compute_metrics(*,
                    task_type: constants.TASKS,
                    y_test: Optional[Union[np.ndarray, pd.DataFrame, List]] = None,
                    # Either y_pred or y_pred_proba should be passed for classification
                    y_pred: Optional[Union[np.ndarray, pd.DataFrame, List]] = None,
                    y_pred_proba: Optional[Union[np.ndarray, pd.DataFrame, List]] = None,
                    **kwargs) -> Dict[str, Dict[str, Any]]:
    """Given task type, y_test, y_pred or y_pred_proba compute metrics for the respective task.

        :param task_type: Accepts an argument of type constants.Tasks for which metrics have to be computed.
            Can accept from any of the values constants.Tasks.CLASSIFICATION, constants.Tasks.REGRESSION,
            constants.Tasks.TEXT_CLASSIFICATION, constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL,
            constants.Tasks.TEXT_NER, constants.Tasks.SUMMARIZATION, constants.Tasks.TRANSLATION,
            constants.Tasks.QUESTION_ANSWERING, constants.Tasks.IMAGE_OBJECT_DETECTION,
            constants.Tasks.IMAGE_INSTANCE_SEGMENTATION, constants.Tasks.FORECASTING.
        :param y_test: Ground truths or reference values.
            optional for computing few of language_modeling metrics.
        :param y_pred: Prediction values.
        :param y_pred_proba: Predicted probability values.

        Example for multiclass classification:
        --------------------------------------
        from azureml.metrics import compute_metrics, constants
        y_pred = [0, 2, 1, 3]
        y_true = [0, 1, 2, 3]
        compute_metrics(task_type=constants.Tasks.CLASSIFICATION, y_test=y_true,
                           y_pred=y_pred)

        Example for multilabel classification:
        --------------------------------------
        from azureml.metrics import compute_metrics, constants
        y_test = np.array([[1, 1, 0],
                        [0, 1, 0],
                        [0, 1, 1],
                        [1, 0, 1]])
        y_pred_proba = np.array([[0.9, 0.6, 0.4],
                                    [0.3, 0.8, 0.6],
                                    [0.1, 0.9, 0.8],
                                    [0.7, 0.1, 0.6]])
        # class labels should be in same order as probability values
        class_labels = np.array([0, 1, 2])
        result = compute_metrics(task_type=constants.Tasks.CLASSIFICATION, y_test=y_test,
                                    y_pred_proba=y_pred_proba, multilabel=True)

        Example for regression:
        -----------------------
        from azureml.metrics import compute_metrics, constants
        result = compute_metrics(task_type=constants.Tasks.REGRESSION, y_test=[0.1, 0.2],
                                    y_pred=[0.15, 0.2], y_max=0, y_min=1, y_std=2, bin_info=2)

        Example for text-ner:
        ---------------------
        from azureml.metrics import compute_metrics, constants
        y_true = [['O', 'O', 'O', 'B-MISC', 'I-MISC', 'I-MISC', 'O'], ['B-PER', 'I-PER', "O"]]
        y_pred = [['O', 'O', 'B-MISC', 'I-MISC', 'I-MISC', 'I-MISC', 'O'], ['B-PER', 'I-PER', 'O']]
        result = compute_metrics(task_type=constants.Tasks.TEXT_NER, y_test=y_true, y_pred=y_pred)

        Example for translation:
        ------------------------
        from azureml.metrics import compute_metrics, constants
        y_pred = ["hello there general kenobi","foo bar foobar", "blue & red"]
        y_test = [["hello there general kenobi san"], ["foo bar foobar"], ["blue & green"]]
        result = compute_metrics(task_type=constants.Tasks.TRANSLATION, y_test=y_test, y_pred=y_pred)

        Example for summarization:
        --------------------------
        from azureml.metrics import compute_metrics, constants
        y_pred = ["hello there general kenobi","foo bar foobar", "blue & red"]
        y_test = [["hello there general kenobi san"], ["foo bar foobar"], ["blue & green"]]
        result = compute_metrics(task_type=constants.Tasks.SUMMARIZATION, y_test=y_test, y_pred=y_pred)

        Example for question-answering:
        -------------------------------
        from azureml.metrics import compute_metrics, constants
        y_pred = ["hello there general kenobi the 123","foo bar foobar", "ram 234", "sid"]
        y_test = ["hello there general kenobi san", "foo bar foobar", "ram 23", "sid$"]
        result = compute_metrics(task_type=constants.Tasks.QUESTION_ANSWERING, y_test=y_test, y_pred=y_pred)

        Example for fill-mask:
        ---------------------
        from azureml.metrics import compute_metrics, constants
        y_pred = ["hi", "green and blue", "he dances"]
        compute_metrics(task_type=constants.Tasks.FILL_MASK, y_pred=y_pred,
                        model_id="gpt2")

        Example for text_generation:
        ----------------------------
        from azureml.metrics import compute_metrics, constants
        y_pred = ["hello there general kenobi","foo bar foobar", "blue & red"]
        y_test = [["hello there general kenobi san"], ["foo bar foobar"], ["blue & green"]]
        result = compute_metrics(task_type=constants.Tasks.TEXT_GENERATION, y_test=y_test, y_pred=y_pred)

        Example for object-detection:
        -------------------------------
        from azureml.metrics import compute_metrics
        y_test = [{
                "boxes": np.array([[160, 120, 320, 240]], dtype=np.float32),
                "classes": np.array([1])
            }]
        image_meta_info = [{
                "areas": [60000],
                "iscrowd": [0],
                "filename": "image_1.jpg",
                "height": 640,
                "width": 480,
                "original_width": 640,
                "original_height": 480,
            }]
        y_pred = [{
                "boxes": np.array([[160, 120, 320, 240]], dtype=np.float32),
                "classes": np.array([1]),
                "scores": np.array([0.75]),
            }]
        result = compute_metrics(task_type=constants.Tasks.IMAGE_OBJECT_DETECTION, y_test=y_test,
                                    y_pred=y_pred,image_meta_info=image_meta_info)

        Example for instance-segmentation:
        -------------------------------
        from azureml.metrics import compute_metrics
        from pycocotools import mask as pycoco_mask
        def _rle_mask_from_bbox(bbox, height, width):
            x1, y1, x2, y2 = bbox
            polygon = [[x1, y1, x2, y1, x2, y2, x1, y2, x1, y1]]
            rle_masks = pycoco_mask.frPyObjects(polygon, height, width)
            return rle_masks[0]

        y_test = [{
                "boxes": np.array([[160, 120, 320, 240]], dtype=np.float32),
                "classes": np.array([1]),
                "masks": [_rle_mask_from_bbox([1, 0, 2, 100], 640, 640)],
            }]
        image_meta_info = [{
                "areas": [60000],
                "iscrowd": [0],
                "filename": "image_1.jpg",
                "height": 640,
                "width": 480,
                "original_width": 640,
                "original_height": 480,
            }]
        y_pred = [{
                "boxes": np.array([[160, 120, 320, 240]], dtype=np.float32),
                "masks": [_rle_mask_from_bbox([1, 0, 2, 100], 640, 640)],
                "classes": np.array([1]),
                "scores": np.array([0.75]),
            }]
        result = compute_metrics(task_type=constants.Tasks.IMAGE_INSTANCE_SEGMENTATION, y_test=y_test,
                                        y_pred=y_pred,image_meta_info=image_meta_info)

        Example for forecasting:
        >>>from azureml.metrics import compute_metrics, constants
        >>>X = pd.DataFrame({
           'date': pd.date_range('2001-01-01', freq='D', periods=42),
           'ts_id': 'a',
           'target': np.random.rand(42)
           })
        >>>X_train = X.iloc[:-10]
        >>>y_train = X_train.pop('target').values
        >>>X_test = X.iloc[-10:]
        >>>y_test = X_test.pop('target').values
        >>>y_pred = np.random.rand(10)
        >>>result = compute_metrics(
            task_type=constants.Tasks.FORECASTING,
            y_test=y_test,
            y_pred=y_pred,
            X_train=X_train,
            y_train=y_train,
            time_column_name='date',
            time_series_id_column_names=['ts_id'],
            X_test=X_test)
    """
    # Step 1: Check either y_pred or y_pred_proba exist
    # Step 2: Instantiate Metrics Class object on the basis of task type
    #   and pass in necessary parameters while creating object
    # Step 3: Call compute method of class object to compute and fetch metrics
    if y_test is None:
        if task_type in [constants.Tasks.FILL_MASK]:
            metrics_list = kwargs.get("metrics", set())
            supported_metrics_list = set(metrics_list).intersection(constants.Metric.FILL_MASK_SPECIAL_SET)
            kwargs["metrics"] = [metric for metric in constants.Metric.FILL_MASK_SET] \
                if len(supported_metrics_list) == 0 else supported_metrics_list
            logger.warning(f"Computing metrics for {kwargs['metrics']} as y_test is None.")
        else:
            raise Exception("y_test argument is needed for compute_metrics")

    if y_pred is None and y_pred_proba is None:
        pred_proba_msg = "Either y_pred or y_pred_proba" if task_type != constants.Tasks.REGRESSION else "y_pred"
        raise Exception("{} should exist.".format(pred_proba_msg))

    if isinstance(y_test, pd.DataFrame) or isinstance(y_pred, pd.DataFrame):
        if (hasattr(y_test, "columns") and len(y_test.columns) != 1) or \
                (hasattr(y_pred, "columns") and len(y_pred.columns) != 1):
            exception_message = "y_test and y_pred should have only one column in the dataframe to compute metrics."
            raise Exception(exception_message)

    # Reading common keyword arguments related to telemetry
    custom_dimensions = kwargs.pop('custom_dimensions', None)
    log_activity = kwargs.pop('log_activity', None)
    log_traceback = kwargs.pop('log_traceback', None)

    common_args = ["custom_dimensions", "log_activity", "log_traceback"]

    if task_type in [constants.Tasks.CLASSIFICATION, constants.Tasks.TEXT_CLASSIFICATION,
                     constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL]:
        metrics_list = kwargs.pop('metrics', None)
        class_labels = kwargs.pop('class_labels', None)
        train_labels = kwargs.pop('train_labels', None)
        sample_weight = kwargs.pop('sample_weight', None)
        y_transformer = kwargs.pop('y_transformer', None)
        use_binary = kwargs.pop('use_binary', False)
        enable_metric_confidence = kwargs.pop('enable_metric_confidence', False)
        multilabel = kwargs.pop('multilabel', False)
        positive_label = kwargs.pop('positive_label', None)
        confidence_metrics = kwargs.pop('confidence_metrics', None)

        if task_type == constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL:
            multilabel = True

        classification_kwargs = ["metrics", "class_labels", "train_labels", "sample_weight",
                                 "y_transformer", "use_binary", "enable_metric_confidence",
                                 "multilabel", "positive_label", "confidence_metrics"]

        check_kwargs(kwargs, task_type, classification_kwargs, common_args)

        metrics = AzureMLClassificationMetrics(
            metrics=metrics_list,
            class_labels=class_labels,
            train_labels=train_labels,
            sample_weight=sample_weight,
            y_transformer=y_transformer,
            use_binary=use_binary,
            enable_metric_confidence=enable_metric_confidence,
            multilabel=multilabel,
            positive_label=positive_label,
            confidence_metrics=confidence_metrics,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred, y_pred_probs=y_pred_proba)

    elif task_type == constants.Tasks.REGRESSION:
        metrics_list = kwargs.pop("metrics", None)
        y_max = kwargs.pop("y_max", None)
        y_min = kwargs.pop("y_min", None)
        y_std = kwargs.pop("y_std", None)
        bin_info = kwargs.pop("bin_info", None)
        sample_weight = kwargs.pop("sample_weight", None)
        enable_metric_confidence = kwargs.pop("enable_metric_confidence", False)
        confidence_metrics = kwargs.pop("confidence_metrics", None)

        regression_kwargs = ["metrics", "y_max", "y_min", "y_std",
                             "bin_info", "sample_weight", "enable_metric_confidence",
                             "confidence_metrics"]

        check_kwargs(kwargs, task_type, regression_kwargs, common_args)

        metrics = AzureMLRegressionMetrics(
            metrics=metrics_list,
            y_max=y_max,
            y_min=y_min,
            y_std=y_std,
            bin_info=bin_info,
            sample_weight=sample_weight,
            enable_metric_confidence=enable_metric_confidence,
            confidence_metrics=confidence_metrics,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)

    elif task_type == constants.Tasks.TEXT_NER:
        label_list = kwargs.pop('label_list', None)
        metrics_list = kwargs.pop('metrics', None)

        ner_kwargs = ["label_list", "metrics"]

        check_kwargs(kwargs, task_type, ner_kwargs, common_args)

        if label_list is None:
            label_list = list({label for row in y_test for label in row})

        metrics = AzureMLTextNERMetrics(
            label_list=label_list,
            metrics=metrics_list,
            custom_dimensions=custom_dimensions,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
    elif task_type == constants.Tasks.TRANSLATION:
        metrics_list = kwargs.pop('metrics', None)
        tokenizer = kwargs.pop('tokenizer', None)
        smoothing = kwargs.pop('smoothing', False)

        translation_kwargs = ['metrics', 'tokenizer', 'smoothing']
        check_kwargs(kwargs, task_type, translation_kwargs, common_args)

        metrics = AzureMLTranslationMetrics(
            metrics=metrics_list,
            tokenizer=tokenizer,
            smoothing=smoothing,
            custom_dimensions=custom_dimensions,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
    elif task_type == constants.Tasks.SUMMARIZATION:
        metrics_list = kwargs.pop('metrics', None)
        tokenizer = kwargs.pop('tokenizer', None)
        aggregator = kwargs.pop('aggregator', True)
        stemmer = kwargs.pop('stemmer', False)

        summarization_kwargs = ['metrics', 'tokenizer', 'aggregator', 'stemmer']
        check_kwargs(kwargs, task_type, summarization_kwargs, common_args)

        metrics = AzureMLSummarizationMetrics(
            metrics=metrics_list,
            tokenizer=tokenizer,
            aggregator=aggregator,
            stemmer=stemmer,
            custom_dimensions=custom_dimensions,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
    elif task_type == constants.Tasks.QUESTION_ANSWERING:
        metrics_list = kwargs.pop('metrics', None)
        tokenizer = kwargs.pop('tokenizer', None)
        regexes_to_ignore = kwargs.pop('regexes_to_ignore', None)
        ignore_case = kwargs.pop('ignore_case', False)
        ignore_punctuation = kwargs.pop('ignore_punctuation', False)
        ignore_numbers = kwargs.pop('ignore_numbers', False)

        qa_kwargs = ['metrics', 'tokenizer', 'regexes_to_ignore', 'ignore_case',
                     'ignore_punctuation', 'ignore_numbers']
        check_kwargs(kwargs, task_type, qa_kwargs, common_args)
        metrics = AzureMLQAMetrics(
            metrics=metrics_list,
            tokenizer=tokenizer,
            regexes_to_ignore=regexes_to_ignore,
            ignore_case=ignore_case,
            ignore_punctuation=ignore_punctuation,
            ignore_numbers=ignore_numbers,
            custom_dimensions=custom_dimensions,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
    elif task_type == constants.Tasks.FILL_MASK:
        metrics_list = kwargs.pop("metrics", None)

        # perplexity keyword arguments
        # using gpt2 as default model_id
        model_id = kwargs.pop("model_id", "gpt2")
        batch_size = kwargs.pop("batch_size", 16)
        add_start_token = kwargs.pop("add_start_token", True)

        lm_kwargs = ["metrics", "model_id", "batch_size", "add_start_token"]
        check_kwargs(kwargs, task_type, lm_kwargs, common_args)

        metrics = AzureMLFillMaskMetrics(
            metrics=metrics_list,
            model_id=model_id,
            batch_size=batch_size,
            add_start_token=add_start_token,
            custom_dimensions=custom_dimensions,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
    elif task_type == constants.Tasks.TEXT_GENERATION:
        metrics_list = kwargs.pop("metrics", None)

        # bleu keyword arguments
        tokenizer = kwargs.pop('tokenizer', None)
        smoothing = kwargs.pop('smoothing', False)

        # rouge keyword arguments
        aggregator = kwargs.pop('aggregator', True)
        stemmer = kwargs.pop('stemmer', False)

        text_generation_kwargs = ["metrics", "tokenizer", "smoothing",
                                  "aggregator", "stemmer"]
        check_kwargs(kwargs, task_type, text_generation_kwargs, common_args)

        metrics = AzureMLTextGenerationMetrics(
            metrics=metrics_list,
            tokenizer=tokenizer,
            smoothing=smoothing,
            aggregator=aggregator,
            stemmer=stemmer,
            custom_dimensions=custom_dimensions,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred)
    elif task_type == constants.Tasks.FORECASTING:
        # Parameters common with regression task
        metrics_list = kwargs.pop('metrics', None)
        sample_weight = kwargs.pop("sample_weight", None)
        X_train = kwargs.pop("X_train", None)
        y_train = kwargs.pop("y_train", None)
        y_std = kwargs.pop("y_std", None)
        # Forecasting-specific parameters
        time_series_id_column_names = kwargs.pop("time_series_id_column_names", None)
        aggregation_method = kwargs.pop("aggregation_method", np.mean)
        time_column_name = kwargs.pop("time_column_name", None)
        X_test = kwargs.pop("X_test", None)
        y_min_dict = kwargs.pop("y_min_dict", None)
        y_max_dict = kwargs.pop("y_max_dict", None)
        forecasting_kwargs = ["metrics", "sample_weight",
                              "X_train", "X_test", "y_train", "y_std",
                              "time_series_id_column_names",
                              "aggregation_method", "time_column_name", "y_min_dict",
                              "y_max_dict"]
        check_kwargs(kwargs, task_type, forecasting_kwargs)
        metrics = AzureMLForecastingMetrics(
            metrics=metrics_list,
            sample_weight=sample_weight,
            X_train=X_train,
            y_train=y_train,
            y_std=y_std,
            time_series_id_column_names=time_series_id_column_names,
            time_column_name=time_column_name,
            aggregation_method=aggregation_method,
            custom_dimensions=custom_dimensions,
            y_min_dict=y_min_dict,
            y_max_dict=y_max_dict,
            log_activity=log_activity,
            log_traceback=log_traceback)
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred, X_test=X_test)
    elif task_type in [constants.Tasks.IMAGE_OBJECT_DETECTION, constants.Tasks.IMAGE_INSTANCE_SEGMENTATION]:
        metrics_list = kwargs.pop("metrics", None)
        task_is_detection = task_type == constants.Tasks.IMAGE_OBJECT_DETECTION
        num_classes = kwargs.pop("num_classes", None)
        iou_threshold = kwargs.pop("iou_threshold", None)
        if num_classes is None:
            raise Exception("The number of classes must be specified for {} tasks.".format(task_type))

        # Extract the additional image-related argument required for object detection / instance segmentation.
        image_meta_info = kwargs.pop("image_meta_info", None)
        if image_meta_info is None:
            raise Exception("The image meta information must be specified for {} tasks.".format(task_type))

        od_is_kwargs = ["metrics", "num_classes", "iou_threshold", "image_meta_info"]
        check_kwargs(kwargs, task_type, od_is_kwargs, common_args)

        metrics = AzureMLODISMetrics(
            task_is_detection=task_is_detection,
            num_classes=num_classes,
            iou_threshold=iou_threshold,
            metrics=metrics_list,
        )
        computed_metrics = metrics.compute(y_test=y_test, y_pred=y_pred, image_meta_info=image_meta_info)
    else:
        supported_tasks = [constants.Tasks.FORECASTING, constants.Tasks.CLASSIFICATION,
                           constants.Tasks.REGRESSION, constants.Tasks.SUMMARIZATION,
                           constants.Tasks.TRANSLATION, constants.Tasks.FILL_MASK,
                           constants.Tasks.QUESTION_ANSWERING, constants.Tasks.IMAGE_OBJECT_DETECTION,
                           constants.Tasks.IMAGE_INSTANCE_SEGMENTATION] + constants.Tasks.ALL_TEXT
        raise Exception(f"Invalid task type. Please choose among the following task types : {supported_tasks}")
    return computed_metrics


def score(*,
          task_type: constants.TASKS,
          model: Any,
          X_test: Any,
          y_test: Union[np.ndarray, pd.DataFrame, List],
          **kwargs) -> Dict[str, Dict[str, Any]]:
    """Given task type, model, y_test, y_pred or y_pred_proba compute predictions and the respective metrics.

        :param task_type: Accepts an argument of type constants.Tasks for which metrics have to be computed.
            Can accept from any of the values constants.Tasks.CLASSIFICATION, constants.Tasks.REGRESSION,
            constants.Tasks.TEXT_CLASSIFICATION, constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL,
            constants.Tasks.TEXT_NER, constants.Tasks.FORECASTING.
        :param model: Any model which has a callable predict method that generates predictions.
        :param X_test: Test data which is sent to the model to compute predictions.
        :param y_test: Ground truths or references.
    """
    # Step 1: Generate predictions using model
    # Step 2: Extract whether predict proba is required, compute and add to kwargs if yes
    # Step 3: Call compute metrics method and pass appropriate kwargs to compute and fetch metrics

    if not (hasattr(model, "predict") and callable(getattr(model, 'predict'))):
        raise Exception("Model should have callable predict method.")

    try:
        if hasattr(model, "forecast") and callable(getattr(model, 'forecast')):
            # In the forecast data we are not guaranteed to have the same
            # dimension of output data as the input so we have to preaggregate
            # the data here.
            if 'X_train' in kwargs and 'y_train' in kwargs:
                kwargs['X_train'], kwargs['y_train'] = model.preaggregate_data_set(
                    kwargs['X_train'], kwargs['y_train'], is_training_set=True)
            X_test_agg, y_test = model.preaggregate_data_set(X_test, y_test)
            y_pred, _ = model.forecast(X_test)
            X_test = X_test_agg
            # Take forecasting-specific parameters from the model.
            kwargs["time_series_id_column_names"] = model.grain_column_names
            kwargs["time_column_name"] = model.time_column_name
        else:
            y_pred = model.predict(X_test)
            y_pred = utilities.check_and_convert_to_np(y_pred)

        multilabel = kwargs.get("multilabel", False)
        if multilabel or (task_type in [constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL,
                                        constants.Tasks.TEXT_NER]):
            y_pred = [ast.literal_eval(label) for label in y_pred]
    except Exception as e:
        exception_msg = "Error occurred while calling predict method on the model."
        raise Exception(exception_msg + str(e))

    compute_probs = kwargs.get("compute_probs", False)
    if task_type in [constants.Tasks.CLASSIFICATION, constants.Tasks.REGRESSION] and \
            kwargs.get("enable_metric_confidence", False):
        compute_probs = True
    elif task_type == constants.Tasks.FORECASTING:
        kwargs['X_test'] = X_test
    if compute_probs:
        if not (hasattr(model, "predict_proba") and callable(getattr(model, 'predict_proba'))):
            raise Exception("Model should have callable predict_proba method when compute_probs is set to True.")

        try:
            y_pred_proba = model.predict_proba(X_test)
            kwargs["y_pred_proba"] = y_pred_proba
        except Exception as e:
            exception_msg = "Error occurred while calling predict_proba method on the model."
            raise Exception(exception_msg + str(e))

    metrics = compute_metrics(task_type=task_type,
                              y_test=y_test,
                              y_pred=y_pred,
                              **kwargs)

    return metrics


def list_metrics(task_type: constants.TASKS,
                 multilabel: Optional[bool] = False) -> List[str]:
    """Get the list of supported metrics for provided task type.

        :param task_type: Accepts an argument of type constants.Tasks for which metrics have to be computed.
            Can accept from any of the values from constants.Tasks Ex: constants.Tasks.CLASSIFICATION,
            constants.Tasks.REGRESSION, constants.Tasks.TEXT_CLASSIFICATION,
            constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL,
            constants.Tasks.TEXT_NER.
        :param multilabel: Accepts a boolean argument which indicates multilabel classification.

        :return: List of supported metrics based on task type.

        Example for multiclass classification:
        --------------------------------------
        >>>from azureml.metrics import list_metrics, constants
        >>>list_metrics(task_type=constants.Tasks.CLASSIFICATION)

        Example for multilabel classification:
        --------------------------------------
        >>>from azureml.metrics import list_metrics, constants
        >>>list_metrics(task_type=constants.Tasks.CLASSIFICATION, multilabel=True)

        Example for multiclass text classification:
        -------------------------------------------
        >>>from azureml.metrics import list_metrics, constants
        >>>list_metrics(task_type=constants.Tasks.CLASSIFICATION)

        Example for multilabel text classification:
        -------------------------------------------
        >>>from azureml.metrics import list_metrics, constants
        >>>list_metrics(task_type=constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL)

        Example for text named entity recognition:
        ------------------------------------------
        >>>from azureml.metrics import list_metrics, constants
        >>>list_metrics(task_type=constants.Tasks.TEXT_NER)

        Example for translation:
        ------------------------
        >>>from azureml.metrics import list_metrics, constants
        >>>list_metrics(task_type=constants.Tasks.TRANSLATION)

        Example for summarization:
        --------------------------
        >>>from azureml.metrics import list_metrics, constants
        >>>list_metrics(task_type=constants.Tasks.SUMMARIZATION)

        Example for question answering:
        -------------------------------
        >>>from azureml.metrics import list_metrics, constants
        >>>list_metrics(task_type=constants.Tasks.QUESTION_ANSWERING)

        Example for text generation:
        -------------------------------
        >>>from azureml.metrics import list_metrics, constants
        >>>list_metrics(task_type=constants.Tasks.TEXT_GENERATION)

        Example for language modeling:
        -------------------------------
        >>>from azureml.metrics import list_metrics, constants
        >>>list_metrics(task_type=constants.Tasks.FILL_MASK)

        Example for object detection:
        --------------------------
        >>>from azureml.metrics import list_metrics, constants
        >>>list_metrics(task_type=constants.Tasks.IMAGE_OBJECT_DETECTION)

        Example for instance segmentation:
        -------------------------------
        >>>from azureml.metrics import list_metrics, constants
        >>>list_metrics(task_type=constants.Tasks.IMAGE_INSTANCE_SEGMENTATION)
    """
    task_options = {
        constants.Tasks.CLASSIFICATION: AzureMLClassificationMetrics,
        constants.Tasks.REGRESSION: AzureMLRegressionMetrics,
        constants.Tasks.TEXT_CLASSIFICATION: AzureMLClassificationMetrics,
        constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL: AzureMLClassificationMetrics,
        constants.Tasks.TEXT_NER: AzureMLTextNERMetrics,
        constants.Tasks.TRANSLATION: AzureMLTranslationMetrics,
        constants.Tasks.SUMMARIZATION: AzureMLSummarizationMetrics,
        constants.Tasks.QUESTION_ANSWERING: AzureMLQAMetrics,
        constants.Tasks.FILL_MASK: AzureMLFillMaskMetrics,
        constants.Tasks.TEXT_GENERATION: AzureMLTextGenerationMetrics,
        constants.Tasks.IMAGE_OBJECT_DETECTION: AzureMLODMetrics,
        constants.Tasks.IMAGE_INSTANCE_SEGMENTATION: AzureMLISMetrics,
        constants.Tasks.FORECASTING: AzureMLForecastingMetrics
    }

    result = task_options.get(task_type, None)

    if result is None:
        return f"Metrics are not implemented for provided task type : {task_type}."
    elif result == AzureMLClassificationMetrics:
        if task_type == constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL:
            multilabel = True
        metrics = result.list_metrics(multilabel=multilabel)
    else:
        metrics = result.list_metrics()

    return metrics


def check_kwargs(kwargs: Dict,
                 task_type: str,
                 task_type_args: List[str],
                 common_args: List[str] = None) -> None:
    """Check for presence of any additional kwargs which are unrelated/typos.

        :param kwargs: additional/ununsed keyword arguments.
        :param task_type: Accepts an argument of type constants.Tasks for which metrics have to be computed.
            Can accept from any of the values constants.Tasks.CLASSIFICATION, constants.Tasks.REGRESSION,
            constants.Tasks.TEXT_CLASSIFICATION, constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL,
            constants.Tasks.TEXT_NER.
        :param common_args: List of arguments which are accepted for all task_types.
        :param task_type_args: keyword arguments based on task type.
    """
    if len(kwargs) > 0:
        if common_args is not None:
            task_type_args += common_args

        warning_message = f"We have unused keyword arguments : {kwargs}\n" + \
                          f"Applicable keyword arguments for {task_type} are {task_type_args}."

        logger.warning(warning_message)
