import logging
import warnings
from pathlib import Path
from typing import Dict, List, Union

from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from picsellia_annotations.coco import Annotation as COCOAnnotation
from picsellia_annotations.coco import COCOFile
from picsellia_annotations.exceptions import FileError, ParsingError
from picsellia_annotations.utils import read_coco_file

from picsellia.decorators import exception_handler
from picsellia.exceptions import (
    FileNotFoundException,
    UnparsableAnnotationFileException,
)
from picsellia.sdk.label import Label
from picsellia.types.enums import InferenceType

warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)
logger = logging.getLogger("picsellia")


@exception_handler
@beartype
def parse_coco_file(file_path: Union[Path, str]) -> COCOFile:
    try:
        return read_coco_file(file_path=file_path)
    except FileError:
        raise FileNotFoundException(f"{file_path} not found")
    except ParsingError as e:
        raise UnparsableAnnotationFileException(
            f"Could not parse COCO file {file_path} because : {e}"
        )


@exception_handler
@beartype
def read_annotations(
    cocofile_type: InferenceType,
    coco_annotations: List[COCOAnnotation],
    labels: Dict[int, Label],
    assets: Dict[int, str],
) -> List[Dict]:
    annotations_asset_map: Dict[str, Dict] = {}
    for annotation in coco_annotations:
        try:
            label = labels[annotation.category_id]
        except KeyError:  # pragma: no cover
            logger.error(
                f"category_id {annotation.category_id} not found into retrieved labels"
            )
            continue

        try:
            asset_id = assets[annotation.image_id]
        except KeyError:
            logger.error(
                f"image_id {annotation.image_id} not found into retrieved assets"
            )
            continue

        if asset_id not in annotations_asset_map:
            annotations_asset_map[asset_id] = {
                "rectangles": [],
                "classifications": [],
                "polygons": [],
            }

        if cocofile_type == InferenceType.SEGMENTATION:
            if not annotation.is_rle():
                polygon_coords = annotation.polygon_to_list_coordinates()
            else:
                logger.error(
                    f"annotation_id {annotation.id} is a RLE which is not supported yet"
                )
                continue

            for polygon_coord in polygon_coords:
                annotations_asset_map[asset_id]["polygons"].append(
                    {
                        "polygon": polygon_coord,
                        "label_id": label.id,
                    }
                )
        elif cocofile_type == InferenceType.OBJECT_DETECTION:
            annotations_asset_map[asset_id]["rectangles"].append(
                {
                    "x": int(annotation.bbox[0]),
                    "y": int(annotation.bbox[1]),
                    "w": int(annotation.bbox[2]),
                    "h": int(annotation.bbox[3]),
                    "label_id": label.id,
                }
            )
        elif cocofile_type == InferenceType.CLASSIFICATION:
            annotations_asset_map[asset_id]["classifications"].append(
                {"label_id": label.id}
            )

    return [
        {"asset_id": asset_id, **annotation}
        for asset_id, annotation in annotations_asset_map.items()
    ]
