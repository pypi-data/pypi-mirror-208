import logging
import warnings
from pathlib import Path
from typing import Dict, List, Union

from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from picsellia_annotations.exceptions import FileError, ParsingError
from picsellia_annotations.utils import read_pascal_voc_file
from picsellia_annotations.voc import Object, PascalVOCFile

from picsellia.decorators import exception_handler
from picsellia.exceptions import (
    FileNotFoundException,
    UnparsableAnnotationFileException,
)
from picsellia.sdk.asset import Asset
from picsellia.types.enums import InferenceType

warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)
logger = logging.getLogger("picsellia")


@exception_handler
@beartype
def parse_file(file_path: Union[Path, str]) -> PascalVOCFile:
    try:
        return read_pascal_voc_file(file_path=file_path)
    except FileError:
        raise FileNotFoundException(f"{file_path} not found")
    except ParsingError as e:
        raise UnparsableAnnotationFileException(
            f"Could not parse VOC file {file_path} because : {e}"
        )


@exception_handler
@beartype
def parse_objects(vocfile: PascalVOCFile) -> List[Object]:
    if isinstance(vocfile.annotation.object, Object):
        return [vocfile.annotation.object]
    else:
        return vocfile.annotation.object


@exception_handler
@beartype
def read_annotations_from_voc_objects(
    inference_type: InferenceType,
    objects: List[Object],
    labels: Dict[str, str],
    asset: Asset,
) -> List[Dict]:
    rectangles: List[Dict] = []
    polygons: List[Dict] = []
    classifications: List[Dict] = []
    for obj in objects:
        label_id = labels[obj.name]

        if inference_type == InferenceType.SEGMENTATION:
            coords = obj.polygon_to_list_coordinates()
            polygons.append({"polygon": coords, "label_id": label_id})
        elif inference_type == InferenceType.OBJECT_DETECTION:
            rectangles.append(
                {
                    "x": int(obj.bndbox.xmin),
                    "y": int(obj.bndbox.ymin),
                    "w": int(obj.bndbox.xmax) - int(obj.bndbox.xmin),
                    "h": int(obj.bndbox.ymax) - int(obj.bndbox.ymin),
                    "label_id": label_id,
                }
            )
        elif inference_type == InferenceType.CLASSIFICATION:
            classifications.append({"label_id": label_id})

    return [
        {
            "asset_id": asset.id,
            "rectangles": rectangles,
            "polygons": polygons,
            "classifications": classifications,
        }
    ]
