# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Custom albumentation augmentations."""

import albumentations
import torch
import random
import numpy as np
from typing import List, Optional, Tuple, Union
from albumentations.pytorch import transforms
from albumentations import DualTransform

BoxInternalType = Tuple[float, float, float, float]


class RandomExpand(DualTransform):
    """ Expand the image, bbox and mask by a random ratio and fill the surrounding space with the mean of ImageNet.
        This is intended to detect smaller objects.
    """
    def apply(self, img: np.ndarray, **params) -> np.ndarray:
        """ Overrides the DualTransform.apply method. This would apply the
        transformation to the input image.
        :param image: image
        :type image: np.ndarray
        :return: transformed image
        :rtype: np.ndarray
        """

        return self._expand_image(img)

    def apply_to_bbox(self, bbox: BoxInternalType, **params) -> BoxInternalType:
        """ Overrides the DualTransform.apply_to_bbox method. This would apply
        the transformations to each bounding box separately.
        :param image: bbox
        :type image: Tuple[float, float, float, float]
        :return: transformed bounding box
        :rtype: Tuple[float, float, float, float]
        """

        return self._expand_bbox(bbox)

    def apply_to_masks(self, masks: List[np.ndarray], **params) -> List[np.ndarray]:
        """ Overrides the DualTransform.apply_to_masks method. This would apply
        the transformations to the masks.
        :param masks: list of masks
        :type image: List[np.ndarray]
        :return: transformed masks
        :rtype: List[np.ndarray]
        """

        return self._expand_masks(masks)

    def get_transform_init_args_names(self) -> Tuple:
        """ Returns a tuple of arguments which are expected in the init method of the
        transformations.
        """

        return ()

    def _expand_image(self, image: np.ndarray) -> np.ndarray:
        """
        :param image: image
        :type image: np.ndarray
        :return: expanded image
        :rtype: np.ndarray
        """

        # Todo: Replace imagenet mean read from model's config file
        imagenet_mean = [0.485, 0.456, 0.406]

        tensor_image = transforms.img_to_tensor(image)
        depth, self.height, self.width = tensor_image.size()

        ratio = random.uniform(1, 2)
        self.new_height = int(self.height * ratio)
        self.new_width = int(self.width * ratio)
        self.top = random.randint(0, self.new_height - self.height)
        self.left = random.randint(0, self.new_width - self.width)

        # place an image in a larger mean image
        new_image = torch.ones((3, self.new_height, self.new_width), dtype=torch.float)
        new_image[:, :, :] *= torch.FloatTensor(imagenet_mean).unsqueeze(1).unsqueeze(2)
        new_image[:, self.top: self.top + self.height, self.left:self.left + self.width] = tensor_image
        # convert image(C, H, W) to (H, W, C)
        return new_image.numpy().transpose(1, 2, 0)

    def _expand_bbox(self, bbox: BoxInternalType) -> BoxInternalType:
        """
        expand the bounding box to the same dimension as the image
        :param box: bounding box in (x_min, y_min, x_max, y_max)
        :type boxe: Tuple[torch.Tensor]
        :return: expanded bounding box
        :rtype: Tuple[torch.Tensor]
        """

        # Albumentation normalizes the input bboxes to keep the scale in range[0,1].
        denormalized_bbox = (
            bbox[0] * self.width, bbox[1] * self.height,
            bbox[2] * self.width, bbox[3] * self.height
        )
        new_bbox = torch.Tensor(denormalized_bbox)
        new_bbox += torch.FloatTensor([self.left, self.top, self.left, self.top])
        new_bbox = tuple(new_bbox)
        normalized_box = (
            new_bbox[0] / self.new_width, new_bbox[1] / self.new_height,
            new_bbox[2] / self.new_width, new_bbox[3] / self.new_height
        )
        return normalized_box

    def _expand_masks(self, masks: Optional[List[np.ndarray]]) -> Optional[List[np.ndarray]]:
        """
        :param masks: NxHxW pixel array masks for the object
        :type masks: List[np.ndarray]
        :return: expanded mask if present
        :rtype: Optional[List[np.ndarray]]
        """

        # if there are masks, align them with the image
        new_masks = None
        if masks is not None:
            new_masks = np.zeros((len(masks), self.new_height, self.new_width), dtype=np.float32)
            new_masks[:, self.top:self.top + self.height, self.left:self.left + self.width] = masks
        return new_masks


