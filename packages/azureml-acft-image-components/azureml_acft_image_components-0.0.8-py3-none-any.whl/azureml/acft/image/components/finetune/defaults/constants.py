# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Finetuning component default contants."""


from dataclasses import dataclass
from azureml.acft.image.components.finetune.defaults.task_defaults import (
    ClassificationDefaults,
    InstanceSegmentationDefaults,
    ObjectDetectionDefaults,
)
from azureml.acft.image.components.finetune.defaults.classification_models_defaults import (
    BEITDefaults,
    DEITDefaults,
    MobileVITDefaults,
    SWINV2Defaults,
    VITDefaults,
)
from azureml.acft.image.components.finetune.defaults.object_detection_models_defaults import (
    YOLODefaults,
)
from azureml.acft.image.components.finetune.defaults.instance_segmentation_models_defaults import (
    RCNNDefaults,
)
from azureml.acft.image.components.finetune.huggingface.common.constants import (
    HfProblemType,
)


@dataclass
class TrainingDefaultsConstants:
    """
    This class contains constants for the TrainingDefaults class.
    Note: Provide mapping of model name to dataclass and task to dataclass.
    """

    MODEL_NAME_TO_DATACLASS_MAPPING = {
        "yolov5": YOLODefaults,
        "google/vit-base-patch16-224": VITDefaults,
        "bitmodel": BEITDefaults,
        "maskrcnn": RCNNDefaults,
        "microsoft/beit-base-patch16-224-pt22k-ft22k": BEITDefaults,
        "microsoft/swinv2-base-patch4-window12-192-22k": SWINV2Defaults,
        "facebook/deit-base-patch16-224": DEITDefaults,
        "apple/mobilevit-small": MobileVITDefaults,
    }

    TASK_TO_DATACLASS_MAPPING = {
        HfProblemType.MULTI_LABEL_CLASSIFICATION: ClassificationDefaults,
        HfProblemType.SINGLE_LABEL_CLASSIFICATION: ClassificationDefaults,
        HfProblemType.INSTANCE_SEGMENTATION: InstanceSegmentationDefaults,
        HfProblemType.OBJECT_DETECTION: ObjectDetectionDefaults,
    }

    MODEL_DEFAULTS_FILE = "model_defaults.json"
    MODEL_METADATA_FILE = "model_metadata.json"
    MODEL_NAME_KEY = "model_name"


@dataclass
class HFTrainerDefaultsKeys:
    """
    This class contains the keys for the Hugging Face trainer defaults.
    Note: Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    NUM_TRAIN_EPOCHS = "num_train_epochs"
    PER_DEVICE_TRAIN_BATCH_SIZE = "per_device_train_batch_size"
    PER_DEVICE_EVAL_BATCH_SIZE = "per_device_eval_batch_size"
    LEARNING_RATE = "learning_rate"
    OPTIM = "optim"
    GRADIENT_ACCUMULATION_STEPS = "gradient_accumulation_steps"
    MAX_STEPS = "max_steps"
    AUTO_FIND_BATCH_SIZE = "auto_find_batch_size"
    EVALUATION_STRATEGY = "evaluation_strategy"
    EVAL_STEPS = "eval_steps"
    SAVE_STRATEGY = "save_strategy"
    SAVE_STEPS = "save_steps"
    LOGGING_STRATEGY = "logging_strategy"
    LOGGING_STEPS = "logging_steps"
    WARMUP_STEPS = "warmup_steps"
    WEIGHT_DECAY = "weight_decay"
    ADAM_BETA1 = "adam_beta1"
    ADAM_BETA2 = "adam_beta2"
    ADAM_EPSILON = "adam_epsilon"
    LR_SCHEDULING_TYPE = "lr_scheduler_type"
    DATALOADER_NUM_WORKERS = "dataloader_num_workers"
    SEED = "seed"
    SAVE_TOTAL_LIMIT = "save_total_limit"


@dataclass
class NonHfTrainerDefaultsKeys:
    """
    This class contains the keys for the non Hugging Face trainer defaults.

    """

    IMAGE_WIDTH = "image_width"
    IMAGE_HEIGHT = "image_height"
