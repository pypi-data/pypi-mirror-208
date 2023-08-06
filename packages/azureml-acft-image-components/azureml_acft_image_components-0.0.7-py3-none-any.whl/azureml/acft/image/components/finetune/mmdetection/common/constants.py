# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File for adding all the constants required for MMDetection."""


class MmDetectionDatasetLiterals:
    """Constants for MMDetection dataset."""
    IMG = "img"
    IMG_METAS = "img_metas"
    GT_BBOXES = 'gt_bboxes'
    GT_LABELS = 'gt_labels'
    GT_CROWDS = 'gt_crowds'
    GT_MASKS = "gt_masks"
    MASKS = "masks"
    BBOXES = "bboxes"
    LABELS = "labels"
    IMAGE_ORIGINAL_SHAPE = "ori_shape"


class MmDetectionConfigLiterals:
    """Constants for MMDetection config."""
    NUM_CLASSES = "num_classes"
    BOX_SCORE_THRESHOLD = "score_thr"
