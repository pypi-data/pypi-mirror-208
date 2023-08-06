# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Finetuning component task-level defaults."""

from dataclasses import dataclass
from azureml.acft.image.components.finetune.defaults.hf_trainer_defaults import (
    HFTrainerDefaults,
)


@dataclass
class ClassificationDefaults(HFTrainerDefaults):
    """
    This class contain trainer defaults specific to classification models.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    _image_width: int = 224
    _image_height: int = 224
    _num_train_epochs: int = 15
    _evaluation_strategy: str = "epoch"
    _save_strategy: str = "epoch"
    _logging_strategy: str = "epoch"
    _lr_scheduler_type: str = "cosine"
    _dataloader_num_workers: int = 6
    _seed: int = 43
    _save_total_limit: int = -1


@dataclass
class ObjectDetectionDefaults(HFTrainerDefaults):
    """
    This class contain trainer defaults specific to object detection models.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    # todo: updated defaults for object detection after benchmarking
    _per_device_train_batch_size: int = 4
    _per_device_eval_batch_size: int = 4
    _learning_rate: float = 5e-4


@dataclass
class InstanceSegmentationDefaults(HFTrainerDefaults):
    """
    This class contain trainer defaults specific to instance segmentation models.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    # todo: updated defaults for instance segmentation after benchmarking
    _per_device_train_batch_size: int = 4
    _per_device_eval_batch_size: int = 4
    _learning_rate: float = 5e-4
