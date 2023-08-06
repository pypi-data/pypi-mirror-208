import logging
import warnings
from typing import List, Optional
from uuid import UUID

import orjson
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning

from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.label import Label
from picsellia.types.schemas import PointSchema

logger = logging.getLogger("picsellia")
warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


class Point(Dao):
    def __init__(self, connexion: Connexion, annotation_id: UUID, data: dict) -> None:
        Dao.__init__(self, connexion, data)
        self._annotation_id = annotation_id

    @property
    def annotation_id(self) -> UUID:
        """UUID of the (Annotation) holding this (Point)"""
        return self._annotation_id

    @property
    def coords(self) -> List[List[int]]:
        """Coords of this (Point)"""
        return self._coords

    @property
    def order(self) -> int:
        """Order of this (Point)"""
        return self._order

    @property
    def label(self) -> Label:
        """(Label) of this (Point)"""
        return self._label

    def __str__(self):
        return f"{Colors.BLUE}Point ({self.coords}, order: {self.order}) with label {self.label.name} on annotation {self.annotation_id} {Colors.ENDC} (id: {self.id})"

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/point/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def refresh(self, data: dict) -> PointSchema:
        schema = PointSchema(**data)
        self._coords = schema.coords
        self._order = schema.order
        self._label = Label(self.connexion, schema.label.dict())
        return schema

    @exception_handler
    @beartype
    def update(
        self,
        coords: Optional[List] = None,
        label: Optional[Label] = None,
    ) -> None:
        """Update this point with new coords or new label.

        Examples:
            ```python
            point.update(coords=[0, 0])
            ```
        """
        payload = {}
        if coords is not None:
            payload["point"] = coords
        if label is not None:
            payload["label_id"] = label.id
        assert payload != {}, "You can't update this point with no data to update"
        r = self.connexion.patch(
            f"/sdk/point/{self.id}", data=orjson.dumps(payload)
        ).json()
        self.refresh(r)
        logger.info(f"{self} updated")

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete this point from the platform.

        :warning: **DANGER ZONE**: Be very careful here!

        Examples:
            ```python
            point.delete()
            ```
        """
        self.connexion.delete(f"/sdk/point/{self.id}")
        logger.info(f"{self} deleted.")
