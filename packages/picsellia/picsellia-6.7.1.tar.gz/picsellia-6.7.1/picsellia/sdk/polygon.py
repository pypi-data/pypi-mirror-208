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
from picsellia.types.schemas import PolygonSchema

logger = logging.getLogger("picsellia")
warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


class Polygon(Dao):
    def __init__(self, connexion: Connexion, annotation_id: UUID, data: dict) -> None:
        Dao.__init__(self, connexion, data)
        self._annotation_id = annotation_id

    @property
    def annotation_id(self) -> UUID:
        """UUID of the (Annotation) holding this (Polygon)"""
        return self._annotation_id

    @property
    def coords(self) -> List[List[int]]:
        """Coords of this (Polygon)"""
        return self._coords

    @property
    def label(self) -> Label:
        """Label of this (Polygon)"""
        return self._label

    def __str__(self):
        return f"{Colors.BLUE}Polygon ({len(self.coords)} points) with label {self.label.name} on annotation {self.annotation_id} {Colors.ENDC} (id: {self.id})"

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/polygon/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def refresh(self, data: dict) -> PolygonSchema:
        schema = PolygonSchema(**data)
        self._coords = schema.coords
        self._label = Label(self.connexion, schema.label.dict())
        return schema

    @exception_handler
    @beartype
    def update(
        self,
        coords: Optional[List] = None,
        label: Optional[Label] = None,
    ) -> None:
        """Update this polygon with new coords or new label.

        Examples:
            ```python
            poly.update(coords=[[0, 0], [0, 1], [1, 1], [0, 0]])
            ```
        """
        payload = {}
        if coords is not None:
            payload["polygon"] = coords
        if label is not None:
            payload["label_id"] = label.id
        assert payload != {}, "You can't update this polygon with no data to update"
        r = self.connexion.patch(
            f"/sdk/polygon/{self.id}", data=orjson.dumps(payload)
        ).json()
        self.refresh(r)
        logger.info(f"{self} updated")

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete this polygon from the platform.

        :warning: **DANGER ZONE**: Be very careful here!

        Examples:
            ```python
            poly.delete()
            ```
        """
        self.connexion.delete(f"/sdk/polygon/{self.id}")
        logger.info(f"{self} deleted.")
