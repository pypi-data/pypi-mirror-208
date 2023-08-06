# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Mlflow save utils."""

import mlflow
import os

from typing import Dict, Optional, List, Any

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.common_components import get_logger_app, ModelSelectorDefaults
from azureml.acft.common_components.utils.error_handling.error_definitions import TaskNotSupported
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from mlflow.models.signature import ModelSignature
from mlflow.types.schema import ColSpec, Schema

from common_constants import (
    AugmentationConfigKeys,
    Tasks,
    MLFlowSchemaLiterals,
    MMDetLiterals
)
from mmdet_mlflow_model_wrapper import ImagesMLFlowModelWrapper

logger = get_logger_app(__name__)


def get_mlflow_signature(task_type: str) -> ModelSignature:
    """
    Return mlflow model signature with input and output schema given the input task type.

    :param task_type: Task type used in training.
    :type task_type: str
    :return: mlflow model signature.
    :rtype: mlflow.models.signature.ModelSignature
    """

    input_schema = Schema(
        [
            ColSpec(
                MLFlowSchemaLiterals.INPUT_COLUMN_IMAGE_DATA_TYPE,
                MLFlowSchemaLiterals.INPUT_COLUMN_IMAGE,
            )
        ]
    )

    # For classification
    if task_type in [
        Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION,
        Tasks.HF_MULTI_LABEL_IMAGE_CLASSIFICATION,
    ]:

        output_schema = Schema(
            [
                ColSpec(
                    MLFlowSchemaLiterals.OUTPUT_COLUMN_DATA_TYPE,
                    MLFlowSchemaLiterals.OUTPUT_COLUMN_PROBS,
                ),
                ColSpec(
                    MLFlowSchemaLiterals.OUTPUT_COLUMN_DATA_TYPE,
                    MLFlowSchemaLiterals.OUTPUT_COLUMN_LABELS,
                ),
            ]
        )

    # for object detection and instance segmentation mlflow signature remains same
    elif task_type in [
        Tasks.MM_OBJECT_DETECTION,
        Tasks.MM_INSTANCE_SEGMENTATION
    ]:
        output_schema = Schema(
            [
                ColSpec(
                    MLFlowSchemaLiterals.OUTPUT_COLUMN_DATA_TYPE,
                    MLFlowSchemaLiterals.OUTPUT_COLUMN_BOXES,
                ),
            ]
        )
    else:
        raise ACFTValidationException._with_error(
            AzureMLError.create(TaskNotSupported, TaskName=task_type)
        )

    return ModelSignature(inputs=input_schema, outputs=output_schema)


def _save_mmdet_mlflow_model(
    model_output_dir: str,
    mlflow_output_dir: str,
    options: Dict[str, Any],
    model_name: str,
    task_type: str
) -> None:
    """
    Save the mmdetection model in mlflow format.

    :param model_output_dir: Output directory where the HF trainer model files are stored.
    :type model_output_dir: str
    :param mlflow_output_dir: Output directory where mlflow model will be stored.
    :type mlflow_output_dir: str
    :param options: Dictionary of MLflow settings/wrappers for model saving process.
    :type options: Dict
    :param model_name: Name of the model.
    :type model_name: str
    :param task_type: Task type used in training.
    :type task_type: str
    :return: None
    """

    config_path = os.path.join(model_output_dir, model_name + ".py")
    model_weights_path = os.path.join(model_output_dir, ModelSelectorDefaults.MODEL_CHECKPOINT_FILE_NAME)
    augmentations_path = os.path.join(model_output_dir, AugmentationConfigKeys.OUTPUT_AUG_FILENAME)
    metafile_path = os.path.join(model_output_dir, MMDetLiterals.METAFILE_PATH + ".json")
    artifacts_dict = {
        MMDetLiterals.CONFIG_PATH : config_path,
        MMDetLiterals.WEIGHTS_PATH : model_weights_path,
        MMDetLiterals.AUGMENTATIONS_PATH: augmentations_path,
        MMDetLiterals.METAFILE_PATH: metafile_path,
    }

    files_to_include = ['common_constants.py', 'common_utils.py', 'mmdet_mlflow_model_wrapper.py',
                        'mmdet_modules.py', 'mmdet_utils.py', 'augmentation_helper.py',
                        'custom_augmentations.py']
    if task_type == Tasks.MM_INSTANCE_SEGMENTATION:
        files_to_include.append('masktools.py')
    directory = os.path.dirname(__file__)
    code_path = [os.path.join(directory, x) for x in files_to_include]

    pip_requirements = None
    if task_type == Tasks.MM_OBJECT_DETECTION:
        pip_requirements = os.path.join(os.path.dirname(__file__), "mmdet-od-requirements.txt")
    elif task_type == Tasks.MM_INSTANCE_SEGMENTATION:
        pip_requirements = os.path.join(os.path.dirname(__file__), "mmdet-is-requirements.txt")

    logger.info(f"Saving mlflow pyfunc model to {mlflow_output_dir}.")

    try:
        mlflow.pyfunc.save_model(
            path=mlflow_output_dir,
            python_model=options[MLFlowSchemaLiterals.WRAPPER],
            artifacts=artifacts_dict,
            pip_requirements=pip_requirements,
            signature=options[MLFlowSchemaLiterals.SCHEMA_SIGNATURE],
            code_path=code_path
        )
        logger.info("Saved mlflow model successfully.")
    except Exception as e:
        logger.error(f"Failed to save the mlflow model {str(e)}")
        raise Exception(f"failed to save the mlflow model {str(e)}")


def save_mmdet_mlflow_pyfunc_model(
    task_type: str,
    model_output_dir: str,
    mlflow_output_dir: str,
    model_name: str,
) -> None:
    """
    Save the mlflow model.

    :param task_type: Task type used in training.
    :type task_type: str
    :param model_output_dir: Output directory where the HF trainer model files are stored.
    :type model_output_dir: str
    :param mlflow_output_dir: Output directory where mlflow model will be stored.
    :type mlflow_output_dir: str
    :param model_name: Name of the model.
    :type model_name: str
    """

    logger.info("Saving the model in MLFlow format.")
    mlflow_model_wrapper = ImagesMLFlowModelWrapper(task_type=task_type)

    # Upload files to artifact store
    mlflow_options = {
        MLFlowSchemaLiterals.WRAPPER: mlflow_model_wrapper,
        MLFlowSchemaLiterals.SCHEMA_SIGNATURE: get_mlflow_signature(task_type),
    }
    _save_mmdet_mlflow_model(
        model_output_dir=model_output_dir,
        mlflow_output_dir=mlflow_output_dir,
        options=mlflow_options or {},
        model_name=model_name,
        task_type=task_type
    )
