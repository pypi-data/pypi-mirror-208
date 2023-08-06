import math
from typing import Dict, List, Optional, Tuple, Union

from picsellia_annotations.coco import Annotation as COCOAnnotation
from picsellia_annotations.coco import Category as COCOCategory
from picsellia_annotations.coco import COCOFile
from picsellia_annotations.coco import Image as COCOImage

from picsellia.exceptions import ResourceNotFoundError
from picsellia.sdk.asset import MultiAsset


class COCOFileBuilder:
    def __init__(self, enforced_ordered_labels: Optional[List[str]] = None):
        self.labels = {}
        self.enforced_ordered_labels = enforced_ordered_labels
        if enforced_ordered_labels:
            for k in range(len(enforced_ordered_labels)):
                self.labels[enforced_ordered_labels[k]] = k

        self.assets = {}
        self.coco_annotations = []
        self.coco_images = []
        self.coco_categories = []

    def load_coco_annotations(self, loaded_annotations: Dict[str, list]) -> List[str]:
        for asset_id, annotations in loaded_annotations.items():
            # Find image id in already seen assets, store image_id for each asset
            if asset_id in self.assets:  # pragma: no cover
                image_id = self.assets[asset_id]
            else:
                image_id = len(self.assets)
                self.assets[asset_id] = image_id

            self._build_coco_shapes(image_id, annotations)

        return list(self.assets.keys())

    def load_coco_images(self, loaded_assets: MultiAsset):
        for asset in loaded_assets:
            coco_image = COCOImage(
                id=self.assets[str(asset.id)],
                file_name=asset.filename,
                width=asset.width,
                height=asset.height,
            )
            self.coco_images.append(coco_image)

    def load_coco_categories(self, loaded_label_names: List[str]):
        for label_name in loaded_label_names:
            if label_name not in self.labels:
                continue
            category = COCOCategory(id=self.labels[label_name], name=label_name)
            self.coco_categories.append(category)

        # Return categories by order of id
        self.coco_categories = sorted(self.coco_categories, key=lambda cat: cat.id)

    def build(self) -> COCOFile:
        return COCOFile(
            categories=self.coco_categories,
            images=self.coco_images,
            annotations=self.coco_annotations,
        )

    def _build_coco_shapes(
        self,
        image_id: int,
        annotations: List,
    ):
        for annotation in annotations:
            if "classifications" in annotation and annotation["classifications"]:
                for classification in annotation["classifications"]:
                    category_id = self._retrieve_label(classification["label"])
                    coco_annotation = COCOAnnotation(
                        id=len(self.coco_annotations),
                        image_id=image_id,
                        category_id=category_id,
                        bbox=[],
                        segmentation=[],
                    )
                    self.coco_annotations.append(coco_annotation)

            if "rectangles" in annotation and annotation["rectangles"]:
                for rectangle in annotation["rectangles"]:
                    category_id = self._retrieve_label(rectangle["label"])
                    coco_annotation = COCOAnnotation(
                        id=len(self.coco_annotations),
                        image_id=image_id,
                        category_id=category_id,
                        bbox=(
                            rectangle["x"],
                            rectangle["y"],
                            rectangle["w"],
                            rectangle["h"],
                        ),
                        segmentation=[],
                    )
                    self.coco_annotations.append(coco_annotation)

            if "polygons" in annotation and annotation["polygons"]:
                for polygon in annotation["polygons"]:
                    if (
                        "polygon" not in polygon or not polygon["polygon"]
                    ):  # pragma: no cover
                        continue
                    category_id = self._retrieve_label(polygon["label"])
                    bbox, shape = COCOFileBuilder._compute_bbox_and_shape(
                        polygon["polygon"]
                    )
                    coco_annotation = COCOAnnotation(
                        id=len(self.coco_annotations),
                        image_id=image_id,
                        category_id=category_id,
                        bbox=bbox,
                        segmentation=[shape],  # COCO needs an array around polygons
                    )
                    self.coco_annotations.append(coco_annotation)

    def _retrieve_label(self, label: str):
        if label not in self.labels:
            if self.enforced_ordered_labels:
                raise ResourceNotFoundError(
                    f"{label} is used by an asset of this dataset but was not given in {self.enforced_ordered_labels}"
                )
            self.labels[label] = len(self.labels)
        return self.labels[label]

    @staticmethod
    def _compute_bbox_and_shape(
        polygon: List[List[Union[int, float]]]
    ) -> Tuple[
        Tuple[
            Union[int, float], Union[int, float], Union[int, float], Union[int, float]
        ],
        List[Union[int, float]],
    ]:
        x_min = math.inf
        x_max = -1
        y_min = math.inf
        y_max = -1

        segmentation = []
        for point in polygon:
            x = point[0]
            x_min = min(x, x_min)
            x_max = max(x, x_max)
            y = point[1]
            y_min = min(y, y_min)
            y_max = max(y, y_max)
            segmentation.append(x)
            segmentation.append(y)

        return (x_min, y_min, x_max - x_min, y_max - y_min), segmentation
