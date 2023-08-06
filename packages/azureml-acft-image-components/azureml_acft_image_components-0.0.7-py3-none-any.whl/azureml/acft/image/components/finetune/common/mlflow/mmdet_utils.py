# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Mlflow PythonModel wrapper helper scripts."""

import logging
import numpy as np
import torch

from datasets import load_dataset
from dataclasses import asdict
from transformers import Trainer, TrainingArguments
from typing import Dict, List, Callable

from common_constants import (HFMiscellaneousLiterals,
                              Tasks,
                              MmDetectionDatasetLiterals,
                              ODLiterals)
from mmdet_modules import ImageMetadata

logger = logging.getLogger(__name__)


def _parse_object_detection_output(output: Dict[str, np.ndarray], id2label: Dict[int, str]) -> List[Dict]:
    proc_op = []
    for bboxes, labels in zip(output[MmDetectionDatasetLiterals.BBOXES], output[MmDetectionDatasetLiterals.LABELS]):
        curimage_preds = {ODLiterals.BOXES: []}
        for bbox, label in zip(bboxes, labels):
            if label >= 0:
                curimage_preds[ODLiterals.BOXES].append({
                    ODLiterals.BOX: {
                        ODLiterals.TOP_X: float(bbox[0]),
                        ODLiterals.TOP_Y: float(bbox[1]),
                        ODLiterals.BOTTOM_X: float(bbox[2]),
                        ODLiterals.BOTTOM_Y: float(bbox[3]),
                    },
                    ODLiterals.LABEL: id2label[label],
                    ODLiterals.SCORE: float(bbox[4]),
                })
        proc_op.append(curimage_preds)
    return proc_op


def _parse_instance_segmentation_output(output: Dict[str, np.ndarray], id2label: Dict[int, str]) -> List[Dict]:
    from masktools import convert_mask_to_polygon
    proc_op = []
    for bboxes, labels, masks in zip(output[MmDetectionDatasetLiterals.BBOXES],
                                     output[MmDetectionDatasetLiterals.LABELS],
                                     output[MmDetectionDatasetLiterals.MASKS]):
        curimage_preds = {ODLiterals.BOXES: []}
        for bbox, label, mask in zip(bboxes, labels, masks):
            if label >= 0:
                box = {
                    ODLiterals.BOX: {
                        ODLiterals.TOP_X: float(bbox[0]),
                        ODLiterals.TOP_Y: float(bbox[1]),
                        ODLiterals.BOTTOM_X: float(bbox[2]),
                        ODLiterals.BOTTOM_Y: float(bbox[3]),
                    },
                    ODLiterals.LABEL: id2label[label],
                    ODLiterals.SCORE: float(bbox[4]),
                    ODLiterals.POLYGON: convert_mask_to_polygon(mask)
                }
                if len(box[ODLiterals.POLYGON]) > 0:
                    curimage_preds[ODLiterals.BOXES].append(box)
        proc_op.append(curimage_preds)
    return proc_op


def mmdet_run_inference_batch(
    test_args: TrainingArguments,
    model: torch.nn.Module,
    id2label: Dict[int, str],
    image_path_list: List,
    task_type: Tasks,
    test_transforms: Callable,
) -> List:
    """This method performs inference on batch of input images.

    :param test_args: Training arguments path.
    :type test_args: transformers.TrainingArguments
    :param image_processor: Preprocessing configuration loader.
    :type image_processor: transformers.AutoImageProcessor
    :param model: Pytorch model weights.
    :type model: transformers.AutoModelForImageClassification
    :param image_path_list: list of image paths for inferencing.
    :type image_path_list: List
    :param task_type: Task type of the model.
    :type task_type: constants.Tasks
    :param test_transforms: Transformations to apply to the test dataset before
                            sending it to the model.
    :param test_transforms: Callable
    :return: list of dict.
    :rtype: list
    """

    def collate_fn(examples: List[Dict[str, Dict]]) -> Dict[str, Dict]:
        # Filter out invalid examples
        valid_examples = [example for example in examples if example is not None]
        if len(valid_examples) != len(examples):
            if len(valid_examples) == 0:
                raise Exception("All images in the current batch are invalid.")
            else:
                num_invalid_examples = len(examples) - len(valid_examples)
                logger.info(f"{num_invalid_examples} invalid images found.")
                logger.info("Replacing invalid images with randomly selected valid images from the current batch")
                new_example_indices = np.random.choice(np.arange(len(valid_examples)), num_invalid_examples)
                for ind in new_example_indices:
                    # Padding the batch with valid examples
                    valid_examples.append(valid_examples[ind])

        # Pre processing Image
        if test_transforms is not None:
            for example in valid_examples:
                example[HFMiscellaneousLiterals.DEFAULT_IMAGE_KEY] = test_transforms(
                    image=np.array(example[HFMiscellaneousLiterals.DEFAULT_IMAGE_KEY])
                )[HFMiscellaneousLiterals.DEFAULT_IMAGE_KEY]

        def to_tensor_fn(img):
            return torch.from_numpy(img.transpose(2, 0, 1)).to(dtype=torch.float)

        pixel_values = torch.stack([
            to_tensor_fn(example[HFMiscellaneousLiterals.DEFAULT_IMAGE_KEY])
            for example in valid_examples
        ])

        img_metas = []
        for i, example in enumerate(valid_examples):
            image = example[HFMiscellaneousLiterals.DEFAULT_IMAGE_KEY]
            if test_transforms:
                width, height, no_ch = image.shape
            else:
                width, height = image.size
                no_ch = len(image.getbands())
            img_metas.append(
                asdict(ImageMetadata(ori_shape=(width, height, no_ch), filename=f"test_{i}.jpg"))
            )

        # input to mmdet model should contain image and image meta data
        output = {
            MmDetectionDatasetLiterals.IMG: pixel_values,
            MmDetectionDatasetLiterals.IMG_METAS: img_metas
        }

        return output

    inference_dataset = load_dataset(
        HFMiscellaneousLiterals.IMAGE_FOLDER,
        data_files={HFMiscellaneousLiterals.VAL: image_path_list}
    )
    inference_dataset = inference_dataset[HFMiscellaneousLiterals.VAL]

    # Initialize the trainer
    trainer = Trainer(
        model=model,
        args=test_args,
        data_collator=collate_fn,
    )
    results = trainer.predict(inference_dataset)
    output = results.predictions[1]
    if task_type == Tasks.MM_OBJECT_DETECTION:
        return _parse_object_detection_output(output, id2label)
    elif task_type == Tasks.MM_INSTANCE_SEGMENTATION:
        return _parse_instance_segmentation_output(output, id2label)
