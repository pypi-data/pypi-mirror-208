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

"""MMDetection model related classes."""

from __future__ import annotations
from typing import Dict, Any, List

from mmcv import Config
from mmcv.runner import load_checkpoint
from mmdet.models import build_detector
from torch import nn

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals,
    InferenceParameters,
)
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.mmdetection.common.constants import (
    MmDetectionConfigLiterals,
)
from azureml.acft.image.components.finetune.mmdetection.instance_segmentation.model_wrapper import (
    InstanceSegmentationModelWrapper,
)
from azureml.acft.image.components.finetune.mmdetection.object_detection.model_wrapper import (
    ObjectDetectionModelWrapper,
)
from azureml.acft.image.components.finetune.interfaces.azml_interface import (
    AzmlModelInterface,
)
from azureml.acft.image.components.model_selector.constants import ImageModelSelectorConstants

logger = get_logger_app(__name__)


class DetectionConfigBuilder:
    """ Builder class to build the MM Detection config."""
    def __init__(self, config_file_path):
        """ Builder class to build the MM Detection config.
        :param config_file_path: parameters used for inference
        :type config_file_path: str
        """
        self.config: Config = Config.fromfile(config_file_path)

    @staticmethod
    def _find_key_and_set_value(
        config: Dict, search_field: str, value: Any, stack: List
    ) -> None:
        """
        Recursively find the search field and update it with value in given config dictionary
        :param config: mm detection model configuration
        :type config: Dict
        :param search_field: field to update
        :type search_field: str
        :param value: value to update
        :type value: Any
        :param stack: The stack to maintain the path of the search field
        :type stack: List
        """
        for key in config:
            stack.append(key)
            if isinstance(config[key], dict):
                DetectionConfigBuilder._find_key_and_set_value(
                    config[key], search_field, value, stack
                )
            elif isinstance(key, str) and key == search_field:
                config[key] = value
                logger.info(f"Setting {value} at {'.'.join(stack)} in config.")
            stack.pop()

    def set_num_labels(self, num_labels: int) -> DetectionConfigBuilder:
        """
        Set number of labels/ classes in the model config
        :param num_labels: number of labels
        :type num_labels: int
        :return: config builder
        :rtype: DetectionConfigBuilder
        """
        if num_labels > 0:
            self._find_key_and_set_value(
                self.config.model,
                MmDetectionConfigLiterals.NUM_CLASSES,
                num_labels,
                stack=["model"],
            )
        return self

    def set_box_scoring_threshold(
        self, box_score_threshold: float
    ) -> DetectionConfigBuilder:
        """
        Set box scoring threshold in the model config
        :param box_score_threshold: threshold for bounding box score
        :type box_score_threshold: float
        :return: config builder
        :rtype: DetectionConfigBuilder
        """
        try:
            self._find_key_and_set_value(
                self.config.model.test_cfg,
                MmDetectionConfigLiterals.BOX_SCORE_THRESHOLD,
                box_score_threshold,
                stack=["model", "test_cfg"],
            )
        except Exception as ex:
            logger.warning(
                f"Exception {ex} when calling set_box_scoring_threshold. "
            )
            # If test_cfg or score_threshold is not present in config, then this thresholding
            # is handled while calculating the metrics.
        return self

    def build(self) -> Config:
        """ Return the built MM Detection config.
        :return: MM Detection config
        :rtype: MMCV Config
        """
        return self.config


class DetectionModel(AzmlModelInterface):
    """MM Detection models."""
    def from_pretrained(self, model_name_or_path: str, **kwargs) -> nn.Module:
        """ Load the model config and weights if weight path specified.
        :param model_name_or_path: parameters used for inference
        :type model_name_or_path: str
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        :return: MM Detection model
        :rtype: nn.Module
        """
        model_weights_path = kwargs.get(ImageModelSelectorConstants.MMLAB_MODEL_WEIGHTS_PATH_OR_URL, None)
        task_name = kwargs.get(SettingLiterals.TASK_NAME, Tasks.MM_OBJECT_DETECTION)
        num_labels = kwargs.get(SettingLiterals.NUM_LABELS, 0)
        box_score_threshold = kwargs.get(
            SettingLiterals.BOX_SCORE_THRESHOLD,
            InferenceParameters.DEFAULT_BOX_SCORE_THRESHOLD,
        )

        config = (
            DetectionConfigBuilder(model_name_or_path)
            .set_num_labels(num_labels)
            .set_box_scoring_threshold(box_score_threshold)
            .build()
        )

        # copy the label2id mapping from kwargs to config. To be used in mlflow export
        config.id2label = kwargs.get(SettingLiterals.ID2LABEL, None)
        model_meta_file_path = kwargs.get(ImageModelSelectorConstants.MMLAB_MODEL_METAFILE_PATH)
        model = build_detector(config.model)
        logger.info(f"Successfully loaded model config and with {num_labels} labels.")
        if model_weights_path:
            load_checkpoint(model, model_weights_path)
            logger.info(f"Successfully loaded model weight from {model_weights_path}.")

        model_wrapper = None
        if task_name == Tasks.MM_OBJECT_DETECTION:
            model_wrapper = ObjectDetectionModelWrapper(
                model, config, model_name_or_path, model_meta_file_path
            )
        elif task_name == Tasks.MM_INSTANCE_SEGMENTATION:
            model_wrapper = InstanceSegmentationModelWrapper(
                model, config, model_name_or_path, model_meta_file_path
            )
        return model_wrapper
