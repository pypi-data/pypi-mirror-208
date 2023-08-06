# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Constants used for image model selector component."""
import os


class ImageModelSelectorConstants:
    """String constants for model selector component."""

    ARTIFACTS_DIR = "artifacts"
    MODEL_FAMILY = "model_family"

    MMLAB_MODEL_WEIGHTS_PATH_OR_URL = "model_weights_path_or_url"
    MMLAB_MODEL_METAFILE_PATH = "model_metafile_path"
    MMLAB_MODEL_METAFILE_NAME = "model_metafile.json"


class MMDetectionModelZooConfigConstants:
    """
    Constants for MMDetection model zoo config.
    """

    MODEL_ZOO_MODELS = "Models"
    MODEL_ZOO_MODEL_NAME = "Name"
    MODEL_ZOO_CONFIG = "Config"
    MODEL_ZOO_WEIGHTS = "Weights"
