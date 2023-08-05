# coding=utf-8
# Copyright 2023 The HuggingFace Inc. team. All rights reserved.
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
"""Image processor class for SAM."""
import math
from copy import deepcopy
from itertools import product
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import convert_to_rgb, normalize, pad, rescale, resize, to_channel_dimension_format
from ...image_utils import (
    IMAGENET_DEFAULT_MEAN,
    IMAGENET_DEFAULT_STD,
    ChannelDimension,
    ImageInput,
    PILImageResampling,
    get_image_size,
    infer_channel_dimension_format,
    make_list_of_images,
    to_numpy_array,
    valid_images,
)
from ...utils import TensorType, is_torch_available, is_torchvision_available, logging, requires_backends


if is_torch_available():
    import torch
    import torch.nn.functional as F

if is_torchvision_available():
    from torchvision.ops.boxes import batched_nms

logger = logging.get_logger(__name__)


class SamImageProcessor(BaseImageProcessor):
    r"""
    Constructs a SAM image processor.

    Args:
        do_resize (`bool`, *optional*, defaults to `True`):
            Whether to resize the image's (height, width) dimensions to the specified `size`. Can be overridden by the
            `do_resize` parameter in the `preprocess` method.
        size (`dict`, *optional*, defaults to `{"longest_edge": 1024}`):
            Size of the output image after resizing. Resizes the longest edge of the image to match
            `size["longest_edge"]` while maintaining the aspect ratio. Can be overridden by the `size` parameter in the
            `preprocess` method.
        resample (`PILImageResampling`, *optional*, defaults to `PILImageResampling.BICUBIC`):
            Resampling filter to use if resizing the image. Can be overridden by the `resample` parameter in the
            `preprocess` method.
        do_rescale (`bool`, *optional*, defaults to `True`):
            Wwhether to rescale the image by the specified scale `rescale_factor`. Can be overridden by the
            `do_rescale` parameter in the `preprocess` method.
        rescale_factor (`int` or `float`, *optional*, defaults to `1/255`):
            Scale factor to use if rescaling the image. Only has an effect if `do_rescale` is set to `True`. Can be
            overridden by the `rescale_factor` parameter in the `preprocess` method.
        do_normalize (`bool`, *optional*, defaults to `True`):
            Whether to normalize the image. Can be overridden by the `do_normalize` parameter in the `preprocess`
            method. Can be overridden by the `do_normalize` parameter in the `preprocess` method.
        image_mean (`float` or `List[float]`, *optional*, defaults to `IMAGENET_DEFAULT_MEAN`):
            Mean to use if normalizing the image. This is a float or list of floats the length of the number of
            channels in the image. Can be overridden by the `image_mean` parameter in the `preprocess` method. Can be
            overridden by the `image_mean` parameter in the `preprocess` method.
        image_std (`float` or `List[float]`, *optional*, defaults to `IMAGENET_DEFAULT_STD`):
            Standard deviation to use if normalizing the image. This is a float or list of floats the length of the
            number of channels in the image. Can be overridden by the `image_std` parameter in the `preprocess` method.
            Can be overridden by the `image_std` parameter in the `preprocess` method.
        do_pad (`bool`, *optional*, defaults to `True`):
            Whether to pad the image to the specified `pad_size`. Can be overridden by the `do_pad` parameter in the
            `preprocess` method.
        pad_size (`dict`, *optional*, defaults to `{"height": 1024, "width": 1024}`):
            Size of the output image after padding. Can be overridden by the `pad_size` parameter in the `preprocess`
            method.
        do_convert_rgb (`bool`, *optional*, defaults to `True`):
            Whether to convert the image to RGB.
    """

    model_input_names = ["pixel_values"]

    def __init__(
        self,
        do_resize: bool = True,
        size: Dict[str, int] = None,
        resample: PILImageResampling = PILImageResampling.BILINEAR,
        do_rescale: bool = True,
        rescale_factor: Union[int, float] = 1 / 255,
        do_normalize: bool = True,
        image_mean: Optional[Union[float, List[float]]] = None,
        image_std: Optional[Union[float, List[float]]] = None,
        do_pad: bool = True,
        pad_size: int = None,
        do_convert_rgb: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"longest_edge": 1024}
        size = get_size_dict(max_size=size, default_to_square=False) if not isinstance(size, dict) else size

        pad_size = pad_size if pad_size is not None else {"height": 1024, "width": 1024}
        pad_size = get_size_dict(pad_size, default_to_square=True)

        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_DEFAULT_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_DEFAULT_STD
        self.do_pad = do_pad
        self.pad_size = pad_size
        self.do_convert_rgb = do_convert_rgb

    def pad_image(
        self,
        image: np.ndarray,
        pad_size: Dict[str, int],
        data_format: Optional[Union[str, ChannelDimension]] = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Pad an image to `(pad_size["height"], pad_size["width"])` with zeros to the right and bottom.

        Args:
            image (`np.ndarray`):
                Image to pad.
            pad_size (`Dict[str, int]`):
                Size of the output image after padding.
            data_format (`str` or `ChannelDimension`, *optional*):
                The data format of the image. Can be either "channels_first" or "channels_last". If `None`, the
                `data_format` of the `image` will be used.
        """
        output_height, output_width = pad_size["height"], pad_size["width"]
        input_height, input_width = get_image_size(image)

        pad_width = output_width - input_width
        pad_height = output_height - input_height

        padded_image = pad(image, ((0, pad_height), (0, pad_width)), data_format=data_format, **kwargs)
        return padded_image

    def _get_preprocess_shape(self, old_shape: Tuple[int, int], longest_edge: int):
        """
        Compute the output size given input size and target long side length.
        """
        oldh, oldw = old_shape
        scale = longest_edge * 1.0 / max(oldh, oldw)
        newh, neww = oldh * scale, oldw * scale
        newh = int(newh + 0.5)
        neww = int(neww + 0.5)
        return (newh, neww)

    def resize(
        self,
        image: np.ndarray,
        size: Dict[str, int],
        resample: PILImageResampling = PILImageResampling.BICUBIC,
        data_format: Optional[Union[str, ChannelDimension]] = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Resize an image to `(size["height"], size["width"])`.

        Args:
            image (`np.ndarray`):
                Image to resize.
            size (`Dict[str, int]`):
                Dictionary in the format `{"longest_edge": int}` specifying the size of the output image. The longest
                edge of the image will be resized to the specified size, while the other edge will be resized to
                maintain the aspect ratio.
            resample:
                `PILImageResampling` filter to use when resizing the image e.g. `PILImageResampling.BILINEAR`.
            data_format (`ChannelDimension` or `str`, *optional*):
                The channel dimension format for the output image. If unset, the channel dimension format of the input
                image is used. Can be one of:
                - `"channels_first"` or `ChannelDimension.FIRST`: image in (num_channels, height, width) format.
                - `"channels_last"` or `ChannelDimension.LAST`: image in (height, width, num_channels) format.
        Returns:
            `np.ndarray`: The resized image.
        """
        size = get_size_dict(size)
        if "longest_edge" not in size:
            raise ValueError(f"The `size` dictionary must contain the key `longest_edge`. Got {size.keys()}")
        input_size = get_image_size(image)
        output_height, output_width = self._get_preprocess_shape(input_size, size["longest_edge"])
        return resize(image, size=(output_height, output_width), resample=resample, data_format=data_format, **kwargs)

    def rescale(
        self,
        image: np.ndarray,
        scale: Union[int, float],
        data_format: Optional[Union[str, ChannelDimension]] = None,
        **kwargs,
    ):
        """
        Rescale an image by a scale factor. image = image * scale.

        Args:
            image (`np.ndarray`):
                Image to rescale.
            scale (`int` or `float`):
                Scale to apply to the image.
            data_format (`str` or `ChannelDimension`, *optional*):
                The channel dimension format of the image. If not provided, it will be the same as the input image.
        """
        return rescale(image, scale=scale, data_format=data_format, **kwargs)

    def normalize(
        self,
        image: np.ndarray,
        mean: Union[float, List[float]],
        std: Union[float, List[float]],
        data_format: Optional[Union[str, ChannelDimension]] = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Normalize an image. image = (image - image_mean) / image_std.

        Args:
            image (`np.ndarray`):
                Image to normalize.
            mean (`float` or `List[float]`):
                Image mean.
            std (`float` or `List[float]`):
                Image standard deviation.
            data_format (`str` or `ChannelDimension`, *optional*):
                The channel dimension format of the image. If not provided, it will be the same as the input image.
        """
        return normalize(image, mean=mean, std=std, data_format=data_format, **kwargs)

    def preprocess(
        self,
        images: ImageInput,
        do_resize: Optional[bool] = None,
        size: Optional[Dict[str, int]] = None,
        resample: Optional["PILImageResampling"] = None,
        do_rescale: Optional[bool] = None,
        rescale_factor: Optional[Union[int, float]] = None,
        do_normalize: Optional[bool] = None,
        image_mean: Optional[Union[float, List[float]]] = None,
        image_std: Optional[Union[float, List[float]]] = None,
        do_pad: Optional[bool] = None,
        pad_size: Optional[Dict[str, int]] = None,
        do_convert_rgb: bool = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        data_format: ChannelDimension = ChannelDimension.FIRST,
        **kwargs,
    ):
        """
        Preprocess an image or batch of images.

        Args:
            images (`ImageInput`):
                Image to preprocess.
            do_resize (`bool`, *optional*, defaults to `self.do_resize`):
                Whether to resize the image.
            size (`Dict[str, int]`, *optional*, defaults to `self.size`):
                Controls the size of the image after `resize`. The longest edge of the image is resized to
                `size["longest_edge"]` whilst preserving the aspect ratio.
            resample (`PILImageResampling`, *optional*, defaults to `self.resample`):
                `PILImageResampling` filter to use when resizing the image e.g. `PILImageResampling.BILINEAR`.
            do_rescale (`bool`, *optional*, defaults to `self.do_rescale`):
                Whether to rescale the image pixel values by rescaling factor.
            rescale_factor (`int` or `float`, *optional*, defaults to `self.rescale_factor`):
                Rescale factor to apply to the image pixel values.
            do_normalize (`bool`, *optional*, defaults to `self.do_normalize`):
                Whether to normalize the image.
            image_mean (`float` or `List[float]`, *optional*, defaults to `self.image_mean`):
                Image mean to normalize the image by if `do_normalize` is set to `True`.
            image_std (`float` or `List[float]`, *optional*, defaults to `self.image_std`):
                Image standard deviation to normalize the image by if `do_normalize` is set to `True`.
            do_pad (`bool`, *optional*, defaults to `self.do_pad`):
                Whether to pad the image.
            pad_size (`Dict[str, int]`, *optional*, defaults to `self.pad_size`):
                Controls the size of the padding applied to the image. The image is padded to `pad_size["height"]` and
                `pad_size["width"]` if `do_pad` is set to `True`.
            do_convert_rgb (`bool`, *optional*, defaults to `self.do_convert_rgb`):
                Whether to convert the image to RGB.
            return_tensors (`str` or `TensorType`, *optional*):
                The type of tensors to return. Can be one of:
                    - Unset: Return a list of `np.ndarray`.
                    - `TensorType.TENSORFLOW` or `'tf'`: Return a batch of type `tf.Tensor`.
                    - `TensorType.PYTORCH` or `'pt'`: Return a batch of type `torch.Tensor`.
                    - `TensorType.NUMPY` or `'np'`: Return a batch of type `np.ndarray`.
                    - `TensorType.JAX` or `'jax'`: Return a batch of type `jax.numpy.ndarray`.
            data_format (`ChannelDimension` or `str`, *optional*, defaults to `ChannelDimension.FIRST`):
                The channel dimension format for the output image. Can be one of:
                - `"channels_first"` or `ChannelDimension.FIRST`: image in (num_channels, height, width) format.
                - `"channels_last"` or `ChannelDimension.LAST`: image in (height, width, num_channels) format.
                - Unset: Use the channel dimension format of the input image.
        """
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        size = get_size_dict(max_size=size, default_to_square=False) if not isinstance(size, dict) else size
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        do_pad = do_pad if do_pad is not None else self.do_pad
        pad_size = pad_size if pad_size is not None else self.pad_size
        pad_size = get_size_dict(pad_size, default_to_square=True)
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb

        images = make_list_of_images(images)

        if not valid_images(images):
            raise ValueError(
                "Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, "
                "torch.Tensor, tf.Tensor or jax.ndarray."
            )

        if do_resize and (size is None or resample is None):
            raise ValueError("Size and resample must be specified if do_resize is True.")

        if do_rescale and rescale_factor is None:
            raise ValueError("Rescale factor must be specified if do_rescale is True.")

        if do_normalize and (image_mean is None or image_std is None):
            raise ValueError("Image mean and std must be specified if do_normalize is True.")

        if do_pad and pad_size is None:
            raise ValueError("Pad size must be specified if do_pad is True.")

        # PIL RGBA images are converted to RGB
        if do_convert_rgb:
            images = [convert_to_rgb(image) for image in images]

        # All transformations expect numpy arrays.
        images = [to_numpy_array(image) for image in images]

        original_sizes = [get_image_size(image) for image in images]

        if do_resize:
            images = [self.resize(image=image, size=size, resample=resample) for image in images]

        reshaped_input_sizes = [get_image_size(image) for image in images]

        if do_rescale:
            images = [self.rescale(image=image, scale=rescale_factor) for image in images]

        if do_normalize:
            images = [self.normalize(image=image, mean=image_mean, std=image_std) for image in images]

        if do_pad:
            images = [self.pad_image(image=image, pad_size=pad_size) for image in images]

        images = [to_channel_dimension_format(image, data_format) for image in images]
        encoded_outputs = BatchFeature(
            data={
                "pixel_values": images,
                "original_sizes": original_sizes,
                "reshaped_input_sizes": reshaped_input_sizes,
            },
            tensor_type=return_tensors,
        )
        return encoded_outputs

    def post_process_masks(
        self, masks, original_sizes, reshaped_input_sizes, mask_threshold=0.0, binarize=True, pad_size=None
    ):
        """
        Remove padding and upscale masks to the original image size.

        Args:
            masks (`Union[List[torch.Tensor], List[np.ndarray]]`):
                Batched masks from the mask_decoder in (batch_size, num_channels, height, width) format.
            original_sizes (`Union[torch.Tensor, List[Tuple[int,int]]]`):
                The original sizes of each image before it was resized to the model's expected input shape, in (height,
                width) format.
            reshaped_input_sizes (`Union[torch.Tensor, List[Tuple[int,int]]]`):
                The size of each image as it is fed to the model, in (height, width) format. Used to remove padding.
            mask_threshold (`float`, *optional*, defaults to 0.0):
                The threshold to use for binarizing the masks.
            binarize (`bool`, *optional*, defaults to `True`):
                Whether to binarize the masks.
            pad_size (`int`, *optional*, defaults to `self.pad_size`):
                The target size the images were padded to before being passed to the model. If None, the target size is
                assumed to be the processor's `pad_size`.
        Returns:
            (`torch.Tensor`): Batched masks in batch_size, num_channels, height, width) format, where (height, width)
            is given by original_size.
        """
        requires_backends(self, ["torch"])
        pad_size = self.pad_size if pad_size is None else pad_size
        target_image_size = (pad_size["height"], pad_size["width"])
        if isinstance(original_sizes, (torch.Tensor, np.ndarray)):
            original_sizes = original_sizes.tolist()
        if isinstance(reshaped_input_sizes, (torch.Tensor, np.ndarray)):
            reshaped_input_sizes = reshaped_input_sizes.tolist()
        output_masks = []
        for i, original_size in enumerate(original_sizes):
            if isinstance(masks[i], np.ndarray):
                masks[i] = torch.from_numpy(masks[i])
            elif not isinstance(masks[i], torch.Tensor):
                raise ValueError("Input masks should be a list of `torch.tensors` or a list of `np.ndarray`")
            interpolated_mask = F.interpolate(masks[i], target_image_size, mode="bilinear", align_corners=False)
            interpolated_mask = interpolated_mask[..., : reshaped_input_sizes[i][0], : reshaped_input_sizes[i][1]]
            interpolated_mask = F.interpolate(interpolated_mask, original_size, mode="bilinear", align_corners=False)
            if binarize:
                interpolated_mask = interpolated_mask > mask_threshold
            output_masks.append(interpolated_mask)

        return output_masks

    def post_process_for_mask_generation(self, all_masks, all_scores, all_boxes, crops_nms_thresh):
        """
        Post processes mask that are generated by calling the Non Maximum Suppression algorithm on the predicted masks.

        Args:
            all_masks (`List[torch.Tensor]`):
                List of all predicted segmentation masks
            all_scores (`List[torch.Tensor]`):
                List of all predicted iou scores
            all_boxes (`List[torch.Tensor]`):
                List of all bounding boxes of the predicted masks
            crops_nms_thresh (`float`):
                Threshold for NMS (Non Maximum Suppression) algorithm.
        """
        return _postprocess_for_mg(all_masks, all_scores, all_boxes, crops_nms_thresh)

    def generate_crop_boxes(
        self,
        image,
        target_size,
        crop_n_layers: int = 0,
        overlap_ratio: float = 512 / 1500,
        points_per_crop: Optional[int] = 32,
        crop_n_points_downscale_factor: Optional[List[int]] = 1,
        device: Optional["torch.device"] = None,
    ):
        """
        Generates a list of crop boxes of different sizes. Each layer has (2**i)**2 boxes for the ith layer.

        Args:
            image (`np.array`):
                Input original image
            target_size (`int`):
                Target size of the resized image
            crop_n_layers (`int`, *optional*, defaults to 0):
                If >0, mask prediction will be run again on crops of the image. Sets the number of layers to run, where
                each layer has 2**i_layer number of image crops.
            overlap_ratio (`float`, *optional*, defaults to 512/1500):
                Sets the degree to which crops overlap. In the first crop layer, crops will overlap by this fraction of
                the image length. Later layers with more crops scale down this overlap.
            points_per_crop (`int`, *optional*, defaults to 32):
                Number of points to sample from each crop.
            crop_n_points_downscale_factor (`List[int]`, *optional*, defaults to 1):
                The number of points-per-side sampled in layer n is scaled down by crop_n_points_downscale_factor**n.
            device (`torch.device`, *optional*, defaults to None):
                Device to use for the computation. If None, cpu will be used.
        """
        return _generate_crop_boxes(
            image, target_size, crop_n_layers, overlap_ratio, points_per_crop, crop_n_points_downscale_factor, device
        )

    def filter_masks(
        self,
        masks,
        iou_scores,
        original_size,
        cropped_box_image,
        pred_iou_thresh=0.88,
        stability_score_thresh=0.95,
        mask_threshold=0,
        stability_score_offset=1,
    ):
        """
        Filters the predicted masks by selecting only the ones that meets several criteria. The first criterion being
        that the iou scores needs to be greater than `pred_iou_thresh`. The second criterion is that the stability
        score needs to be greater than `stability_score_thresh`. The method also converts the predicted masks to
        bounding boxes and pad the predicted masks if necessary.

        Args:
            masks (`torch.Tensor`):
                Input masks.
            iou_scores (`torch.Tensor`):
                List of IoU scores.
            original_size (`Tuple[int,int]`):
                Size of the orginal image.
            cropped_box_image (`np.array`):
                The cropped image.
            pred_iou_thresh (`float`, *optional*, defaults to 0.88):
                The threshold for the iou scores.
            stability_score_thresh (`float`, *optional*, defaults to 0.95):
                The threshold for the stability score.
            mask_threshold (`float`, *optional*, defaults to 0):
                The threshold for the predicted masks.
            stability_score_offset (`float`, *optional*, defaults to 1):
                The offset for the stability score used in the `_compute_stability_score` method.

        """
        requires_backends(self, ["torch"])
        original_height, original_width = original_size
        iou_scores = iou_scores.flatten(0, 1)
        masks = masks.flatten(0, 1)

        if masks.shape[0] != iou_scores.shape[0]:
            raise ValueError("masks and iou_scores must have the same batch size.")

        if masks.device != iou_scores.device:
            iou_scores = iou_scores.to(masks.device)

        batch_size = masks.shape[0]

        keep_mask = torch.ones(batch_size, dtype=torch.bool, device=masks.device)

        if pred_iou_thresh > 0.0:
            keep_mask = keep_mask & (iou_scores > pred_iou_thresh)

        # compute stability score
        if stability_score_thresh > 0.0:
            stability_scores = _compute_stability_score(masks, mask_threshold, stability_score_offset)
            keep_mask = keep_mask & (stability_scores > stability_score_thresh)

        scores = iou_scores[keep_mask]
        masks = masks[keep_mask]

        # binarize masks
        masks = masks > mask_threshold
        converted_boxes = _batched_mask_to_box(masks)

        keep_mask = ~_is_box_near_crop_edge(
            converted_boxes, cropped_box_image, [0, 0, original_width, original_height]
        )

        scores = scores[keep_mask]
        masks = masks[keep_mask]
        converted_boxes = converted_boxes[keep_mask]

        masks = _pad_masks(masks, cropped_box_image, original_height, original_width)
        # conversion to rle is necessary to run non-maximum suppresion
        masks = _mask_to_rle_pytorch(masks)

        return masks, scores, converted_boxes


def _compute_stability_score(masks: "torch.Tensor", mask_threshold: float, stability_score_offset: int):
    # One mask is always contained inside the other.
    # Save memory by preventing unnecesary cast to torch.int64
    intersections = (
        (masks > (mask_threshold + stability_score_offset)).sum(-1, dtype=torch.int16).sum(-1, dtype=torch.int32)
    )
    unions = (masks > (mask_threshold - stability_score_offset)).sum(-1, dtype=torch.int16).sum(-1, dtype=torch.int32)
    stability_scores = intersections / unions
    return stability_scores


def _build_point_grid(n_per_side: int) -> np.ndarray:
    """Generates a 2D grid of points evenly spaced in [0,1]x[0,1]."""
    offset = 1 / (2 * n_per_side)
    points_one_side = np.linspace(offset, 1 - offset, n_per_side)
    points_x = np.tile(points_one_side[None, :], (n_per_side, 1))
    points_y = np.tile(points_one_side[:, None], (1, n_per_side))
    points = np.stack([points_x, points_y], axis=-1).reshape(-1, 2)
    return points


def _normalize_coordinates(
    target_size: int, coords: np.ndarray, original_size: Tuple[int, int], is_bounding_box=False
) -> np.ndarray:
    """
    Expects a numpy array of length 2 in the final dimension. Requires the original image size in (height, width)
    format.
    """
    old_height, old_width = original_size

    scale = target_size * 1.0 / max(old_height, old_width)
    new_height, new_width = old_height * scale, old_width * scale
    new_width = int(new_width + 0.5)
    new_height = int(new_height + 0.5)

    coords = deepcopy(coords).astype(float)

    if is_bounding_box:
        coords = coords.reshape(-1, 2, 2)

    coords[..., 0] = coords[..., 0] * (new_width / old_width)
    coords[..., 1] = coords[..., 1] * (new_height / old_height)

    if is_bounding_box:
        coords = coords.reshape(-1, 4)

    return coords


def _generate_crop_boxes(
    image,
    target_size: int,  # Is it tuple here?
    crop_n_layers: int = 0,
    overlap_ratio: float = 512 / 1500,
    points_per_crop: Optional[int] = 32,
    crop_n_points_downscale_factor: Optional[List[int]] = 1,
    device: Optional["torch.device"] = None,
) -> Tuple[List[List[int]], List[int]]:
    """
    Generates a list of crop boxes of different sizes. Each layer has (2**i)**2 boxes for the ith layer.

    Args:
        image (Union[`numpy.ndarray`, `PIL.Image`, `torch.Tensor`]):
            Image to generate crops for.
        target_size (`int`):
            Size of the smallest crop.
        crop_n_layers (`int`, *optional*):
            If `crops_n_layers>0`, mask prediction will be run again on crops of the image. Sets the number of layers
            to run, where each layer has 2**i_layer number of image crops.
        overlap_ratio (`int`, *optional*):
            Sets the degree to which crops overlap. In the first crop layer, crops will overlap by this fraction of the
            image length. Later layers with more crops scale down this overlap.
        points_per_crop (`int`, *optional*):
            Number of points to sample per crop.
        crop_n_points_downscale_factor (`int`, *optional*):
            The number of points-per-side sampled in layer n is scaled down by crop_n_points_downscale_factor**n.
        device (`torch.device`, *optional*):
            Device to run the crop generation on. Defaults to CPU.
    """
    if device is None:
        device = torch.device("cpu")

    if isinstance(image, list):
        raise ValueError("Only one image is allowed for crop generation.")
    image = to_numpy_array(image)
    original_size = get_image_size(image)

    points_grid = []
    for i in range(crop_n_layers + 1):
        n_points = int(points_per_crop / (crop_n_points_downscale_factor**i))
        points_grid.append(_build_point_grid(n_points))

    crop_boxes, layer_idxs = _generate_per_layer_crops(crop_n_layers, overlap_ratio, original_size)

    cropped_images, point_grid_per_crop = _generate_crop_images(
        crop_boxes, image, points_grid, layer_idxs, target_size, original_size
    )

    crop_boxes = torch.tensor(crop_boxes, dtype=torch.float32, device=device)
    point_grid_per_crop = np.array([point_grid_per_crop])
    points_per_crop = torch.tensor(point_grid_per_crop, device=device)
    points_per_crop = points_per_crop.permute(0, 2, 1, 3)

    input_labels = torch.ones_like(points_per_crop[:, :, :, 0], dtype=torch.long, device=device)

    return crop_boxes, points_per_crop, cropped_images, input_labels


def _generate_per_layer_crops(crop_n_layers, overlap_ratio, original_size):
    """
    Generates 2 ** (layers idx + 1) crops for each crop_n_layers. Crops are in the XYWH format : The XYWH format
    consists of the following required indices:
        - X: X coordinate of the top left of the bounding box
        - Y: Y coordinate of the top left of the bounding box
        - W: width of the bounding box
        - H: height of the bounding box
    """
    crop_boxes, layer_idxs = [], []
    im_height, im_width = original_size
    short_side = min(im_height, im_width)

    # Original image
    crop_boxes.append([0, 0, im_width, im_height])
    layer_idxs.append(0)
    for i_layer in range(crop_n_layers):
        n_crops_per_side = 2 ** (i_layer + 1)
        overlap = int(overlap_ratio * short_side * (2 / n_crops_per_side))

        crop_width = int(math.ceil((overlap * (n_crops_per_side - 1) + im_width) / n_crops_per_side))
        crop_height = int(math.ceil((overlap * (n_crops_per_side - 1) + im_height) / n_crops_per_side))

        crop_box_x0 = [int((crop_width - overlap) * i) for i in range(n_crops_per_side)]
        crop_box_y0 = [int((crop_height - overlap) * i) for i in range(n_crops_per_side)]

        for left, top in product(crop_box_x0, crop_box_y0):
            box = [left, top, min(left + crop_width, im_width), min(top + crop_height, im_height)]
            crop_boxes.append(box)
            layer_idxs.append(i_layer + 1)

    return crop_boxes, layer_idxs


def _generate_crop_images(crop_boxes, image, points_grid, layer_idxs, target_size, original_size):
    """
    Takes as an input bounding boxes that are used to crop the image. Based in the crops, the corresponding points are
    also passed.
    """
    cropped_images = []
    total_points_per_crop = []
    for i, crop_box in enumerate(crop_boxes):
        left, top, right, bottom = crop_box

        channel_dim = infer_channel_dimension_format(image)
        if channel_dim == ChannelDimension.LAST:
            cropped_im = image[top:bottom, left:right, :]
        else:
            cropped_im = image[:, top:bottom, left:right]

        cropped_images.append(cropped_im)

        cropped_im_size = get_image_size(cropped_im)
        points_scale = np.array(cropped_im_size)[None, ::-1]

        points = points_grid[layer_idxs[i]] * points_scale
        normalized_points = _normalize_coordinates(target_size, points, original_size)
        total_points_per_crop.append(normalized_points)

    return cropped_images, total_points_per_crop


def _pad_masks(masks, crop_box: List[int], orig_height: int, orig_width: int):
    left, top, right, bottom = crop_box
    if left == 0 and top == 0 and right == orig_width and bottom == orig_height:
        return masks
    # Coordinate transform masks
    pad_x, pad_y = orig_width - (right - left), orig_height - (bottom - top)
    pad = (left, pad_x - left, top, pad_y - top)
    return torch.nn.functional.pad(masks, pad, value=0)


def _is_box_near_crop_edge(boxes, crop_box, orig_box, atol=20.0):
    """Filter masks at the edge of a crop, but not at the edge of the original image."""
    crop_box_torch = torch.as_tensor(crop_box, dtype=torch.float, device=boxes.device)
    orig_box_torch = torch.as_tensor(orig_box, dtype=torch.float, device=boxes.device)

    left, top, _, _ = crop_box
    offset = torch.tensor([[left, top, left, top]], device=boxes.device)
    # Check if boxes has a channel dimension
    if len(boxes.shape) == 3:
        offset = offset.unsqueeze(1)
    boxes = (boxes + offset).float()

    near_crop_edge = torch.isclose(boxes, crop_box_torch[None, :], atol=atol, rtol=0)
    near_image_edge = torch.isclose(boxes, orig_box_torch[None, :], atol=atol, rtol=0)
    near_crop_edge = torch.logical_and(near_crop_edge, ~near_image_edge)
    return torch.any(near_crop_edge, dim=1)


def _batched_mask_to_box(masks: "torch.Tensor"):
    """
    Computes the bounding boxes around the given input masks. The bounding boxes are in the XYXY format which
    corresponds the following required indices:
        - LEFT: left hand side of the bounding box
        - TOP: top of the bounding box
        - RIGHT: right of the bounding box
        - BOTTOM: bottom of the bounding box

    Return [0,0,0,0] for an empty mask. For input shape channel_1 x channel_2 x ... x height x width, the output shape
    is channel_1 x channel_2 x ... x 4.

    Args:
        - masks (`torch.Tensor` of shape `(batch, nb_mask, height, width)`)
    """
    # torch.max below raises an error on empty inputs, just skip in this case

    if torch.numel(masks) == 0:
        return torch.zeros(*masks.shape[:-2], 4, device=masks.device)

    # Normalize shape to Cxheightxwidth
    shape = masks.shape
    height, width = shape[-2:]

    # Get top and bottom edges
    in_height, _ = torch.max(masks, dim=-1)
    in_height_coords = in_height * torch.arange(height, device=in_height.device)[None, :]
    bottom_edges, _ = torch.max(in_height_coords, dim=-1)
    in_height_coords = in_height_coords + height * (~in_height)
    top_edges, _ = torch.min(in_height_coords, dim=-1)

    # Get left and right edges
    in_width, _ = torch.max(masks, dim=-2)
    in_width_coords = in_width * torch.arange(width, device=in_width.device)[None, :]
    right_edges, _ = torch.max(in_width_coords, dim=-1)
    in_width_coords = in_width_coords + width * (~in_width)
    left_edges, _ = torch.min(in_width_coords, dim=-1)

    # If the mask is empty the right edge will be to the left of the left edge.
    # Replace these boxes with [0, 0, 0, 0]
    empty_filter = (right_edges < left_edges) | (bottom_edges < top_edges)
    out = torch.stack([left_edges, top_edges, right_edges, bottom_edges], dim=-1)
    out = out * (~empty_filter).unsqueeze(-1)

    # Return to original shape
    out = out.reshape(*shape[:-2], 4)
    return out


def _mask_to_rle_pytorch(input_mask: "torch.Tensor"):
    """
    Encodes masks the run-length encoding (RLE), in the format expected by pycoco tools.
    """
    # Put in fortran order and flatten height and width
    batch_size, height, width = input_mask.shape
    input_mask = input_mask.permute(0, 2, 1).flatten(1)

    # Compute change indices
    diff = input_mask[:, 1:] ^ input_mask[:, :-1]
    change_indices = diff.nonzero()

    # Encode run length
    out = []
    for i in range(batch_size):
        cur_idxs = change_indices[change_indices[:, 0] == i, 1] + 1
        btw_idxs = cur_idxs[1:] - cur_idxs[:-1]
        counts = [] if input_mask[i, 0] == 0 else [0]
        counts += [cur_idxs[0].item()] + btw_idxs.tolist() + [height * width - cur_idxs[-1]]
        out.append({"size": [height, width], "counts": counts})
    return out


def _rle_to_mask(rle: Dict[str, Any]) -> np.ndarray:
    """Compute a binary mask from an uncompressed RLE."""
    height, width = rle["size"]
    mask = np.empty(height * width, dtype=bool)
    idx = 0
    parity = False
    for count in rle["counts"]:
        mask[idx : idx + count] = parity
        idx += count
        parity = not parity
    mask = mask.reshape(width, height)
    return mask.transpose()  # Reshape to original shape


def _postprocess_for_mg(rle_masks, iou_scores, mask_boxes, amg_crops_nms_thresh=0.7):
    """
    Perform NMS (Non Maxium Suppression) on the outputs.

    Args:
            rle_masks (`torch.Tensor`):
                binary masks in the RLE format
            iou_scores (`torch.Tensor` of shape (nb_masks, 1)):
                iou_scores predicted by the model
            mask_boxes (`torch.Tensor`):
                The bounding boxes corresponding to segmentation masks
            amg_crops_nms_thresh (`float`, *optional*, defaults to 0.7):
                NMS threshold.
    """
    keep_by_nms = batched_nms(
        boxes=mask_boxes.float(),
        scores=iou_scores,
        idxs=torch.zeros(mask_boxes.shape[0]),
        iou_threshold=amg_crops_nms_thresh,
    )

    iou_scores = iou_scores[keep_by_nms]
    rle_masks = [rle_masks[i] for i in keep_by_nms]
    mask_boxes = mask_boxes[keep_by_nms]
    masks = [_rle_to_mask(rle) for rle in rle_masks]

    return masks, iou_scores, rle_masks, mask_boxes
