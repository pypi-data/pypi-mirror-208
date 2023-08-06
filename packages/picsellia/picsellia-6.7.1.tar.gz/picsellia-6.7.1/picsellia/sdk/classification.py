import logging
import warnings
from uuid import UUID

import orjson
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning

from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.label import Label
from picsellia.types.schemas import ClassificationSchema

logger = logging.getLogger("picsellia")
warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


class Classification(Dao):
    def __init__(self, connexion: Connexion, annotation_id: UUID, data: dict) -> None:
        Dao.__init__(self, connexion, data)
        self._annotation_id = annotation_id

    @property
    def annotation_id(self) -> UUID:
        """UUID of (Annotation) holding this (Classification)"""
        return self._annotation_id

    @property
    def label(self) -> Label:
        """(Label) of this (Classification)"""
        return self._label

    def __str__(self):
        return f"{Colors.BLUE}Classification with label {self.label.name} on annotation {self.annotation_id} {Colors.ENDC} (id: {self.id})"

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/classification/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def refresh(self, data: dict) -> ClassificationSchema:
        schema = ClassificationSchema(**data)
        self._label = Label(self.connexion, schema.label.dict())
        return schema

    @exception_handler
    @beartype
    def update(
        self,
        label: Label,
    ) -> None:
        """Update this classification with another label.

        Examples:
            ```python
            classification.update(label=label_plane)
            ```
        """
        payload = {"label_id": label.id}
        r = self.connexion.patch(
            f"/sdk/classification/{self.id}", data=orjson.dumps(payload)
        ).json()
        self.refresh(r)
        logger.info(f"{self} updated")

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete this classification from the platform.

        :warning: **DANGER ZONE**: Be very careful here!

        Examples:
            ```python
            classification.delete()
            ```
        """
        self.connexion.delete(f"/sdk/classification/{self.id}")
        logger.info(f"{self} deleted.")
