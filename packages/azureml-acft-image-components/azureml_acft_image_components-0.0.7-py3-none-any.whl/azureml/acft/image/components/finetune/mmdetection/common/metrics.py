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

"""MMDetection image OD and IS evaluation related functions."""

import numpy as np
import torch

from transformers import EvalPrediction
from typing import Dict, List, Tuple

from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals,
    InferenceParameters,
)
from azureml.acft.image.components.finetune.common import masktools
from azureml.acft.image.components.finetune.mmdetection.common.constants import (
    MmDetectionDatasetLiterals,
)
from azureml.acft.image.components.finetune.mmdetection.object_detection.model_wrapper import (
    ObjectDetectionModelWrapper as od_model_wrapper,
)
from azureml.acft.image.components.finetune.mmdetection.instance_segmentation.model_wrapper import (
    InstanceSegmentationModelWrapper as is_model_wrapper,
)
from azureml.metrics import compute_metrics
from azureml.metrics import list_metrics
from azureml.metrics.constants import Tasks as MetricsTasks

# TODO Compute metrics package is yet to define constants for literals like "boxes", "metrics" which are
#  used in this file. Replace these with constants from metrics package when it'll be available.


def _get_valid_index(
    labels: np.ndarray, box_scores: np.ndarray = None, box_score_threshold: float = None
) -> List:
    """
    Get the index of valid labels i.e, id >= 0 and box score above box score threshold
    :param labels: classification labels of image
    :param labels: nd-array
    :param box_scores: Optional, prediction score of bounding box
    :param box_scores: nd-array
    :param box_score_threshold: Optional, box score threshold
    :param box_score_threshold: float
    :return: index of valid labels
    :rtype: List

    Note: This helper function is used for preparing the model output and ground truth labels before
    feeding to compute_metrics. (It returns the valid indices of predictions, we then filtered out the invalid labels,
    bbox and masks).
    1. For prediction, It will only keep those indices which satisfy the following 2 conditions:
        1.1 label id >= 0 (basically, remove the padding that we intentially added for HF trainer.)
        1.2 the box scoring confidence >= box score threshold
        i.e., lbl >=0 and box_scores[index] >= box_score_threshold
    2. For ground truth, we don't have the box score. Hence, we only remove the padding.
    i.e., lbl >=0 and box_score is None
    """
    valid_index = []
    for index, lbl in enumerate(labels):
        if lbl >= 0 and (
            box_scores is None or box_scores[index] >= box_score_threshold
        ):
            valid_index.append(index)
    return valid_index


def _convert_masks_to_rle(masks: np.ndarray) -> List[Dict]:
    """
    Convert masks to rle as required by metrics functions
    :param masks: Binary masks
    :type masks: np.ndarray
    :return: List of masks in rle format
    :rtype: List of rle dict
    """
    rle_mask = list()
    for mask in masks:
        rle_mask.append(masktools.encode_mask_as_rle(torch.tensor(mask)))
    return rle_mask


def _prepare_prediction_labels(
    predictions: Tuple,
    box_score_threshold: float,
    output_keys_to_index_mapping: Dict[MmDetectionDatasetLiterals, int],
) -> List[Dict[str, np.ndarray]]:
    """
    This function transforms the predictions from HF trainer as required by the metrics functions.
    It also removes the padded (dummy) predictions added in model forward function.
    :param predictions: model prediction containing bboxes, labels and masks
    :type predictions: Tuple
    :param box_score_threshold: threshold for bounding box score
    :type box_score_threshold: float
    :param output_keys_to_index_mapping: mapping of keys to index in prediction tuple
    :type output_keys_to_index_mapping: dict
    :return: Transformed predictions as required by metrics compute function
    :rtype: List of prediction dictionary List[Dict[str, np.ndarray]]
    """
    batch_bboxes = predictions[
        output_keys_to_index_mapping[MmDetectionDatasetLiterals.BBOXES]
    ]
    batch_labels = predictions[
        output_keys_to_index_mapping[MmDetectionDatasetLiterals.LABELS]
    ]

    outputs: List[Dict] = list()
    for index, (bboxes, labels) in enumerate(zip(batch_bboxes, batch_labels)):
        keep_index = _get_valid_index(
            labels, box_scores=bboxes[:, 4], box_score_threshold=box_score_threshold
        )
        output = {
            "boxes": bboxes[keep_index][:, :4],
            "classes": labels[keep_index],
            "scores": bboxes[keep_index][:, 4],
        }

        # if len of prediction is greater than 5, then it will have mask information.
        if len(predictions) > 5:
            image_masks = predictions[
                output_keys_to_index_mapping[MmDetectionDatasetLiterals.MASKS]
            ][index]
            valid_masks = image_masks[keep_index]
            output["masks"] = _convert_masks_to_rle(valid_masks)

        outputs.append(output)
    return outputs


