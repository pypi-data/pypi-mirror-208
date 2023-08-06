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

"""MMdetection object detection model wrapper class."""


import numpy as np
import os
import shutil
import torch

from mmcv import Config
from pathlib import Path
from torch import nn, Tensor
from torch.nn.utils.rnn import pad_sequence
from typing import Dict, List, Union, Any, Tuple, OrderedDict

from azureml.acft.common_components import get_logger_app, ModelSelectorDefaults
from azureml.acft.image.components.finetune.common.utils import get_current_device
from azureml.acft.image.components.finetune.mmdetection.common.constants import (
    MmDetectionDatasetLiterals,
)
from azureml.acft.image.components.model_selector.constants import ImageModelSelectorConstants

logger = get_logger_app(__name__)


class ObjectDetectionModelWrapper(nn.Module):
    """Wrapper class over object detection model of MMDetection framework."""
    MODEL_OUTPUT_KEY_ORDERING = [
        MmDetectionDatasetLiterals.GT_BBOXES,
        MmDetectionDatasetLiterals.GT_LABELS,
        MmDetectionDatasetLiterals.GT_CROWDS,
        MmDetectionDatasetLiterals.BBOXES,
        MmDetectionDatasetLiterals.LABELS,
    ]

    def __init__(
        self,
        mm_object_detection_model: nn.Module,
        config: Config,
        model_name_or_path: str,
        meta_file_path: str,
    ):
        """Wrapper class over object detection model of MMDetection.
        :param mm_object_detection_model: MM object detection model
        :type mm_object_detection_model: nn.Module
        :param config: MM Detection model configuration
        :type config: MMCV Config
        :param model_name_or_path: model name or path
        :type model_name_or_path: str
        :param meta_file_path: path to meta file
        :type meta_file_path: str
        """
        super().__init__()
        self.model = mm_object_detection_model
        self.config = config
        self.model_name = Path(model_name_or_path).stem
        self.meta_file_path = meta_file_path

    @classmethod
    def _get_bboxes_and_labels(
        cls, predicted_bbox: List[List[np.ndarray]]
    ) -> Tuple[Tensor, Tensor]:
        """
        Map the MM detection model's predicted label to the bbox and labels
        :param predicted_bbox: bbox of shape [Number of labels, Number of boxes, 5 [tl_x, tl_y, br_x, br_y,
        box_score]] format.
        :type predicted_bbox: List[List[np.ndarray]]
        :return: bounding boxes of shape [Number of boxes, 5 [tl_x, tl_y, br_x, br_y, box_score]] and labels of
        shape [Number of boxes, label id]
        :rtype: Tuple[Tensor, Tensor]
        """
        bboxes = torch.as_tensor(np.vstack(predicted_bbox))
        labels = [
            np.full(bbox.shape[0], i, dtype=np.int32)
            for i, bbox in enumerate(predicted_bbox)
        ]
        labels = torch.as_tensor(np.concatenate(labels))
        return bboxes, labels

    @classmethod
    def _pad_sequence(cls, sequences: Tensor, padding_value: float = -1, batch_first: bool = True) -> Tensor:
        """
        It stacks a list of Tensors sequences, and pads them to equal length.
        :param sequences: list of variable length sequences.
        :type sequences: Tensor
        :param padding_value: value for padded elements
        :type padding_value: float
        :param batch_first: output will be in B x T x * if True, or in T x B x * otherwise
        :type batch_first: bool
        :return: Tensor of size ``B x T x *`` if batch_first is True
        :rtype: Tensor
        """
        return pad_sequence(
            sequences, padding_value=padding_value, batch_first=batch_first
        ).to(get_current_device())

    @classmethod
    def _organize_ground_truth_for_trainer(
        cls,
        gt_bboxes: List[Tensor],
        gt_labels: List[Tensor],
        gt_crowds: List[Tensor],
        **kwargs,
    ) -> Dict[str, Tensor]:
        """
        Transform the batch of ground truth as required by the HF trainer.
        :param gt_bboxes: batch of ground truth bounding boxes
        :type gt_bboxes: list of tensor
        :param gt_labels: batch of ground truth class labels
        :type gt_labels: list of tensor
        :param gt_crowds: batch of ground truth crowds flag
        :type gt_crowds: list of tensor
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        :return: Dict of ground truth labels
        :rtype: Dict[str, Tensor]

        Note: The model needs the ground truth in dict of List of tensor format. List for batch and tensor for per
         image labels. But, the HF trainer need the dictionary of tensor, otherwise it will fail while concatenating
         the batches to form full dataset before passing to evaluation function.
         We will need to convert these Dict[List] to Dict[tensors]. List can have different size; for example,
         1st image can have 2 bbox and 2nd image can have 1 bbox. Hence, we need to pad the labels
         to have same dimension so that it can be converted to tensor.
        """
        output = dict()
        output[MmDetectionDatasetLiterals.GT_BBOXES] = ObjectDetectionModelWrapper._pad_sequence(gt_bboxes)
        output[MmDetectionDatasetLiterals.GT_LABELS] = ObjectDetectionModelWrapper._pad_sequence(gt_labels)
        output[MmDetectionDatasetLiterals.GT_CROWDS] = ObjectDetectionModelWrapper._pad_sequence(gt_crowds)
        return output

    @classmethod
    def _organize_predictions_for_trainer(
        cls, batch_predictions: List[List[np.ndarray]], img_metas: List[Dict]
    ) -> Dict[str, Tensor]:
        """
        Transform the batch of predicted labels as required by the HF trainer.
        :param batch_predictions: batch of predicted labels
        :type batch_predictions: List of bbox list for each image
        :param img_metas: batch of predicted labels
        :type img_metas: List of image metadata dictionary
        :return: Dict of predicted labels in tensor format
        :rtype: Dict[str, Tensor]

        Note: Same reasoning like _organize_ground_truth_for_trainer function but for predicted label
        """
        batch_bboxes, batch_labels = [], []
        for prediction in batch_predictions:
            bboxes, labels = ObjectDetectionModelWrapper._get_bboxes_and_labels(
                prediction
            )
            batch_bboxes.append(bboxes)
            batch_labels.append(labels)
        output = dict()
        output[MmDetectionDatasetLiterals.BBOXES] = ObjectDetectionModelWrapper._pad_sequence(batch_bboxes)
        output[MmDetectionDatasetLiterals.LABELS] = ObjectDetectionModelWrapper._pad_sequence(batch_labels)
        return output

    @classmethod
    def _convert_output_to_tuple(cls, output: Dict) -> Tuple:
        """Convert model output from dict to tuple to make it suitable for trainer distirubeted_concat method
        :param output: model output containing predictions and ground truth
        :type output: dict
        :return: output formatted in tuple
        :rtype: tuple
        """
        return tuple(output[key] for key in cls.MODEL_OUTPUT_KEY_ORDERING)

    def forward(self, **data) -> Union[Dict[str, Any], Tuple[Tensor, Tuple]]:
        """
        Model forward pass for training and validation mode
        :param data: Input data to model
        :type data: Dict
        :return: A dictionary of loss components in training mode OR Tuple of dictionary of predicted and ground
        labels in validation mode
        :rtype: Dict[str, Any] in training mode; Tuple[Tensor, Dict[str, Tensor]] in validation mode;

        Note: Input data dictionary consist of
            img: Tensor of shape (N, C, H, W) encoding input images.
            img_metas: list of image info dict where each dict has: 'img_shape', 'scale_factor', 'flip',
             and may also contain 'filename', 'ori_shape', 'pad_shape', and 'img_norm_cfg'. For details on the values
             of these keys see `mmdet/datasets/pipelines/formatting.py:Collect`.
            gt_bboxes - Ground truth bboxes for each image with shape (num_gts, 4) in [tl_x, tl_y, br_x, br_y] format.
            gt_labels - List of class indices corresponding to each box
            gt_crowds - List of "is crowds" (boolean) to each box
            gt_masks - List of masks (type BitmapMasks) for each image if task is instance_segmentation
        """
        if self.model.training:
            # GT_CROWDS is not required for training
            data.pop(MmDetectionDatasetLiterals.GT_CROWDS)
            return self.model.train_step(data, optimizer=None)
        else:
            img = data[MmDetectionDatasetLiterals.IMG]
            img_metas = data[MmDetectionDatasetLiterals.IMG_METAS]
            batch_predictions = self.model(
                img=[img], img_metas=[img_metas], return_loss=False
            )
            output: dict = self._organize_predictions_for_trainer(
                batch_predictions, img_metas
            )
            ground_truth: dict = self._organize_ground_truth_for_trainer(**data)
            output.update(ground_truth)

            dummy_loss = torch.asarray([]).to(get_current_device())

            return dummy_loss, self._convert_output_to_tuple(output)

    def save_pretrained(self, output_dir: os.PathLike, state_dict: OrderedDict) -> None:
        """
        Save finetuned weights and model configuration
        :param output_dir: Output directory to store the model
        :type output_dir: os.PathLike
        :param state_dict: Model state dictionary
        :return state_dict: Dict
        """
        # TODO: Revisit the logic for resuming training from checkpoint. Taking user input in python script
        #  may not be a good idea from security perspective. Or, it may not affect as user machine is individual.
        os.makedirs(output_dir, exist_ok=True)
        torch.save(state_dict, os.path.join(output_dir, ModelSelectorDefaults.MODEL_CHECKPOINT_FILE_NAME))
        self.config.dump(os.path.join(output_dir, self.model_name + ".py"))
        shutil.copy(self.meta_file_path,
                    os.path.join(output_dir, ImageModelSelectorConstants.MMLAB_MODEL_METAFILE_NAME))
        logger.info(f"Model saved at {output_dir}")
