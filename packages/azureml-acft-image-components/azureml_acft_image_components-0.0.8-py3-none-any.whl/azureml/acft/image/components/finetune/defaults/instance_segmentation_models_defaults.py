# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Finetuning component instance segmentation model family defaults."""

from dataclasses import dataclass
from azureml.acft.image.components.finetune.defaults.task_defaults import (
    InstanceSegmentationDefaults,
)


@dataclass
class RCNNDefaults(InstanceSegmentationDefaults):

    """
    This class contain trainer defaults specific to RCNN models.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    _per_device_train_batch_size: int = 4
    _per_device_eval_batch_size: int = 4
    _learning_rate: float = 5e-4
