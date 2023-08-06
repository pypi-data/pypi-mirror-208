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

from picsellia import exceptions as exceptions
from picsellia import pxl_multithreading as mlt
from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.multi_object import MultiObject
from picsellia.sdk.tag import Tag, TagTarget
from picsellia.sdk.taggable import Taggable
from picsellia.types.enums import DataType
from picsellia.types.schemas import DataSchema, ImageSchema, VideoSchema

from .dao import Dao
from .datasource import DataSource
from .downloadable import Downloadable

logger = logging.getLogger("picsellia")
warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


class Data(Dao, Downloadable, Taggable):
    def __init__(self, connexion: Connexion, datalake_id: UUID, data: dict):
        Dao.__init__(self, connexion, data)
        Downloadable.__init__(self)
        Taggable.__init__(self, TagTarget.DATA)
        self._datalake_id = datalake_id

    def __str__(self):
        return f"{Colors.GREEN}Data{Colors.ENDC} object (id: {self.id})"

    @property
    def datalake_id(self) -> UUID:
        """UUID of (Datalake) where this (Data) is"""
        return self._datalake_id

    @property
    def object_name(self) -> str:
        """Object name of this (Data)"""
        return self._object_name

    @property
    def filename(self) -> str:
        """Filename of this (Data)"""
        return self._filename

    @property
    def large(self) -> bool:
        """If true, this (Data) file is considered large"""
        return True

    @property
    def type(self) -> DataType:
        """Type of this (Data)"""
        return self._type

    @property
    def width(self) -> int:
        """Width of this (Data)"""
        if self.type == DataType.IMAGE:
            return self._width
        else:
            return 0

    @property
    def height(self) -> int:
        """Height of this (Data) if this is an Image."""
        if self.type == DataType.IMAGE:
            return self._height
        else:
            return 0

    @property
    def duration(self) -> int:
        """Duration of this (Data) if this is a Video."""
        if self.type == DataType.VIDEO:
            return self._duration
        else:
            return 0

    @exception_handler
    @beartype
    def refresh(self, data: dict):
        data_type = data["type"]
        if data_type in [DataType.IMAGE, DataType.IMAGE.value]:
            schema = ImageSchema(**data)
        elif data_type in [DataType.VIDEO, DataType.VIDEO.value]:
            schema = VideoSchema(**data)
        else:
            schema = DataSchema(**data)

        # Downloadable properties
        self._object_name = schema.object_name
        self._filename = schema.filename
        self._url = schema.url

        self._type = schema.type
        if schema.type == DataType.IMAGE:
            self._height = schema.meta.height
            self._width = schema.meta.width
        elif schema.type == DataType.VIDEO:
            self._duration = schema.meta.duration

        return schema

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/data/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def reset_url(self) -> str:
        """Reset url property of this Data by calling platform.

        Returns:
            A url as a string of this Data.
        """
        self.sync()
        return self._url

    @exception_handler
    @beartype
    def get_tags(self) -> List[Tag]:
        """Retrieve the tags of your data.

        Examples:
            ```python
            tags = data.get_tags()
            assert tags[0].name == "bicycle"
            ```

        Returns:
            List of tags as Tag
        """
        r = self.sync()
        return list(map(partial(Tag, self.connexion), r["tags"]))

    @exception_handler
    @beartype
    def get_datasource(self) -> Optional[DataSource]:
        """Retrieve (DataSource) of this Data if it exists. Else, will return None.

        Returns:
            A (DataSource) object or None.
        """
        r = self.sync()
        if "data_source" not in r or r["data_source"] is None:
            return None

        return DataSource(self.connexion, r["data_source"])

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete data and remove it from datalake.

        :warning: **DANGER ZONE**: Be very careful here!

        Remove this data from datalake, and all assets linked to this data.

        Examples:
            ```python
            data.delete()
            ```
        """
        response = self.connexion.delete(f"/sdk/data/{self.id}")
        assert response.status_code == 204
        logger.info(f"1 data (id: {self.id}) deleted from datalake {self.datalake_id}.")


class MultiData(MultiObject[Data], Taggable):
    @beartype
    def __init__(self, connexion: Connexion, datalake_id: UUID, items: List[Data]):
        MultiObject.__init__(self, connexion, items)
        Taggable.__init__(self, TagTarget.DATA)
        self.datalake_id = datalake_id

    def __str__(self) -> str:
        return f"{Colors.GREEN}MultiData for datalake {self.datalake_id} {Colors.ENDC}, size: {len(self)}"

    def __getitem__(self, key) -> Union[Data, "MultiData"]:
        if isinstance(key, slice):
            indices = range(*key.indices(len(self.items)))
            data = [self.items[i] for i in indices]
            return MultiData(self.connexion, self.datalake_id, data)
        return self.items[key]

    @beartype
    def __add__(self, other) -> "MultiData":
        self.assert_same_connexion(other)
        items = self.items.copy()
        if isinstance(other, MultiData):
            items.extend(other.items.copy())
        elif isinstance(other, Data):
            items.append(other)
        else:
            raise exceptions.BadRequestError("You can't add these two objects")

        return MultiData(self.connexion, self.datalake_id, items)

    @beartype
    def __iadd__(self, other) -> "MultiData":
        self.assert_same_connexion(other)

        if isinstance(other, MultiData):
            self.extend(other.items.copy())
        elif isinstance(other, Data):
            self.append(other)
        else:
            raise exceptions.BadRequestError("You can't add these two objects")

        return self

    def copy(self) -> "MultiData":
        return MultiData(self.connexion, self.datalake_id, self.items.copy())

    @exception_handler
    @beartype
    def split(self, ratio: float) -> Tuple["MultiData", "MultiData"]:
        s = round(ratio * len(self.items))
        return MultiData(self.connexion, self.datalake_id, self.items[:s]), MultiData(
            self.connexion, self.datalake_id, self.items[s:]
        )

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete a bunch of data and remove them from datalake.

        :warning: **DANGER ZONE**: Be very careful here!

        Remove a bunch of data from datalake, and all assets linked to each data.

        Examples:
            ```python
            whole_data = datalake.list_data(limit=3)
            whole_data.delete()
            ```
        """
        payload = self.ids
        self.connexion.delete(
            f"/sdk/datalake/{self.datalake_id}/datas",
            data=orjson.dumps(payload),
        )
        logger.info(f"{len(self.items)} data deleted from datalake {self.datalake_id}.")

    @exception_handler
    @beartype
    def download(
        self,
        target_path: Union[str, Path] = "./",
        force_replace: bool = False,
        max_workers: Optional[int] = None,
    ) -> None:
        """Download this multi data in given target path


        Examples:
            ```python
            bunch_of_data = client.get_datalake().list_data(limit=25)
            bunch_of_data.download('./downloads/')
            ```
        Arguments:
            target_path (str or Path, optional): Target path where to download. Defaults to './'.
            force_replace: (bool, optional): Replace an existing file if exists. Defaults to False.
            max_workers (int, optional): Number of max workers used to download. Defaults to os.cpu_count() + 4.
        """

        def download_one_data(item: Data):
            return item._do_download(target_path, force_replace)

        results = mlt.do_mlt_function(
            self.items, download_one_data, lambda item: item.id, max_workers=max_workers
        )
        downloaded = countOf(results.values(), True)

        logger.info(
            f"{downloaded} data downloaded (over {len(results)}) in directory {target_path}"
        )