def _prepare_ground_truth_labels(
    ground_truths: Tuple,
    output_keys_to_index_mapping: Dict[MmDetectionDatasetLiterals, int],
) -> Tuple[List[Dict], List[Dict]]:
    """
    This function transforms the ground truth labels as required by the metrics functions.
    It also removes the padded (dummy) labels added in model forward function.
    :param ground_truths: Ground truth labels
    :type ground_truths: Tuple of ground truth
    :param output_keys_to_index_mapping: mapping of keys to index in prediction tuple
    :type output_keys_to_index_mapping: dict
    :return: Dictionaries of transformed ground truth and image_metadata
    :rtype: Tuple of Lists having gt and metadata dictionaries
    """
    batch_gt_bboxes = ground_truths[
        output_keys_to_index_mapping[MmDetectionDatasetLiterals.GT_BBOXES]
    ]
    batch_gt_labels = ground_truths[
        output_keys_to_index_mapping[MmDetectionDatasetLiterals.GT_LABELS]
    ]
    batch_gt_crowds = ground_truths[
        output_keys_to_index_mapping[MmDetectionDatasetLiterals.GT_CROWDS]
    ]

    gts: List[Dict] = list()
    meta_infos: List[Dict] = list()
    for index, (gt_bboxes, gt_labels, gt_crowds) in enumerate(
        zip(batch_gt_bboxes, batch_gt_labels, batch_gt_crowds)
    ):
        keep_index = _get_valid_index(gt_labels)

        ground_truth = {
            "boxes": gt_bboxes[keep_index],
            "classes": gt_labels[keep_index],
        }

        if len(ground_truths) > 5:
            gt_image_masks = ground_truths[
                output_keys_to_index_mapping[MmDetectionDatasetLiterals.GT_MASKS]
            ][index]
            gt_valid_masks = gt_image_masks[keep_index]
            ground_truth["masks"] = _convert_masks_to_rle(gt_valid_masks)

        image_metadata = {"iscrowd": gt_crowds[keep_index]}

        gts.append(ground_truth)
        meta_infos.append(image_metadata)
    return gts, meta_infos


def calculate_detection_metrics(eval_prediction: EvalPrediction, **kwargs) -> Dict:
    """
    compute and return metrics for Object Detection task
    :param eval_prediction: eval_prediction containing predictions and labels
    :type eval_prediction: Huggingface EvalPrediction
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    :return: Dictionary containing all metrics.
    :rtype: Dict
    """
    num_classes = kwargs[SettingLiterals.NUM_LABELS]
    task_name = kwargs[SettingLiterals.TASK_NAME]
    box_score_threshold = kwargs.get(
        SettingLiterals.BOX_SCORE_THRESHOLD,
        InferenceParameters.DEFAULT_BOX_SCORE_THRESHOLD,
    )
    iou_threshold = kwargs.get(
        SettingLiterals.IOU_THRESHOLD, InferenceParameters.DEFAULT_IOU_THRESHOLD
    )

    if task_name == Tasks.MM_INSTANCE_SEGMENTATION:
        metrics_list = list_metrics(MetricsTasks.IMAGE_INSTANCE_SEGMENTATION)
        task_type = MetricsTasks.IMAGE_INSTANCE_SEGMENTATION
        model_output_keys_ordering = is_model_wrapper.MODEL_OUTPUT_KEY_ORDERING
    else:
        metrics_list = list_metrics(MetricsTasks.IMAGE_OBJECT_DETECTION)
        task_type = MetricsTasks.IMAGE_OBJECT_DETECTION
        model_output_keys_ordering = od_model_wrapper.MODEL_OUTPUT_KEY_ORDERING
    output_keys_to_index_mapping = {
        value: index for index, value in enumerate(model_output_keys_ordering)
    }
    predictions = _prepare_prediction_labels(
        eval_prediction.predictions, box_score_threshold, output_keys_to_index_mapping
    )
    gts, img_meta_infos = _prepare_ground_truth_labels(
        eval_prediction.predictions, output_keys_to_index_mapping
    )

    metrics = compute_metrics(
        task_type=task_type,
        y_test=gts,
        image_meta_info=img_meta_infos,
        y_pred=predictions,
        num_classes=num_classes,
        iou_threshold=iou_threshold,
        metrics=metrics_list,
    )["metrics"]
    return metrics
