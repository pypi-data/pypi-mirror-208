# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Mlflow PythonModel wrapper class that loads the Mlflow model, preprocess inputs and performs inference."""

import logging
import subprocess
import sys
import tempfile

import mlflow
import pandas as pd
import torch
from transformers import TrainingArguments

from augmentation_helper import (
    load_augmentation_dict_from_config,
    get_transform
)
from common_constants import (AugmentationConfigKeys,
                              HFMiscellaneousLiterals, Tasks,
                              MMDetLiterals,
                              MLFlowSchemaLiterals)
from common_utils import process_image, create_temp_file

logger = logging.getLogger(__name__)


def get_device() -> str:
    """Returns the currently existing device type.
    Returns:
        str: cuda | cpu.
    """
    return "cuda" if torch.cuda.is_available() else "cpu"


class ImagesMLFlowModelWrapper(mlflow.pyfunc.PythonModel):
    """MLFlow model wrapper for AutoML for Images models."""

    def __init__(
        self,
        task_type: str,
    ) -> None:
        """This method is called when the python model wrapper is initialized.

        :param task_type: Task type used in training.
        :type task_type: str
        """
        super().__init__()
        self.test_args = None
        self.test_transforms = None
        self.mmdet_run_inference_batch = None
        self._config = None
        self._model = None
        self._task_type = task_type

    def load_context(self, context: mlflow.pyfunc.PythonModelContext) -> None:
        """This method is called when loading a Mlflow model with pyfunc.load_model().

        :param context: Mlflow context containing artifacts that the model can use for inference.
        :type context: mlflow.pyfunc.PythonModelContext
        """
        logger.info("Inside load_context()")

        if self._task_type in [Tasks.MM_OBJECT_DETECTION, Tasks.MM_INSTANCE_SEGMENTATION]:
            # Install mmcv and mmdet using mim, with pip installation is not working
            subprocess.check_call([sys.executable, "-m", "mim", "install", "mmcv-full==1.7.1"])
            subprocess.check_call([sys.executable, "-m", "mim", "install", "mmdet==2.28.2"])

            # importing mmdet/mmcv after installing using mim
            from mmdet.models import build_detector
            from mmcv import Config
            from mmcv.runner import load_checkpoint
            from mmdet_modules import ObjectDetectionModelWrapper, InstanceSegmentationModelWrapper
            from mmdet_utils import mmdet_run_inference_batch
            self.mmdet_run_inference_batch = mmdet_run_inference_batch

            try:
                model_config_path = context.artifacts[MMDetLiterals.CONFIG_PATH]
                model_weights_path = context.artifacts[MMDetLiterals.WEIGHTS_PATH]
                self._config = Config.fromfile(model_config_path)
                self._model = build_detector(self._config.model)
                if self._task_type == Tasks.MM_INSTANCE_SEGMENTATION:
                    self._model = InstanceSegmentationModelWrapper(self._model, self._config, model_weights_path)
                elif self._task_type == Tasks.MM_OBJECT_DETECTION:
                    self._model = ObjectDetectionModelWrapper(self._model, self._config, model_weights_path)
                load_checkpoint(self._model, model_weights_path, map_location=get_device())
                logger.info("Model loaded successfully")
            except Exception:
                logger.warning("Failed to load the the model.")
                raise

            aug_config_path = context.artifacts[MMDetLiterals.AUGMENTATIONS_PATH]
            aug_config_dict = load_augmentation_dict_from_config(aug_config_path)
            self.test_transforms = get_transform(AugmentationConfigKeys.VALIDATION_PHASE_KEY,
                                                 aug_config_dict,
                                                 # Bbox is not required at test time
                                                 is_bbox_required=False)
            # arguments for Trainer
            self.test_args = TrainingArguments(
                output_dir=".",
                do_train=False,
                do_predict=True,
                per_device_eval_batch_size=1,
                dataloader_drop_last=False,
                remove_unused_columns=False
            )
        else:
            raise ValueError(f"invalid task type {self._task_type}."
                             f"Supported tasks: {Tasks.MM_OBJECT_DETECTION, Tasks.MM_INSTANCE_SEGMENTATION}")

    def predict(
        self, context: mlflow.pyfunc.PythonModelContext, input_data: pd.DataFrame
    ) -> pd.DataFrame:
        """This method performs inference on the input data.

        :param context: Mlflow context containing artifacts that the model can use for inference.
        :type context: mlflow.pyfunc.PythonModelContext
        :param input_data: Input images for prediction.
        :type input_data: Pandas DataFrame with a first column name ["image"] of images where each
        image is in base64 String format.
        :return: Output of inferencing
        :rtype: Pandas DataFrame with columns ["probs", "labels"] for classification and
        ["boxes"] for object detection, instance segmentation
        """
        task = self._task_type

        # process the images in image column
        processed_images = input_data.loc[:, [MLFlowSchemaLiterals.INPUT_COLUMN_IMAGE]]\
            .apply(axis=1, func=process_image)

        # To Do: change image height and width based on kwargs.

        with tempfile.TemporaryDirectory() as tmp_output_dir:
            image_path_list = (
                processed_images.iloc[:, 0]
                .map(lambda row: create_temp_file(row, tmp_output_dir))
                .tolist()
            )

            result = self.mmdet_run_inference_batch(
                self.test_args,
                model=self._model,
                id2label=self._config[HFMiscellaneousLiterals.ID2LABEL],
                image_path_list=image_path_list,
                task_type=task,
                test_transforms=self.test_transforms,
            )

        return pd.DataFrame(result)
