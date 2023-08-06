# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2018-2023 OpenMMLab. All rights reserved.
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

"""MMdetection instance segmentation model wrapper class."""

import mmcv
import numpy as np
import torch

from mmcv import Config
from torch import nn, Tensor
from typing import List, Dict, Tuple

from azureml.acft.image.components.finetune.common.utils import get_current_device
from azureml.acft.image.components.finetune.mmdetection.common.constants import (
    MmDetectionDatasetLiterals,
)
from azureml.acft.image.components.finetune.mmdetection.object_detection.model_wrapper import (
    ObjectDetectionModelWrapper,
)


class InstanceSegmentationModelWrapper(ObjectDetectionModelWrapper):
    """Wrapper class over mm instance segmentation model of MMDetection framework."""
    MODEL_OUTPUT_KEY_ORDERING = [
        MmDetectionDatasetLiterals.GT_BBOXES,
        MmDetectionDatasetLiterals.GT_LABELS,
        MmDetectionDatasetLiterals.GT_CROWDS,
        MmDetectionDatasetLiterals.GT_MASKS,
        MmDetectionDatasetLiterals.BBOXES,
        MmDetectionDatasetLiterals.LABELS,
        MmDetectionDatasetLiterals.MASKS,
    ]

    def __init__(
        self,
        mm_instance_segmentation_model: nn.Module,
        config: Config,
        model_name_or_path: str,
        meta_file_path: str = None,
    ):
        """Wrapper class over mm instance segmentation model of MMDetection framework.
        :param mm_instance_segmentation_model: MM instance segmentation model
        :type mm_instance_segmentation_model: nn.Module
        :param config: MM Instance segmentation model configuration
        :type config: MMCV Config
        :param model_name_or_path: model name or path
        :type model_name_or_path: str
        :param meta_file_path: path to meta file
        :type meta_file_path: str
        """
        super(InstanceSegmentationModelWrapper, self).__init__(
            mm_instance_segmentation_model, config, model_name_or_path, meta_file_path
        )

    @classmethod
    def _get_segmentation_masks(cls, mask_result: List[List[np.ndarray]]) -> Tensor:
        """
        Map the model's predicted segmentation masks to the format required by the HF trainer
        :param mask_result:
        :type mask_result: List of masks
        :return: mask in tensor format
        :rtype: Tensor
        """
        mask = mmcv.concat_list(
            mask_result
        )  # Concatenate a list of list into a single list.
        if isinstance(mask[0], torch.Tensor):
            mask = torch.stack(mask, dim=0)
        else:
            mask = torch.as_tensor(np.stack(mask, axis=0))
        return mask

    @classmethod
    def _organize_predictions_for_trainer(
        cls,
        batch_predictions: List[Tuple[List[np.ndarray], List[np.ndarray]]],
        img_metas: List[Dict],
    ) -> Dict[str, Tensor]:
        """
        Transform the batch of predicted labels as required by the HF trainer.
        :param batch_predictions: batch of predicted labels
        :type batch_predictions: List of tuple containing list of bboxes and masks
        :param img_metas: batch of predicted labels
        :type img_metas: List of image metadata dictionary
        :return: Dict of predicted labels in tensor format
        :rtype: Dict[str, Tensor]

        Note: Same reasoning like _organize_ground_truth_for_trainer function but for predicted label
        """
        batch_bboxes, batch_labels, batch_masks = [], [], []
        for (predicted_bbox, predicted_mask), img_meta in zip(
            batch_predictions, img_metas
        ):
            if isinstance(predicted_mask, tuple):
                predicted_mask = predicted_mask[0]  # ms rcnn

            bboxes, labels = super()._get_bboxes_and_labels(predicted_bbox)
            if predicted_mask is not None and len(labels) > 0:
                masks = InstanceSegmentationModelWrapper._get_segmentation_masks(
                    predicted_mask
                )
            else:
                # The case when all predictions are below the box score threshold. Add empty mask tensor to satisfy
                # the pad_sequence criteria.
                height, width, channel = img_meta[
                    MmDetectionDatasetLiterals.IMAGE_ORIGINAL_SHAPE
                ]
                masks = torch.empty(0, height, width)

            batch_bboxes.append(bboxes)
            batch_labels.append(labels)
            batch_masks.append(masks)

        output = dict()
        output[MmDetectionDatasetLiterals.BBOXES] = super()._pad_sequence(batch_bboxes)
        output[MmDetectionDatasetLiterals.LABELS] = super()._pad_sequence(batch_labels)
        output[MmDetectionDatasetLiterals.MASKS] = super()._pad_sequence(batch_masks)
        return output

    @classmethod
    def _organize_ground_truth_for_trainer(
        cls,
        gt_bboxes: List[Tensor],
        gt_labels: List[Tensor],
        gt_crowds: List[Tensor],
        **kwargs
    ) -> Dict[str, Tensor]:
        """
        Transform the batch of ground truth as required by the HF trainer.
        :param gt_bboxes: batch of ground truth bounding boxes
        :type gt_bboxes: list of tensor
        :param gt_labels: batch of ground truth class labels
        :type gt_labels: list of tensor
        :param gt_crowds: batch of ground truth crowds flag
        :type gt_crowds: list of tensor
        :param kwargs: A dictionary of additional configuration parameters. For instance segmentation taak,
        it should contain the ground truth masks (bitmask type) in MmDetectionDatasetLiterals.GT_MASKS key.
        :type kwargs: dict
        :return: Dict of ground truth labels in Tensor type
        :rtype: Dict[str, Tensor]

        Note: The model needs the ground truth in dict of List of tensor format. List for batch and tensor for per
         image labels. But, the HF trainer need the dictionary of tensor, otherwise it will fail while concatenating
         the batches to form full dataset before passing to evaluation function.
         We will need to convert these Dict[List] to Dict[tensors]. List can have different size; for example,
         1st image can have 2 bbox and 2nd image can have 1 bbox. Hence, we need to pad the labels
         to have same dimension so that it can be converted to tensor.
        """
        output = super()._organize_ground_truth_for_trainer(
            gt_bboxes, gt_labels, gt_crowds
        )
        gt_masks = kwargs[MmDetectionDatasetLiterals.GT_MASKS]

        # convert from bitmap to tensor
        gt_masks_in_tensor = [
            mask.to_tensor(dtype=torch.bool, device=get_current_device())
            for mask in gt_masks
        ]

        output[MmDetectionDatasetLiterals.GT_MASKS] = super()._pad_sequence(gt_masks_in_tensor)
        return output
