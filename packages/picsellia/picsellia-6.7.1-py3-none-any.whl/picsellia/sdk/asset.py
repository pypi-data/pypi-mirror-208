import logging
import warnings
from functools import partial
from operator import countOf
from pathlib import Path
from typing import List, Optional, Tuple, Union
from uuid import UUID

import orjson
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning

import picsellia.exceptions as exceptions
from picsellia import pxl_multithreading as mlt
from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.sdk.annotation import Annotation
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.data import Data, MultiData
from picsellia.sdk.downloadable import Downloadable
from picsellia.sdk.multi_object import MultiObject
from picsellia.sdk.tag import Tag
from picsellia.sdk.taggable import Taggable
from picsellia.sdk.worker import Worker
from picsellia.types.enums import DataType, TagTarget
from picsellia.types.schemas import AssetSchema, ImageMetaSchema, ImageSchema

logger = logging.getLogger("picsellia")
warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


class Asset(Dao, Downloadable, Taggable):
    def __init__(self, connexion: Connexion, dataset_version_id: UUID, data: dict):
        Dao.__init__(self, connexion, data)
        Downloadable.__init__(self)
        Taggable.__init__(self, TagTarget.ASSET)
        self._dataset_version_id = dataset_version_id

    @property
    def dataset_version_id(self) -> UUID:
        """UUID of (DatasetVersion) where this (Asset) is"""
        return self._dataset_version_id

    @property
    def data_id(self) -> UUID:
        """UUID of (Data) of this (Asset)"""
        return self._data_id

    @property
    def object_name(self) -> str:
        """Object name of this (Asset)"""
        return self._object_name

    @property
    def filename(self) -> str:
        """Filename of this (Asset)"""
        return self._filename

    @property
    def large(self) -> bool:
        """If true, this (Asset) file is considered large"""
        return True

    @property
    def type(self) -> DataType:
        """Type of this (Asset)"""
        return self._type

    @property
    def width(self) -> int:
        """Width of this (Asset) if this is an Image."""
        if self.type == DataType.IMAGE:
            return self._width
        else:
            return 0

    @property
    def height(self) -> int:
        """Height of this (Asset) if this is an Image."""
        if self.type == DataType.IMAGE:
            return self._height
        else:
            return 0

    @property
    def duration(self) -> int:
        """Duration of this (Asset) if this is a Video."""
        if self.type == DataType.VIDEO:
            return self._duration
        else:
            return 0

    def __str__(self):
        return f"{Colors.YELLOW}Asset '{self.filename}' ({self.type}) {Colors.ENDC} (id: {self.id})"

    @exception_handler
    @beartype
    def refresh(self, data: dict) -> AssetSchema:
        schema = AssetSchema(**data)
        self._data_id = schema.data.id

        # Downloadable properties
        self._object_name = schema.data.object_name
        self._filename = schema.data.filename
        self._url = schema.data.url

        self._type = schema.data.type
        if self._type == DataType.IMAGE:
            self._height = schema.data.meta.height
            self._width = schema.data.meta.width
        elif self._type == DataType.VIDEO:
            self._duration = schema.data.meta.duration
        return schema

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/asset/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def reset_url(self) -> str:
        """Reset url property of this Asset by calling platform.

        Returns:
            A url as str of this Asset.
        """
        self.sync()
        return self._url

    @exception_handler
    @beartype
    def to_data_schema(self) -> ImageSchema:
        if self.type != DataType.IMAGE:  # pragma: no cover
            raise NotImplementedError()

        return ImageSchema(
            id=self.data_id,
            object_name=self.object_name,
            filename=self.filename,
            type=self.type,
            url=self._url,
            meta=ImageMetaSchema(height=self.height, width=self.width),
        )

    @exception_handler
    @beartype
    def get_tags(self) -> List[Tag]:
        """Retrieve the tags of your asset.

        Examples:
            ```python
            tags = asset.get_tags()
            assert tags[0].name == "bicycle"
            ```

        Returns:
            List of tags as Tag
        """
        r = self.sync()
        return list(map(partial(Tag, self.connexion), r["tags"]))

    @exception_handler
    @beartype
    def get_data(self):
        """Retrieve data of this asset

            ```python
            data = asset.get_data()
            assert data.id == asset.data_id
            assert data.filename == asset.filename
            ```

        Returns:
            A (Data) object
        """
        r = self.connexion.get(f"/sdk/data/{self.data_id}").json()
        return Data(self.connexion, UUID(r["datalake_id"]), r)

    @exception_handler
    @beartype
    def get_data_tags(self) -> List[Tag]:
        """Retrieve data tag of this asset

            ```python
            tags = asset.get_data_tags()
            assert tags[0].name == "bicycle"
            ```

        Returns:
            List of tags as Tag
        """
        r = self.connexion.get(f"/sdk/data/{self.data_id}").json()
        return list(map(partial(Tag, self.connexion), r["tags"]))

    @exception_handler
    @beartype
    def get_annotation(self, worker: Optional[Worker] = None) -> Annotation:
        """Retrieve the annotation of this asset by the given worker (if none given, it is the current user)

        Examples:
            ```python
            some_annotation = one_asset.get_annotation(my_worker)
            my_annotation = one_asset.get_annotation()
            assert some_annotation == my_annotation
            ```

        Returns:
            An object (Annotation)
        """
        params = {}
        if worker is not None:
            params["worker_id"] = worker.id
        r = self.connexion.get(
            f"/sdk/asset/{self.id}/annotations/find", params=params
        ).json()
        return Annotation(self.connexion, self.dataset_version_id, self.id, r)

    @exception_handler
    @beartype
    def create_annotation(
        self, duration: Union[float, int] = 0.0, worker: Optional[Worker] = None
    ) -> Annotation:
        """Create an annotation on this asset

        Examples:
            ```python
            some_annotation = one_asset.create_annotation(0.120, my_worker_1)
            ```

        Returns:
            An object (Annotation)
        """
        payload = {
            "duration": float(duration),
        }
        if worker is not None:
            payload["worker_id"] = worker.id
        r = self.connexion.post(
            f"/sdk/asset/{self.id}/annotations", data=orjson.dumps(payload)
        ).json()
        return Annotation(self.connexion, self.dataset_version_id, self.id, r)

    @exception_handler
    @beartype
    def list_annotations(self) -> List[Annotation]:
        """List all annotation of an asset

        Examples:
            ```python
            annotations = one_asset.list_annotations()
            ```

        Returns:
            A list of (Annotation)
        """
        r = self.connexion.get(f"/sdk/asset/{self.id}/annotations").json()
        return list(
            map(
                partial(Annotation, self.connexion, self.dataset_version_id, self.id),
                r["items"],
            )
        )

    @exception_handler
    @beartype
    def delete_annotations(self, workers: Optional[List[Worker]] = None) -> None:
        """Delete all annotations of an asset: it will erase every shape of every annotation.

        You can give workers on which it will be effectively erased.

        :warning: **DANGER ZONE**: Be careful here !

        Examples:
            ```python
            one_asset.delete_annotations()
            ```
        """
        payload = {"asset_ids": [self.id]}
        if workers is not None:
            payload["worker_ids"] = [worker.id for worker in workers]

        self.connexion.delete(
            f"/sdk/dataset/version/{self.dataset_version_id}/annotations",
            data=orjson.dumps(payload),
        )
        logger.info(f"All annotations of {self} were removed.")

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete this asset from its dataset

        :warning: **DANGER ZONE**: Be very careful here!

        Remove this asset and its annotation from the dataset it belongs

        Examples:
            ```python
            one_asset.delete()
            ```
        """
        self.connexion.delete(f"/sdk/asset/{self.id}")
        logger.info(f"{self} removed from dataset")


class MultiAsset(MultiObject[Asset], Taggable):
    @beartype
    def __init__(
        self, connexion: Connexion, dataset_version_id: UUID, items: List[Asset]
    ):
        MultiObject.__init__(self, connexion, items)
        Taggable.__init__(self, TagTarget.ASSET)
        self.dataset_version_id = dataset_version_id

    def __str__(self) -> str:
        return f"{Colors.GREEN}MultiAsset for dataset version {self.dataset_version_id} {Colors.ENDC}, size: {len(self)}"

    def __getitem__(self, key) -> Union[Asset, "MultiAsset"]:
        if isinstance(key, slice):
            indices = range(*key.indices(len(self.items)))
            assets = [self.items[i] for i in indices]
            return MultiAsset(self.connexion, self.dataset_version_id, assets)
        return self.items[key]

    @beartype
    def __add__(self, other) -> "MultiAsset":
        self.assert_same_connexion(other)
        items = self.items.copy()
        if isinstance(other, MultiAsset):
            items.extend(other.items.copy())
        elif isinstance(other, Asset):
            items.append(other)
        else:
            raise exceptions.BadRequestError("You can't add these two objects")

        return MultiAsset(self.connexion, self.dataset_version_id, items)

    @beartype
    def __iadd__(self, other) -> "MultiAsset":
        self.assert_same_connexion(other)

        if isinstance(other, MultiAsset):
            self.extend(other.items.copy())
        elif isinstance(other, Asset):
            self.append(other)
        else:
            raise exceptions.BadRequestError("You can't add these two objects")

        return self

    def copy(self) -> "MultiAsset":
        return MultiAsset(self.connexion, self.dataset_version_id, self.items.copy())

    @exception_handler
    @beartype
    def split(self, ratio: float) -> Tuple["MultiAsset", "MultiAsset"]:
        s = round(ratio * len(self.items))
        return MultiAsset(
            self.connexion, self.dataset_version_id, self.items[:s]
        ), MultiAsset(self.connexion, self.dataset_version_id, self.items[s:])

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete assets from their dataset

        :warning: **DANGER ZONE**: Be very careful here!

        Remove these assets and its annotation from the dataset it belongs

        Examples:
            ```python
            some_assets = dataset.list_assets()[:10]
            some_assets.delete()
            ```
        """
        payload = self.ids
        self.connexion.delete(
            f"/sdk/dataset/version/{self.dataset_version_id}/assets",
            data=orjson.dumps(payload),
        )
        logger.info(f"{len(self.items)} assets removed from {self}")

    @exception_handler
    @beartype
    def download(
        self,
        target_path: Union[str, Path] = "./",
        force_replace: bool = False,
        max_workers: Optional[int] = None,
    ) -> None:
        """Download this multi asset in given target path


        Examples:
            ```python
            bunch_of_assets = client.get_dataset("foo_dataset").get_version("first").list_assets()
            bunch_of_assets.download('./downloads/')
            ```
        Arguments:
            target_path (str or Path, optional): Target path where to download. Defaults to './'.
            max_workers (int, optional): Number of max workers used to download. Defaults to os.cpu_count() + 4.
            force_replace: (bool, optional): Replace an existing file if exists. Defaults to False.
        """

        def download_one_data(item: Asset):
            return item._do_download(target_path, force_replace)

        results = mlt.do_mlt_function(
            self.items, download_one_data, lambda item: item.id, max_workers=max_workers
        )
        downloaded = countOf(results.values(), True)

        logger.info(
            f"{downloaded} assets downloaded (over {len(results)}) in directory {target_path}"
        )

    @exception_handler
    @beartype
    def delete_annotations(self, workers: Optional[List[Worker]] = None) -> None:
        """Delete all annotations of all these assets: it will erase every shape of every annotation of every asset.

        You can give workers on which it will be effectively erased.

        :warning: **DANGER ZONE**: Be careful here !

        Examples:
            ```python
            multiple_assets.delete_annotations(workers=)
            ```
        """
        payload = {"asset_ids": self.ids}
        if workers is not None:
            payload["worker_ids"] = [worker.id for worker in workers]

        self.connexion.delete(
            f"/sdk/dataset/version/{self.dataset_version_id}/annotations",
            data=orjson.dumps(payload),
        )
        logger.info(f"All annotations of {len(self)} assets were removed.")

    @exception_handler
    @beartype
    def as_list_of_data(self) -> List[Data]:
        """
            Convert a MultiAsset into a List of Data. Assets can come from different Datalake.
            This is slower than calling .as_multidata(), so if you know that all your data are coming
            from the same datalake, you should call .as_multidata instead

        Returns:
            a list of (Data) object
        """
        if not self.items:  # pragma: no cover
            raise exceptions.NoDataError("There is no data into this MultiAsset")

        return [asset.get_data() for asset in self.items]

    @exception_handler
    @beartype
    def as_multidata(self, force_refresh: bool = True) -> MultiData:
        """
            Convert a MultiAsset into a MultiData.
            Assets must all be in the same datalake to be retrieved.
            In case of a dataset with multiple datalake source, you can use .as_list_of_data() that will return a list of data but slower

        Args:
            force_refresh (bool, optional): when False, will not refresh data by calling platform.

        Returns:
            a (MultiData) object
        """
        if not self.items:  # pragma: no cover
            raise exceptions.NoDataError("There is no data into this MultiAsset")

        if force_refresh:
            data_list = self._retrieve_all_data_with_refresh()
        else:
            data_list = self._retrieve_all_data_without_refresh()
        return MultiData(self.connexion, data_list[0].datalake_id, data_list)

    def _retrieve_all_data_with_refresh(self):
        def _do_list_data_of_datalake(
            datalake_id: UUID,
            ids: List[UUID],
            limit: int,
            offset: int,
        ) -> Tuple[List[Data], int]:
            data = {"limit": limit, "offset": offset, "ids": ids}
            r = self.connexion.xget(
                f"/sdk/datalake/{datalake_id}/datas", data=orjson.dumps(data)
            ).json()
            return (
                list(map(partial(Data, self.connexion, datalake_id), r["items"])),
                r["count"],
            )

        first_data = self.items[0].get_data()
        if len(self.items) == 1:
            return [first_data]

        return mlt.do_paginate(
            limit=None,
            offset=None,
            page_size=None,
            f=partial(
                _do_list_data_of_datalake,
                first_data.datalake_id,
                [asset.data_id for asset in self.items],
            ),
        )

    def _retrieve_all_data_without_refresh(self):
        first_data = self.items[0].get_data()
        return [
            Data(
                self.connexion,
                first_data.datalake_id,
                data=asset.to_data_schema().dict(),
            )
            for asset in self.items
        ]
