import logging
import warnings
from functools import partial
from typing import List, Optional, Union
from uuid import UUID

import orjson
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning

from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.dataset_version import DatasetVersion
from picsellia.sdk.tag import Tag, TagTarget
from picsellia.sdk.taggable import Taggable
from picsellia.sdk.worker import Worker
from picsellia.types.enums import InferenceType
from picsellia.types.schemas import DatasetSchema
from picsellia.utils import filter_payload

warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)
logger = logging.getLogger("picsellia")


class Dataset(Dao, Taggable):
    def __init__(self, connexion: Connexion, data: dict):
        Dao.__init__(self, connexion, data)
        Taggable.__init__(self, TagTarget.DATASET)

    @property
    def name(self) -> str:
        """Name of this (Dataset)"""
        return self._name

    def __str__(self):
        return f"{Colors.YELLOW}Dataset {self.name} {Colors.ENDC} (id: {self.id})"

    @exception_handler
    @beartype
    def refresh(self, data: dict):
        schema = DatasetSchema(**data)
        self._name = schema.name
        return schema

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/dataset/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def get_tags(self) -> List[Tag]:
        """Retrieve the tags of your dataset.

        Examples:
            ```python
            tags = foo_dataset.get_tags()
            assert tags[0].name == "my-dataset-1"
            ```

        Returns:
            List of tags as Tag
        """
        r = self.sync()
        return list(map(partial(Tag, self.connexion), r["tags"]))

    @exception_handler
    @beartype
    def get_resource_url_on_platform(self) -> str:
        """Get platform url of this resource.

        Examples:
            ```python
            print(foo_dataset.get_resource_url_on_platform())
            >>> "https://app.picsellia.com/dataset/62cffb84-b92c-450c-bc37-8c4dd4d0f590"
            ```

        Returns:
            Url on Platform for this resource
        """

        return f"{self.connexion.host}/dataset/{self.id}"

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete a dataset.

        :warning: **DANGER ZONE**: Be very careful here!

        It will remove this dataset from our database, its versions with their assets and annotations will be removed.

        Examples:
            ```python
            foo_dataset.delete()
            ```
        """
        self.connexion.delete(f"/sdk/dataset/{self.id}")
        logger.info(f"{self} deleted")

    @exception_handler
    @beartype
    def update(
        self,
        name: Optional[str] = None,
        private: Optional[bool] = None,
        description: Optional[str] = None,
    ) -> None:
        """Update name, private or description of this Dataset.

        Examples:
            ```python
            dataset.update(description='My favourite dataset')
            ```
        """
        payload = {"name": name, "private": private, "description": description}
        filtered_payload = filter_payload(payload)
        r = self.connexion.patch(
            f"/sdk/dataset/{self.id}", data=orjson.dumps(filtered_payload)
        ).json()
        self.refresh(r)
        logger.info(f"{self} updated")

    @exception_handler
    @beartype
    def list_versions(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
    ) -> List[DatasetVersion]:
        """List all versions of this dataset

        Examples:
            ```python
            dataset.list_versions()
            ```
        """
        params = {"limit": limit, "offset": offset, "order_by": order_by}
        params = filter_payload(params)
        r = self.connexion.get(f"/sdk/dataset/{self.id}/versions", params=params).json()
        return list(map(partial(DatasetVersion, self.connexion), r["items"]))

    @exception_handler
    @beartype
    def get_version(self, version: str) -> DatasetVersion:
        """Retrieve one version of a dataset

        Examples:
            ```python
            my_dataset_version = my_dataset.get_version("first")
            ```
        """
        params = {"version": version}
        r = self.connexion.get(
            f"/sdk/dataset/{self.id}/versions/find", params=params
        ).json()
        return DatasetVersion(self.connexion, r)

    @exception_handler
    @beartype
    def get_version_by_id(self, id: Union[UUID, str]) -> DatasetVersion:
        """Retrieve one version of a dataset

        Examples:
            ```python
            my_dataset_version = my_dataset.get_version("first")
            ```
        """
        if isinstance(id, str):
            id = UUID(id)
        params = {"id": id}
        r = self.connexion.get(
            f"/sdk/dataset/{self.id}/versions/find", params=params
        ).json()
        return DatasetVersion(self.connexion, r)

    @exception_handler
    @beartype
    def create_version(
        self,
        version: str,
        description: str = "",
        type: Union[InferenceType, str] = InferenceType.NOT_CONFIGURED,
    ) -> DatasetVersion:
        """Create a version of this dataset.

        A versioned dataset (DatasetVersion) takes (Data) from (Datalake) and transform it as annotable (Asset).

        Examples:
            ```python
            foo_dataset = client.create_dataset('foo_dataset')
            foo_dataset_version_1 = foo_dataset.create_version('first')
            some_data = client.get_datalake().list_data(limit=10)
            foo_dataset_version_1.add_data(some_data)
            ```

        Returns:
            A (DatasetVersion) manipulable that can receive data
        """
        payload = {
            "version": version,
            "description": description,
            "type": InferenceType.validate(type),
        }

        r = self.connexion.post(
            f"/sdk/dataset/{self.id}/versions", data=orjson.dumps(payload)
        ).json()
        return DatasetVersion(self.connexion, r)

    @exception_handler
    @beartype
    def list_workers(self) -> List[Worker]:
        """List all workers of this dataset

        Examples:
            ```python
            dataset.list_workers()
            ```
        """
        r = self.connexion.get(f"/sdk/dataset/{self.id}/workers").json()
        return list(map(partial(Worker, self.connexion), r["items"]))

    @exception_handler
    @beartype
    def find_worker(self, username: str) -> Worker:
        """Find worker of this dataset from its username"""
        params = {"username": username}
        r = self.connexion.get(
            f"/sdk/dataset/{self.id}/workers/find", params=params
        ).json()
        return Worker(self.connexion, r)