class ConstraintResize(DualTransform):
    """
    Given the scale<min_size, max_size>, the image will be rescaled as large as possible within the scale.
    The image size will be constraint so that the max edge is no longer than max_size and
    short edge is no longer than min_size.
    """
    def __init__(self, img_scale: Union[List[int], List[Tuple]],
                 keep_ratio: bool = True, always_apply: bool = False, p: float = 0.5):
        """
        :param img_scale: Image scale for resizing. [min_size, max_size] or multiple (min_size, max_size) to randomly
        select from.
        :type img_scale: (List[int] or list[tuple(int, int)]).
        :param keep_ratio: Whether to keep the aspect ratio.
        :type keep_ratio: Boolean
        :param always_apply: Whether to apply the transformation always irrespective of the parameter 'p'.
        :type always_apply: Boolean
        :param p: Probability to apply the transform.
        :type p: float
        """
        super(ConstraintResize, self).__init__(always_apply, p)
        self.img_scale = img_scale
        self.min_size = min(img_scale)
        self.max_size = max(img_scale)
        self.keep_ratio = keep_ratio
        self.new_h = None
        self.new_w = None

    def _random_select(self):
        """Randomly select an img_scale from given candidates.
        Args:
            img_scales (list[tuple]): Images scales for selection.
        Returns:
            (tuple, int): Returns a tuple ``(img_scale, scale_dix)``, \
                where ``img_scale`` is the selected image scale and \
                ``scale_idx`` is the selected index in the given candidates.
        """

        scale_idx = np.random.randint(len(self.img_scale))
        selected_img_scale = self.img_scale[scale_idx]
        return selected_img_scale, scale_idx

    def _set_new_size(self, img: np.ndarray, keep_ratio=True) -> None:
        """
        Calcuate the final size of the output image
        :param img: Input image
        :type img: np.ndarray
        :param keep_ratio: Whether to keep the aspect ratio.
        :type keep_ratio: Boolean
        """

        self.h, self.w = img.shape[:2]
        if type(self.img_scale[0]) == list or type(self.img_scale[0]) == tuple:
            randomly_selected_scale, _ = self._random_select()
            self.min_size = min(randomly_selected_scale)
            self.max_size = max(randomly_selected_scale)

        if keep_ratio:
            img_min_size = min(img.shape[:2])
            img_max_size = max(img.shape[:2])
            # Todo: Add support for min_size and max_size as a list also
            scale_factor = min(self.min_size / img_min_size, self.max_size / img_max_size)
            self.new_h = int(self.h * scale_factor)
            self.new_w = int(self.w * scale_factor)
        else:
            self.new_h = self.max_size if self.h > self.w else self.min_size
            self.new_w = self.min_size if self.h > self.w else self.max_size
        self.w_scale = self.new_w / self.w
        self.h_scale = self.new_h / self.h

    def apply(self, img: np.ndarray, **params) -> np.ndarray:
        """ Overrides the DualTransform.apply method. This would apply the
        transformation to the input image.
        :param image: image
        :type image: np.ndarray
        :return: transformed image
        :rtype: np.ndarray
        """

        # Todo: This resizes all the images to a fixed size which is the size
        # of the first image. Remove this and add resizing of all the images
        # in current batch to the same size in collate method. This should
        # resize the bboxes, masks as well.

        if not self.new_h or not self.new_w:
            self._set_new_size(img, self.keep_ratio)
        new_image = albumentations.resize(img, self.new_h, self.new_w)
        return new_image

    def apply_to_bbox(self, bbox: BoxInternalType, **params) -> BoxInternalType:
        """ Overrides the DualTransform.apply_to_bbox method. This would apply
        the transformations to each bounding box separately.
        :param image: bbox
        :type image: Tuple[float, float, float, float]
        :return: transformed bounding box
        :rtype: Tuple[float, float, float, float]
        """

        denormalized_bbox = (
            bbox[0] * self.w, bbox[1] * self.h,
            bbox[2] * self.w, bbox[3] * self.h
        )
        new_bbox = torch.Tensor(denormalized_bbox)
        new_bbox *= torch.FloatTensor([self.w_scale, self.h_scale, self.w_scale, self.h_scale])
        new_bbox = tuple(new_bbox)
        normalized_box = (
            new_bbox[0] / self.new_w, new_bbox[1] / self.new_h,
            new_bbox[2] / self.new_w, new_bbox[3] / self.new_h
        )
        return normalized_box

    def apply_to_masks(self, masks: List[np.ndarray], **params) -> List[np.ndarray]:
        """ Overrides the DualTransform.apply_to_masks method. This would apply
        the transformations to the masks.
        :param masks: list of masks
        :type image: List[np.ndarray]
        :return: transformed masks
        :rtype: List[np.ndarray]
        """

        if masks is None:
            return masks
        rescaled_masks = []
        for mask in masks:
            rescaled_masks.append(albumentations.resize(mask, self.new_h, self.new_w))
        return rescaled_masks

    def get_transform_init_args_names(self) -> Tuple:
        """ Returns a tuple of arguments which are expected in the init method of the
        transformations.
        """

        return (
            "img_scale",
            "keep_ratio"
        )


# Todo: Move this file to inference folder for model export
albumentations.RandomExpand = RandomExpand
albumentations.ConstraintResize = ConstraintResize
