import logging
import warnings
from functools import partial
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

import orjson
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning

import picsellia.pxl_multithreading as mlt
from picsellia import exceptions
from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.sdk.classification import Classification
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.label import Label
from picsellia.sdk.line import Line
from picsellia.sdk.multi_object import MultiObject
from picsellia.sdk.point import Point
from picsellia.sdk.polygon import Polygon
from picsellia.sdk.rectangle import Rectangle
from picsellia.sdk.worker import Worker
from picsellia.types.enums import AnnotationStatus
from picsellia.types.schemas import AnnotationSchema
from picsellia.utils import chunk_list

logger = logging.getLogger("picsellia")
warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


class Annotation(Dao):
    def __init__(
        self, connexion: Connexion, dataset_version_id: UUID, asset_id: UUID, data: dict
    ) -> None:
        Dao.__init__(self, connexion, data)
        self._dataset_version_id = dataset_version_id
        self._asset_id = asset_id

    @property
    def asset_id(self) -> UUID:
        """UUID of the (Asset) holding this (Annotation)"""
        return self._asset_id

    @property
    def dataset_version_id(self) -> UUID:
        """UUID of (DatasetVersion) holding this (Annotation)"""
        return self._dataset_version_id

    @property
    def duration(self) -> float:
        """Duration time of this (Annotation)"""
        return self._duration

    @property
    def status(self) -> AnnotationStatus:
        """Status of this (Annotation)"""
        return self._status

    @property
    def worker_id(self) -> UUID:
        """UUID of the (Worker) that created this (Annotation)"""
        return self._worker_id

    def __str__(self):
        return f"{Colors.BLUE}Annotation from worker {self.worker_id} on asset {self.asset_id} {Colors.ENDC} (id: {self.id})"

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/annotation/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def refresh(self, data: dict) -> AnnotationSchema:
        schema = AnnotationSchema(**data)
        self._worker_id = schema.worker_id
        self._duration = schema.duration
        self._status = schema.status
        return schema

    @exception_handler
    @beartype
    def update(
        self,
        worker: Optional[Worker] = None,
        duration: Union[float, int, None] = None,
        status: Union[AnnotationStatus, str, None] = None,
    ) -> None:
        """Update this annotation with a new worker, a new duration or a new status.

        Examples:
            ```python
            one_annotation.update(status=AnnotationStatus.ACCEPTED)
            ```
        Arguments:
            worker (Worker, optional): Worker of this annotation. Defaults to None.
            duration (float, optional): Duration of this annotation. Defaults to None.
            status (AnnotationStatus, optional): Status of this annotation. Defaults to None.
        """
        payload = {}
        if duration:
            payload["duration"] = float(duration)

        if worker:
            payload["worker_id"] = worker.id

        if status:
            payload["status"] = AnnotationStatus.validate(status)

        r = self.connexion.patch(
            f"/sdk/annotation/{self.id}", data=orjson.dumps(payload)
        ).json()
        self.refresh(r)
        logger.info(f"{self} updated")

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete this annotation from the platform.
        All annotations shapes will be deleted!
        This is a very dangerous move.

        :warning: **DANGER ZONE**: Be very careful here!

        Examples:
            ```python
            one_annotation.delete()
            ```
        """
        self.connexion.delete(f"/sdk/annotation/{self.id}")
        logger.info(f"{self} deleted from platform.")

    @exception_handler
    @beartype
    def overwrite(
        self,
        rectangles: Optional[List[Tuple[int, int, int, int, Label]]] = None,
        polygons: Optional[List[Tuple[List[List[int]], Label]]] = None,
        classifications: Optional[List[Label]] = None,
        lines: Optional[List[Tuple[List[List[int]], Label]]] = None,
        points: Optional[List[Tuple[List[int], int, Label]]] = None,
        duration: Union[float, int] = 0.0,
    ) -> None:
        """Overwrite content of this annotation with a new duration and new shapes

        :warning: **DANGER ZONE**: Be very careful here!

        Examples:
            ```python
            one_annotation.overwrite(rectangles=[(10, 20, 30, 40, label_cat), (50, 60, 20, 30, label_dog)])
            ```
        """
        payload = {"duration": duration}
        if rectangles:
            payload["rectangles"] = [
                {
                    "x": rectangle[0],
                    "y": rectangle[1],
                    "w": rectangle[2],
                    "h": rectangle[3],
                    "label_id": rectangle[4].id,
                }
                for rectangle in rectangles
            ]

        if polygons:
            payload["polygons"] = [
                {"polygon": polygon[0], "label_id": polygon[1].id}
                for polygon in polygons
            ]
        if lines:
            payload["lines"] = [
                {"line": line[0], "label_id": line[1].id} for line in lines
            ]
        if points:
            payload["points"] = [
                {"point": point[0], "order": point[1], "label_id": point[2].id}
                for point in points
            ]
        if classifications:
            payload["classifications"] = [
                {"label_id": classification.id} for classification in classifications
            ]

        r = self.connexion.post(
            f"/sdk/annotation/{self.id}/save", data=orjson.dumps(payload)
        ).json()
        self.refresh(r)
        logger.info(
            f"{self} is now saved with a new content. Old shapes already retrieved are not consistent anymore."
        )

    @exception_handler
    @beartype
    def list_rectangles(self) -> List[Rectangle]:
        """Retrieve all rectangles of this annotation

        Examples:
            ```python
            rects = one_annotation.list_rectangles()
            ```
        """
        r = self.connexion.get(f"/sdk/annotation/{self.id}/rectangles").json()
        return list(map(partial(Rectangle, self.connexion, self.id), r["items"]))

    @exception_handler
    @beartype
    def create_rectangle(
        self, x: int, y: int, w: int, h: int, label: Label
    ) -> Rectangle:
        """Create a rectangle into this annotation.

        Examples:
            ```python
            rect = one_annotation.create_rectangle(420, 69, 100, 10, label_car)
            ```
        """
        payload = {"x": x, "y": y, "w": w, "h": h, "label_id": label.id}
        r = self.connexion.post(
            f"/sdk/annotation/{self.id}/rectangles", data=orjson.dumps(payload)
        ).json()
        return Rectangle(self.connexion, self.id, r)

    @exception_handler
    @beartype
    def create_multiple_rectangles(
        self, rectangles: List[Tuple[int, int, int, int, Label]]
    ) -> List[Rectangle]:
        """Create some rectangles into this annotation.

        Examples:
            ```python
            rects = one_annotation.create_multiple_rectangles([(420, 69, 100, 10, label_car), (123, 456, 20, 20, label_person)])
            ```
        """
        assert len(rectangles) > 0, "Please give at least one rectangle"
        payload = []
        for rectangle in rectangles:
            payload.append(
                {
                    "x": rectangle[0],
                    "y": rectangle[1],
                    "w": rectangle[2],
                    "h": rectangle[3],
                    "label_id": rectangle[4].id,
                }
            )
        r = self.connexion.post(
            f"/sdk/annotation/{self.id}/rectangles", data=orjson.dumps(payload)
        ).json()
        return list(map(partial(Rectangle, self.connexion, self.id), r))

    @exception_handler
    @beartype
    def list_polygons(self) -> List[Polygon]:
        """Retrieve all polygons of this annotation

        Examples:
            ```python
            polys = one_annotation.list_polygons()
            ```
        """
        r = self.connexion.get(f"/sdk/annotation/{self.id}/polygons").json()
        return list(map(partial(Polygon, self.connexion, self.id), r["items"]))

    @exception_handler
    @beartype
    def create_polygon(self, coords: List[List[int]], label: Label) -> Polygon:
        """Create a polygon into this annotation.

        Examples:
            ```python
            poly = one_annotation.create_polygon([[0, 0], [0, 1], [1, 1], [0, 0]], label_car)
            ```
        """
        payload = {"polygon": coords, "label_id": label.id}
        r = self.connexion.post(
            f"/sdk/annotation/{self.id}/polygons", data=orjson.dumps(payload)
        ).json()
        return Polygon(self.connexion, self.id, r)

    @exception_handler
    @beartype
    def create_multiple_polygons(
        self, polygons: List[Tuple[List[List[int]], Label]]
    ) -> List[Polygon]:
        """Create some polygons into this annotation.

        Examples:
            ```python
            polys = one_annotation.create_multiple_polygons([([[0, 0], [0, 1], [1, 1], [0, 0]] label_car), ([[0, 2], [0, 3], [1, 2], [0, 2]] label_person)])
            ```
        """
        assert len(polygons) > 0, "Please give at least one polygon"
        payload = []
        for polygon in polygons:
            payload.append({"polygon": polygon[0], "label_id": polygon[1].id})
        r = self.connexion.post(
            f"/sdk/annotation/{self.id}/polygons", data=orjson.dumps(payload)
        ).json()
        return list(map(partial(Polygon, self.connexion, self.id), r))

    @exception_handler
    @beartype
    def list_lines(self) -> List[Line]:
        """Retrieve all lines of this annotation

        Examples:
            ```python
            lines = one_annotation.list_lines()
            ```
        """
        r = self.connexion.get(f"/sdk/annotation/{self.id}/lines").json()
        return list(map(partial(Line, self.connexion, self.id), r["items"]))

    @exception_handler
    @beartype
    def create_line(self, coords: List[List[int]], label: Label) -> Line:
        """Create a line into this annotation.

        Examples:
            ```python
            line = one_annotation.create_line([[0, 0], [0, 1], [1, 1], [0, 0]], label_car)
            ```
        """
        payload = {"line": coords, "label_id": label.id}
        r = self.connexion.post(
            f"/sdk/annotation/{self.id}/lines", data=orjson.dumps(payload)
        ).json()
        return Line(self.connexion, self.id, r)

    @exception_handler
    @beartype
    def create_multiple_lines(
        self, lines: List[Tuple[List[List[int]], Label]]
    ) -> List[Line]:
        """Create some lines into this annotation.

        Examples:
            ```python
            lines = one_annotation.create_multiple_lines([([[0, 0], [0, 1], [1, 1]] label_car), ([[0, 2], [0, 3], [1, 2]] label_person)])
            ```
        """
        assert len(lines) > 0, "Please give at least one line"
        payload = []
        for line in lines:
            payload.append({"line": line[0], "label_id": line[1].id})
        r = self.connexion.post(
            f"/sdk/annotation/{self.id}/lines", data=orjson.dumps(payload)
        ).json()
        return list(map(partial(Line, self.connexion, self.id), r))

    @exception_handler
    @beartype
    def list_points(self) -> List[Point]:
        """Retrieve all points of this annotation

        Examples:
            ```python
            points = one_annotation.list_points()
            ```
        """
        r = self.connexion.get(f"/sdk/annotation/{self.id}/points").json()
        return list(map(partial(Point, self.connexion, self.id), r["items"]))

    @exception_handler
    @beartype
    def create_point(self, coords: List[int], order: int, label: Label) -> Point:
        """Create a point into this annotation.

        Examples:
            ```python
            poly = one_annotation.create_point([0, 0], 1, label_car)
            ```
        """
        payload = {"point": coords, "order": order, "label_id": label.id}
        r = self.connexion.post(
            f"/sdk/annotation/{self.id}/points", data=orjson.dumps(payload)
        ).json()
        return Point(self.connexion, self.id, r)

    @exception_handler
    @beartype
    def create_multiple_points(
        self, points: List[Tuple[List[int], int, Label]]
    ) -> List[Point]:
        """Create some points into this annotation.

        Examples:
            ```python
            polys = one_annotation.create_multiple_points([([0, 0], label_car), ([0, 2], label_person)])
            ```
        """
        assert len(points) > 0, "Please give at least one point"
        payload = []
        for point in points:
            payload.append(
                {"point": point[0], "order": point[1], "label_id": point[2].id}
            )
        r = self.connexion.post(
            f"/sdk/annotation/{self.id}/points", data=orjson.dumps(payload)
        ).json()
        return list(map(partial(Point, self.connexion, self.id), r))

    @exception_handler
    @beartype
    def list_classifications(self) -> List[Classification]:
        """Retrieve all classifications of this annotation

        Examples:
            ```python
            classifications = one_annotation.list_classifications()
            ```
        """
        r = self.connexion.get(f"/sdk/annotation/{self.id}/classifications").json()
        return list(map(partial(Classification, self.connexion, self.id), r["items"]))

    @exception_handler
    @beartype
    def create_classification(self, label: Label) -> Classification:
        """Create a classification into this annotation.

        Examples:
            ```python
            classifications = one_annotation.create_classification(label_car)
            ```
        """
        payload = {"label_id": label.id}
        r = self.connexion.post(
            f"/sdk/annotation/{self.id}/classifications",
            data=orjson.dumps(payload),
        ).json()
        return Classification(self.connexion, self.id, r)

    @exception_handler
    @beartype
    def create_multiple_classifications(
        self, classifications: List[Label]
    ) -> List[Classification]:
        """Create some classifications into this annotation.

        Examples:
            ```python
            polys = one_annotation.create_multiple_classifications([label_car, label_person])
            ```
        """
        assert len(classifications) > 0, "Please give at least one polygon"
        payload = []
        for classification in classifications:
            payload.append({"label_id": classification.id})
        r = self.connexion.post(
            f"/sdk/annotation/{self.id}/classifications",
            data=orjson.dumps(payload),
        ).json()
        return list(map(partial(Classification, self.connexion, self.id), r))


class MultiAnnotation(MultiObject[Annotation]):
    @beartype
    def __init__(
        self, connexion: Connexion, dataset_version_id: UUID, items: List[Annotation]
    ):
        MultiObject.__init__(self, connexion, items)
        self._dataset_version_id = dataset_version_id

    @property
    def dataset_version_id(self) -> UUID:
        return self._dataset_version_id

    def __str__(self) -> str:
        return f"{Colors.GREEN}MultiAnnotation for dataset version {self.dataset_version_id}{Colors.ENDC}  size: {len(self)}"

    def __getitem__(self, key) -> Union[Annotation, "MultiAnnotation"]:
        if isinstance(key, slice):
            indices = range(*key.indices(len(self.items)))
            annotations = [self.items[i] for i in indices]
            return MultiAnnotation(self.connexion, self.dataset_version_id, annotations)
        return self.items[key]

    @beartype
    def __add__(self, other) -> "MultiAnnotation":
        self.assert_same_connexion(other)
        items = self.items.copy()
        self._add_other_items_to_items(other, items)
        return MultiAnnotation(self.connexion, self.dataset_version_id, items)

    @beartype
    def __iadd__(self, other) -> "MultiAnnotation":
        self.assert_same_connexion(other)
        self._add_other_items_to_items(other, self.items)
        return self

    def _add_other_items_to_items(self, other, items) -> None:
        if isinstance(other, MultiAnnotation):
            if other.dataset_version_id != self.dataset_version_id:
                raise exceptions.BadRequestError(
                    "These annotations does not come from the same dataset"
                )
            items.extend(other.items.copy())
        elif isinstance(other, Annotation):
            if other.dataset_version_id != self.dataset_version_id:
                raise exceptions.BadRequestError(
                    "This annotation does not come from the same dataset"
                )
            items.append(other)
        else:
            raise exceptions.BadRequestError("You can't add these two objects")

    def copy(self) -> "MultiAnnotation":
        return MultiAnnotation(
            self.connexion, self.dataset_version_id, self.items.copy()
        )

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete these annotations and their shape

        :warning: **DANGER ZONE**: Be very careful here!

        Remove these annotations

        Examples:
            ```python
            some_annotations = dataset.list_annotations()[:10]
                some_annotations.delete()
            ```
        """
        payload = {"asset_ids": ["__all__"], "annotation_ids": self.ids}
        self.connexion.delete(
            f"/sdk/dataset/version/{self.dataset_version_id}/annotations",
            data=orjson.dumps(payload),
        )
        logger.info(f"{len(self.items)} annotations deleted.")

    @exception_handler
    @beartype
    def load(
        self,
        chunk_size: int = 1000,
        max_workers: Optional[int] = None,
        skip_error: bool = False,
    ) -> dict:
        """Load these annotation by retrieving shapes with labels, asset_id and worker_id

        Examples:
            ```python
            annotations = foo_dataset.list_annotations()
                annotations_dict = annotations.load()
            ```
        Arguments:
            chunk_size (int, optional): Size of chunk of annotations to load by request. Defaults to 1000.
            max_workers (int, optional): Number of max workers used to load annotations. Defaults to os.cpu_count() + 4.
            skip_error (bool, optional): skip error of a chunk and return partial annotations. Default to False
        """
        if chunk_size < 1 or chunk_size > 10000:
            raise exceptions.BadRequestError(
                "Impossible to load less than 1 or more than 10000 annotations by chunk. Please give another chunk_size"
            )

        return MultiAnnotation.load_annotations_from_ids(
            self.connexion,
            self.dataset_version_id,
            self.ids,
            chunk_size,
            max_workers,
            skip_error,
        )

    @staticmethod
    def load_annotations_from_ids(
        connexion: Connexion,
        dataset_version_id: UUID,
        ids: List[UUID],
        chunk_size: int,
        max_workers: Optional[int] = None,
        skip_error: bool = False,
    ) -> dict:
        def load_some_annotations(list_index: tuple):
            r = connexion.xget(
                f"/sdk/dataset/version/{dataset_version_id}/annotations",
                data=orjson.dumps(list_index[0]),
            )
            return r.json()

        list_chunked = chunk_list(ids, chunk_size)

        results: Dict[int, List[dict]] = mlt.do_mlt_function(
            list_chunked,
            load_some_annotations,
            lambda item: item[1],
            max_workers=max_workers,
        )

        assets: Dict[str, list] = {}
        for key, chunk_annotation in results.items():
            if chunk_annotation is None:
                if skip_error:
                    logging.error(
                        f"Something wrong happened while loading annotations with chunk {key}."
                    )
                    logging.error(
                        "This dataset may not be ready for loading annotations (check its type). Skipping chunk."
                    )
                    continue
                else:
                    raise exceptions.BadRequestError(
                        f"Something wrong happened while loading annotations with chunk {key}."
                        "This dataset may not be ready for loading annotations (check its type)."
                    )

            for annotation in chunk_annotation:
                asset_id = annotation.pop("asset_id")
                if asset_id not in assets:
                    assets[asset_id] = []
                assets[asset_id].append(annotation)

        return assets
