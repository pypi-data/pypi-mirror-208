import json
from collections import defaultdict
from tempfile import NamedTemporaryFile
from typing import List, Tuple

import cv2
import numpy as np
import torch

from dataquality.clients.objectstore import ObjectStore
from dataquality.core._config import GALILEO_DEFAULT_RESULT_BUCKET_NAME
from dataquality.schemas.semantic_segmentation import Contour, Pixel, Polygon

object_store = ObjectStore()


def find_polygons_batch(
    pred_masks: torch.Tensor, gold_masks: torch.Tensor
) -> Tuple[List, List]:
    """Creates polygons for a given batch

    NOTE: Background pixels do not get polygons

    Args:
        masks: Tensor of ground truth or predicted masks
            torch.Tensor of shape (batch_size, height, width)

    Returns (Tuple):
        List of pred polygons for each image in the batch
        List of ground truth polygons for each image in the batch
    """
    pred_masks_np = pred_masks.numpy()
    bs = pred_masks_np.shape[0]
    gold_masks_np = gold_masks.numpy()

    pred_polygons_batch = []
    gold_polygons_batch = []

    for i in range(bs):
        pred_polygons = build_polygons_image(pred_masks_np[i])
        pred_polygons_batch.append(pred_polygons)
        gold_polygons = build_polygons_image(gold_masks_np[i], len(pred_polygons))
        gold_polygons_batch.append(gold_polygons)

    return pred_polygons_batch, gold_polygons_batch


def build_polygons_image(mask: np.ndarray, polygon_idx: int = 0) -> List[Polygon]:
    """Returns a list of Polygons for the mask of a single image

    Args:
        mask: numpy array of shape (height, width) either gold or pred

    Returns:
        List: A list of polygons for the image

    A polygon is a list of CV2 contours, where each contour is a list of
    pixel coordinates that make up the boundary of a shape.
    """
    polygons = []
    for label_idx in np.unique(mask).astype(int).tolist():
        if label_idx == 0:  # Background pixels don't get polygons
            continue

        class_mask = (mask == label_idx).astype(np.uint8)  # maybe don't need this
        # contours is a tuple of numpy arrays
        contours, hierarchy = cv2.findContours(
            class_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        polygons_per_label, polygon_idx = build_polygons_label(
            contours, hierarchy, label_idx, polygon_idx
        )
        polygons.extend(polygons_per_label)

    return polygons


def build_polygons_label(
    contours: Tuple[np.ndarray],
    hierarchy: np.ndarray,
    label_idx: int,
    polygon_idx: int = 0,
) -> Tuple[List[Polygon], int]:
    """Builds the polygons given contours of a single label for one image

    :param contours: a tuple of numpy arrays where each array is a contour
    :param hierarchy: a numpy array of shape (num_contours, 4)
        where each row is a contour
    :param label_idx: the label index for all polygons in the given contours

    :return: a list of polygons where each polygon is a list of contours
    """

    def get_eldest_parent(hier: np.ndarray, idx: int) -> int:
        """Returns the index of the eldest parent of a contour

        If a contour has no parents, return the idx of the contour itself
        """
        current_parent = idx
        next_parent = hierarchy[0, current_parent, -1]
        while next_parent != -1:
            current_parent = next_parent
            next_parent = hierarchy[0, current_parent, -1]

        return current_parent

    all_polygons = defaultdict(list)
    for i, contour in enumerate(contours):
        eldest_parent = get_eldest_parent(hierarchy, i)
        # process the contour by creating a list of Pixel objects
        contour_pixels = [Pixel(x=point[0, 0], y=point[0, 1]) for point in contour]
        all_polygons[eldest_parent].append(Contour(pixels=contour_pixels))
    # Build the polygons
    final_polygons = []
    for contour_parent_idx in all_polygons.keys():
        polygon = Polygon(
            id=polygon_idx,
            label_idx=label_idx,
            contours=all_polygons[contour_parent_idx],
        )
        final_polygons.append(polygon)
        polygon_idx += 1

    return final_polygons, polygon_idx


def draw_polygon(polygon: Polygon, shape: Tuple[int, ...]) -> np.ndarray:
    """Draws one polygon onto a blank image, assigning the polygon a label

    drawContours takes in order an image, a list of contours, the index of the
    contour to draw (or -1 if drawing all), the color of the contour, and the
    thickness of the line to draw or -1 if you want to fill it in

    Args:
        polygon (Polygon): Polygon object
        shape (Tuple[int]): Dimensions of returned image

    Returns:
        np.ndarray: image with single polygon drawn on it
    """
    return cv2.drawContours(
        np.zeros(shape), polygon.contours_opencv, -1, polygon.label_idx, -1
    )


def upload_polygon_contours(
    polygon: Polygon,
    polygon_idx: int,
    prefix: str,
) -> None:
    """Uploads a Polygon's contours to the cloud

    Args:
        polygon(Polygon): A Polygon object
        polygon_idx(int): id to be used in the object name
        prefix(str): prefix of the object name in storage
            - /proj-id/run-id/training/contours/1.json
    """
    obj_name = f"{prefix}/{polygon_idx}.json"

    with NamedTemporaryFile(mode="w+", delete=False) as f:
        json.dump(polygon.contours_json, f)

    object_store.create_object(
        object_name=obj_name,
        file_path=f.name,
        content_type="application/json",
        progress=False,
        bucket_name=GALILEO_DEFAULT_RESULT_BUCKET_NAME,
    )
