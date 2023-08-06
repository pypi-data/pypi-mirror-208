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

"""Finetune runner for image tasks."""

import os

from argparse import Namespace
from functools import partial

from azureml.acft.accelerator.constants import HfTrainerType
from azureml.acft.accelerator.finetune import AzuremlDatasetArgs, AzuremlFinetuneArgs
from azureml.acft.accelerator.finetune import AzuremlTrainer

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.factory.mappings import MODEL_FAMILY_CLS
from azureml.acft.image.components.finetune.factory.model_factory import ModelFactory
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals,
)
from azureml.evaluate import mlflow

logger = get_logger_app(__name__)


def finetune_runner(component_args: Namespace) -> None:
    """
    finetune runner for all image tasks

    :param component_args: args from the finetune component
    :type component_args: Namespace
    """
    # importing here after common/mlfow is added to the path.
    from azureml.acft.image.components.finetune.defaults.training_defaults import (
        TrainingDefaults,
    )

    logger.info("Starting finetune runner")
    logger.info(f"Task name: {component_args.task_name}")

    model_factory = ModelFactory(
        component_args.model_family,
        component_args.model_name_or_path,
        task_name=component_args.task_name,
    )
    trainer_classes_obj = model_factory.get_trainer_classes()

    # set the trainer classes
    finetune_cls = trainer_classes_obj.finetune_cls
    image_processor = trainer_classes_obj.tokenizer_cls
    data_cls = trainer_classes_obj.dataset_cls
    model_cls = trainer_classes_obj.model_cls
    calculate_metrics = trainer_classes_obj.metrics_function
    trainer_callbacks = trainer_classes_obj.callbacks

    # call the interface
    finetune_obj = finetune_cls(vars(component_args))

    # get the component args dict
    custom_finetune_args = finetune_obj.get_finetune_args()
    component_args_dict = vars(component_args)
    component_args_dict.update(custom_finetune_args)

    # get the training defaults if auto hyperparameter selection is set
    if component_args_dict.get(SettingLiterals.AUTO_HYPERPARAMETER_SELECTION, False):
        training_defaults = TrainingDefaults(
            task=component_args.task_name,
            model_name_or_path=component_args.model_name_or_path,
        )
        component_args_dict.update(training_defaults.defaults_dict)

    # log the component args dict
    logger.info(f"Component args dict used for training: {component_args_dict}")

    # get the custom trainer functions
    custom_trainer_functions = finetune_obj.get_custom_trainer_functions()

    # init the tokenizer
    tokenizer = (
        image_processor.from_pretrained(
            component_args.model_name_or_path, **component_args_dict
        )
        if image_processor
        else None
    )
    data_cls = data_cls(tokenizer=tokenizer, **component_args_dict)
    # set the dataset args
    dataset_args = AzuremlDatasetArgs(
        train_dataset=data_cls.get_train_dataset(),
        validation_dataset=data_cls.get_validation_dataset(),
        data_collator=data_cls.get_collation_function(),
    )

    # init model
    model = model_cls.from_pretrained(
        component_args.model_name_or_path,
        label2id=data_cls.label2id,
        id2label=data_cls.id2label,
        num_labels=len(data_cls.label2id),
        **component_args_dict,
    )

    if isinstance(model, tuple):
        model, mismatch_info = model
        logger.info(f"Mismatch info: {mismatch_info}")

    component_args_dict[SettingLiterals.NUM_LABELS] = len(data_cls.label2id)

    azml_finetune_args = AzuremlFinetuneArgs(
        finetune_args=component_args_dict, trainer_type=HfTrainerType.DEFAULT
    )

    # Define metric func, send the arguments to the metric function
    compute_metric_func = (
        partial(calculate_metrics, **component_args_dict) if calculate_metrics else None
    )

    # init trainer
    azml_trainer = AzuremlTrainer(
        finetune_args=azml_finetune_args,
        dataset_args=dataset_args,
        model=model,
        tokenizer=tokenizer,
        metric_func=compute_metric_func,
        custom_trainer_callbacks=trainer_callbacks,
        custom_trainer_functions=custom_trainer_functions,
        new_initalized_layers=None,
    )
    azml_trainer.train()

    # saving the mlflow model
    if component_args.save_as_mlflow_model:
        logger.info("saving the mlflow model")
        if component_args.model_family == MODEL_FAMILY_CLS.HUGGING_FACE_IMAGE:

            # In new version azureml_evaluate_mlflow 0.1.0.86769376 package infer the tokenizer class.
            # Now, we don't need to pass "hf_tokenizer_class": AutoImageProcessor.__name__,

            # In train_label_list, use id2label to get label list. Avoid using label2id as label2id can be
            # inconsistent if there are two labels with same name (very rare condition). It's observed in google vit
            # model's default config.

            hf_conf = {
                "task_type": component_args.task_name,
                "train_label_list": sorted(list(model.config.id2label.values())),
                "hf_predict_module": "hf_test_predict",
            }
            mlflow_dir = os.path.join(os.path.dirname(__file__), "common", "mlflow")
            files_to_include = ['common_constants.py', 'common_utils.py', 'hf_test_predict.py']
            code_paths = [os.path.join(mlflow_dir, x) for x in files_to_include]
            from mlflow_save_utils import get_mlflow_signature
            mlflow.hftransformers.save_model(
                model,
                component_args.mlflow_model_folder,
                tokenizer=tokenizer,
                config=model.config,
                hf_conf=hf_conf,
                code_paths=code_paths,
                signature=get_mlflow_signature(component_args.task_name)
            )
        elif component_args.model_family == MODEL_FAMILY_CLS.MMDETECTION_IMAGE:
            # importing directly from acft package is resulting in our package dependencies.
            from mlflow_save_utils import save_mmdet_mlflow_pyfunc_model
            save_mmdet_mlflow_pyfunc_model(
                model_output_dir=component_args.pytorch_model_folder,
                mlflow_output_dir=component_args.mlflow_model_folder,
                model_name=os.path.basename(component_args.model_name).split('.')[0],
                task_type=component_args.task_name,
            )
        else:
            raise NotImplementedError(f"Saving mlflow model is not implemented for this model family\
                : {component_args.model_family}")
