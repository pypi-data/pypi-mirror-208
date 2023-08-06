import logging
import warnings
from typing import Optional

import orjson
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning

from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.downloadable import Downloadable
from picsellia.types.schemas import ScanFileSchema
from picsellia.utils import filter_payload

logger = logging.getLogger("picsellia")
warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


class ScanFile(Dao, Downloadable):
    def __init__(self, connexion: Connexion, data: dict):
        Dao.__init__(self, connexion, data)
        Downloadable.__init__(self)

    def __str__(self):
        return f"{Colors.GREEN}ScanFile {self.name}{Colors.ENDC} (id: {self.id})"

    @property
    def name(self) -> str:
        """Name of this (ScanFile)"""
        return self._name

    @property
    def object_name(self) -> str:
        """Object name of this (ScanFile)"""
        return self._object_name

    @property
    def large(self) -> bool:
        """If True, this (ScanFile) is considered large"""
        return self._large

    @property
    def filename(self) -> str:
        """Filename of this (ScanFile)"""
        return self._name

    @exception_handler
    @beartype
    def refresh(self, data: dict) -> ScanFileSchema:
        schema = ScanFileSchema(**data)
        self._name = schema.name
        self._object_name = schema.object_name
        self._large = schema.large
        self._url = schema.url
        return schema

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/scan/file/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def reset_url(self) -> str:
        """Reset url property of this ScanFile by calling platform.

        Returns:
            A url as a string of this ScanFile.
        """
        self._url = self.connexion.init_download(self.object_name)
        return self._url

    @exception_handler
    @beartype
    def update(
        self,
        name: Optional[str] = None,
        object_name: Optional[str] = None,
        large: Optional[bool] = None,
    ) -> None:
        """Update this scan file.

        Examples:
            ```python
            script.update(object_name="another-path-to-script")
            ```
        """
        payload = {
            "name": name,
            "object_name": object_name,
            "large": large,
        }
        filtered_payload = filter_payload(payload)
        r = self.connexion.patch(
            f"/sdk/scan/file/{self.id}", data=orjson.dumps(filtered_payload)
        ).json()
        self.refresh(r)

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete this scan file

        Examples:
            ```python
            script.delete()
            ```
        """
        self.connexion.delete(f"/sdk/scan/file/{self.id}")
