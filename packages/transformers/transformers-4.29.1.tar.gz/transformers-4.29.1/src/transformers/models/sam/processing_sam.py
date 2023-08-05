# coding=utf-8
# Copyright 2023 The HuggingFace Inc. team.
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
"""
Processor class for SAM.
"""
from copy import deepcopy
from typing import Optional, Union

import numpy as np

from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import BatchEncoding
from ...utils import TensorType, is_torch_available


if is_torch_available():
    import torch


class SamProcessor(ProcessorMixin):
    r"""
    Constructs a SAM processor which wraps a SAM image processor and an 2D points & Bounding boxes processor into a
    single processor.

    [`SamProcessor`] offers all the functionalities of [`SamImageProcessor`]. See the docstring of
    [`~SamImageProcessor.__call__`] for more information.

    Args:
        image_processor (`SamImageProcessor`):
            An instance of [`SamImageProcessor`]. The image processor is a required input.
    """
    attributes = ["image_processor"]
    image_processor_class = "SamImageProcessor"

    def __init__(self, image_processor):
        super().__init__(image_processor)
        self.current_processor = self.image_processor
        self.point_pad_value = -10
        self.target_size = self.image_processor.size["longest_edge"]

    def __call__(
        self,
        images=None,
        input_points=None,
        input_labels=None,
        input_boxes=None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        **kwargs,
    ) -> BatchEncoding:
        """
        This method uses [`SamImageProcessor.__call__`] method to prepare image(s) for the model. It also prepares 2D
        points and bounding boxes for the model if they are provided.
        """
        encoding_image_processor = self.image_processor(
            images,
            return_tensors=return_tensors,
            **kwargs,
        )

        # pop arguments that are not used in the foward but used nevertheless
        original_sizes = encoding_image_processor["original_sizes"]

        if isinstance(original_sizes, torch.Tensor):
            original_sizes = original_sizes.numpy()

        input_points, input_labels, input_boxes = self._check_and_preprocess_points(
            input_points=input_points,
            input_labels=input_labels,
            input_boxes=input_boxes,
        )

        encoding_image_processor = self._normalize_and_convert(
            encoding_image_processor,
            original_sizes,
            input_points=input_points,
            input_labels=input_labels,
            input_boxes=input_boxes,
            return_tensors=return_tensors,
        )

        return encoding_image_processor

    def _normalize_and_convert(
        self,
        encoding_image_processor,
        original_sizes,
        input_points=None,
        input_labels=None,
        input_boxes=None,
        return_tensors="pt",
    ):
        if input_points is not None:
            if len(original_sizes) != len(input_points):
                input_points = [
                    self._normalize_coordinates(self.target_size, point, original_sizes[0]) for point in input_points
                ]
            else:
                input_points = [
                    self._normalize_coordinates(self.target_size, point, original_size)
                    for point, original_size in zip(input_points, original_sizes)
                ]
            # check that all arrays have the same shape
            if not all([point.shape == input_points[0].shape for point in input_points]):
                if input_labels is not None:
                    input_points, input_labels = self._pad_points_and_labels(input_points, input_labels)

            input_points = np.array(input_points)

        if input_labels is not None:
            input_labels = np.array(input_labels)

        if input_boxes is not None:
            if len(original_sizes) != len(input_boxes):
                input_boxes = [
                    self._normalize_coordinates(self.target_size, box, original_sizes[0], is_bounding_box=True)
                    for box in input_boxes
                ]
            else:
                input_boxes = [
                    self._normalize_coordinates(self.target_size, box, original_size, is_bounding_box=True)
                    for box, original_size in zip(input_boxes, original_sizes)
                ]
            input_boxes = np.array(input_boxes)

        if input_boxes is not None:
            if return_tensors == "pt":
                input_boxes = torch.from_numpy(input_boxes)
                # boxes batch size of 1 by default
                input_boxes = input_boxes.unsqueeze(1) if len(input_boxes.shape) != 3 else input_boxes
            encoding_image_processor.update({"input_boxes": input_boxes})
        if input_points is not None:
            if return_tensors == "pt":
                input_points = torch.from_numpy(input_points)
                # point batch size of 1 by default
                input_points = input_points.unsqueeze(1) if len(input_points.shape) != 4 else input_points
            encoding_image_processor.update({"input_points": input_points})
        if input_labels is not None:
            if return_tensors == "pt":
                input_labels = torch.from_numpy(input_labels)
                # point batch size of 1 by default
                input_labels = input_labels.unsqueeze(1) if len(input_labels.shape) != 3 else input_labels
            encoding_image_processor.update({"input_labels": input_labels})

        return encoding_image_processor

    def _pad_points_and_labels(self, input_points, input_labels):
        r"""
        The method pads the 2D points and labels to the maximum number of points in the batch.
        """
        expected_nb_points = max([point.shape[0] for point in input_points])
        processed_input_points = []
        for i, point in enumerate(input_points):
            if point.shape[0] != expected_nb_points:
                point = np.concatenate(
                    [point, np.zeros((expected_nb_points - point.shape[0], 2)) + self.point_pad_value], axis=0
                )
                input_labels[i] = np.append(input_labels[i], [self.point_pad_value])
            processed_input_points.append(point)
        input_points = processed_input_points
        return input_points, input_labels

    def _normalize_coordinates(
        self, target_size: int, coords: np.ndarray, original_size, is_bounding_box=False
    ) -> np.ndarray:
        """
        Expects a numpy array of length 2 in the final dimension. Requires the original image size in (H, W) format.
        """
        old_h, old_w = original_size
        new_h, new_w = self.image_processor._get_preprocess_shape(original_size, longest_edge=target_size)
        coords = deepcopy(coords).astype(float)

        if is_bounding_box:
            coords = coords.reshape(-1, 2, 2)

        coords[..., 0] = coords[..., 0] * (new_w / old_w)
        coords[..., 1] = coords[..., 1] * (new_h / old_h)

        if is_bounding_box:
            coords = coords.reshape(-1, 4)

        return coords

    def _check_and_preprocess_points(
        self,
        input_points=None,
        input_labels=None,
        input_boxes=None,
    ):
        r"""
        Check and preprocesses the 2D points, labels and bounding boxes. It checks if the input is valid and if they
        are, it converts the coordinates of the points and bounding boxes. If a user passes directly a `torch.Tensor`,
        it is converted to a `numpy.ndarray` and then to a `list`.
        """
        if input_points is not None:
            if isinstance(input_points, torch.Tensor):
                input_points = input_points.numpy().tolist()

            if not isinstance(input_points, list) and not isinstance(input_points[0], list):
                raise ValueError("Input points must be a list of list of floating integers.")
            input_points = [np.array(input_point) for input_point in input_points]
        else:
            input_points = None

        if input_labels is not None:
            if isinstance(input_labels, torch.Tensor):
                input_labels = input_labels.numpy().tolist()

            if not isinstance(input_labels, list) and not isinstance(input_labels[0], list):
                raise ValueError("Input labels must be a list of list integers.")
            input_labels = [np.array(label) for label in input_labels]
        else:
            input_labels = None

        if input_boxes is not None:
            if isinstance(input_boxes, torch.Tensor):
                input_boxes = input_boxes.numpy().tolist()

            if (
                not isinstance(input_boxes, list)
                and not isinstance(input_boxes[0], list)
                and not isinstance(input_boxes[0][0], list)
            ):
                raise ValueError("Input boxes must be a list of list of list of floating integers.")
            input_boxes = [np.array(box).astype(np.float32) for box in input_boxes]
        else:
            input_boxes = None

        return input_points, input_labels, input_boxes

    @property
    def model_input_names(self):
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(image_processor_input_names))

    def post_process_masks(self, *args, **kwargs):
        return self.image_processor.post_process_masks(*args, **kwargs)
