import logging
import os
import warnings
from functools import partial
from pathlib import Path
from typing import List, Optional, Tuple, Union
from uuid import UUID

import orjson
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from deprecation import deprecated
from PIL import Image

import picsellia.pxl_multithreading as mlt
from picsellia import exceptions
from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.exceptions import (
    NoConnectorFound,
    NoDataError,
    NothingDoneError,
    UploadError,
)
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.data import Data, MultiData
from picsellia.sdk.datasource import DataSource
from picsellia.sdk.tag import Tag
from picsellia.services.datasource import DataSourceService
from picsellia.services.error_manager import ErrorManager
from picsellia.types.enums import DataType, TagTarget
from picsellia.types.schemas import DatalakeSchema
from picsellia.utils import (
    combine_two_ql,
    convert_tag_list_to_query_language,
    filter_payload,
    get_image_shape_with_exif_transpose,
)

logger = logging.getLogger("picsellia")
warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


class Datalake(Dao):
    def __init__(self, connexion: Connexion, organization_id: UUID, data: dict):
        Dao.__init__(self, connexion, data)
        self._organization_id = organization_id

    def __str__(self):
        return f"{Colors.GREEN}Datalake '{self.name}'{Colors.ENDC} (id: {self.id})"

    @property
    def name(self) -> str:
        """Name of this (Datalake)"""
        return self._name

    @property
    def connector_id(self) -> UUID:
        """Connector id used by this (Datalake)"""
        if self._connector_id is None:
            raise NoConnectorFound(
                "This datalake has no connector. You cannot retrieve and upload data into this datalake."
            )
        return self._connector_id

    @exception_handler
    @beartype
    def refresh(self, data: dict):
        schema = DatalakeSchema(**data)
        self._name = schema.name
        if schema.connector_id is not None:
            self._connector_id = schema.connector_id
        return schema

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/datalake/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def get_resource_url_on_platform(self) -> str:
        """Get platform url of this resource.

        Examples:
            ```python
            print(foo_dataset.get_resource_url_on_platform())
            >>> "https://app.picsellia.com/datalake/62cffb84-b92c-450c-bc37-8c4dd4d0f590"
            ```

        Returns:
            Url on Platform for this resource
        """

        return f"{self.connexion.host}/datalake/{self.id}"

    @exception_handler
    @beartype
    def upload_data(
        self,
        filepaths: Union[str, Path, List[Union[str, Path]]],
        tags: Optional[List[Union[str, Tag]]] = None,
        source: Union[str, DataSource, None] = None,
        max_workers: Optional[int] = None,
        error_manager: Optional[ErrorManager] = None,
    ) -> Union[Data, MultiData]:
        """Upload data into this datalake.

        Upload files representing data, into a datalake.
        You can give some tags as a list.
        You can give a source for your data.

        If some data fails to upload, check the example to see how
        to retrieve the list of file paths that failed.

        Examples:
            ```python
            tag_car = client.get_data_tag("car")
            tag_huge_car = client.get_data_tag("huge-car")
            source_camera_one = client.get_datasource("camera-one")
            source_camera_two = client.get_datasource("camera-two")

            lake = client.get_datalake()
            lake.upload_data(filepaths=["porsche.png", "ferrari.png"], tags=[tag_car], source=source_camera_one)
            lake.upload_data(filepaths="truck.png", tags=[tag_huge_car], source=source_camera_two)


            error_manager = ErrorManager()
            lake.upload_data(filepaths=["twingo.png", "path/unknown.png", error_manager=error_manager)

            # This call will return a list of UploadError to see what was wrong
            error_paths = [error.path for error in error_manager.errors]
            ```
        Arguments:
            filepaths (str or Path or List[str or Path]): Filepaths of your data
            tags (List[Tag], optional): Data Tags that will be given to data. Defaults to [].
            source (DataSource, optional): Source of your data.
            max_workers (int, optional): Number of max workers used to upload. Defaults to os.cpu_count() + 4.
            error_manager (ErrorManager, optional): Giving an ErrorManager will allow you to retrieve errors

        Returns:
            A (Data) object or a (MultiData) object that wraps a list of Data.
        """
        computed_tags_ids = []
        if tags:
            for tag in tags:
                if isinstance(tag, str):
                    computed_tag = self.get_or_create_data_tag(tag)
                else:
                    if tag.target_type == TagTarget.DATA:
                        computed_tag = tag
                    else:
                        computed_tag = self.create_data_tag(tag.name)

                computed_tags_ids.append(computed_tag.id)

        if source and isinstance(source, str):
            source = DataSourceService.get_or_create_datasource(
                self.connexion, self._organization_id, source
            )

        def upload_filepath(path: Union[str, Path]):
            try:
                # Retrieve presigned url from platform
                filename = os.path.split(path)[-1]
                object_name = self.connexion.generate_data_object_name(
                    filename, self.connector_id
                )
                _, _, content_type = self.connexion.upload_file(
                    object_name, path, connector_id=self.connector_id
                )

                with Image.open(path) as image:
                    width, height = get_image_shape_with_exif_transpose(image)

                payload = {
                    "type": DataType.IMAGE,
                    "filename": filename,
                    "object_name": object_name,
                    "content_type": content_type,
                    "meta": {
                        "height": height,
                        "width": width,
                    },
                    "tags": computed_tags_ids,
                    "data_source_id": source.id if source else None,
                }

                r = self.connexion.post(
                    f"/sdk/datalake/{self.id}/datas",
                    data=orjson.dumps(payload),
                ).json()
                return Data(self.connexion, self.id, r)
            except Exception as e:
                message = f"Could not upload path '{path}'"
                logger.error(message, exc_info=e)
                if error_manager:
                    error_manager.append(
                        UploadError(message=message, path=path, parent=e)
                    )
                return None

        if isinstance(filepaths, str) or isinstance(filepaths, Path):
            filepaths = [filepaths]

        logger.info("🌎 Starting upload..")

        results = mlt.do_mlt_function(
            filepaths, upload_filepath, max_workers=max_workers
        )
        data_list: List[Data] = [v for _, v in results.items() if v is not None]

        if len(data_list) != len(filepaths):
            logger.error(f"❌ {len(filepaths) - len(data_list)} data not uploaded.")
            if error_manager:
                logger.error(
                    "Calling error_manager.errors will return a list of UploadError objects to see what happened"
                )

        if len(data_list) == 0:
            raise NothingDoneError("Nothing has been uploaded.")
        elif len(data_list) == 1:
            logger.info(f"✅ {data_list[0].filename} data uploaded in {self}")
            return data_list[0]
        else:
            logger.info(f"✅ {len(data_list)} data uploaded in {self}")
            return MultiData(self.connexion, self.id, data_list)

    @exception_handler
    @beartype
    def find_data(
        self,
        filename: Optional[str] = None,
        object_name: Optional[str] = None,
        id: Union[str, UUID, None] = None,
    ) -> Data:
        """Find a data into this datalake

        You can find it by giving its filename or its object name or its id

        Examples:
            ```python
            my_data = my_datalake.find_asset(filename="test.png")
            ```
        Arguments:
            filename (str, optional): filename of the data. Defaults to None.
            object_name (str, optional): object name in the storage S3. Defaults to None.
            id (str or UUID, optional): id of the data. Defaults to None

        Raises:
            If no data match the query, it will raise a NotFoundError.
            In some case, it can raise an InvalidQueryError,
                it might be because platform stores 2 data matching this query (for example if filename is duplicated)

        Returns:
            The (Data) found
        """
        assert not (
            filename is None and object_name is None and id is None
        ), "Select at least one criteria to find a data"

        params = {}
        if id is not None:
            params["id"] = id

        if filename is not None:
            params["filename"] = filename

        if object_name is not None:
            params["object_name"] = object_name

        r = self.connexion.get(
            f"/sdk/datalake/{self.id}/datas/find", params=params
        ).json()
        return Data(self.connexion, self.id, r)

    @exception_handler
    @beartype
    def list_data(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        page_size: Optional[int] = None,
        order_by: Optional[List[str]] = None,
        tags: Union[str, Tag, List[Union[str, Tag]], None] = None,
        filenames: Optional[List[str]] = None,
        intersect_tags: Optional[bool] = False,
        object_names: Optional[List[str]] = None,
        q: Optional[str] = None,
    ) -> MultiData:
        """List data of this datalake.

        If there is no data, raise a NoDataError exception.

        Returned object is a MultiData. An object that allows manipulation of a bunch of data.
        You can add tags on them or feed a dataset with them.

        Examples:
            ```python
            lake = client.get_datalake()
            data = lake.list_data()
            ```

        Args:
            limit (int, optional): if given, will limit the number of data returned
            offset (int, optional): if given, will return data that would have been returned
                                    after this offset in given order
            page_size (int, optional): page size when returning data paginated, can change performance
            order_by (list[str], optional): if not empty, will order data by fields given in this parameter
            filenames (list[str], optional): if given, will return data that have filename equals to one of given filenames
            object_names (list[str], optional): if  given, will return data that have object name equals to one of given object names
            tags (str, (Tag), list[(Tag) or str], optional): if given, will return data that have one of given tags
                                                            by default. if `intersect_tags` is True, it will return data
                                                            that have all the given tags
            intersect_tags (bool, optional): if True, and a list of tags is given, will return data that have
                                             all the given tags. Defaults to False.
            q (str, optional): if given, will filter data with given query. Defaults to None.

        Raises:
            NoDataError: When datalake has no data, raise this exception.

        Returns:
            A (MultiData) object that wraps a list of (Data).
        """
        tags_q = convert_tag_list_to_query_language(tags, intersect_tags)
        query = combine_two_ql(q, tags_q)

        datas = mlt.do_paginate(
            limit,
            offset,
            page_size,
            partial(self._do_list_data, query, order_by, filenames, object_names),
        )

        if len(datas) == 0:
            raise NoDataError("No data found in this datalake with this query")

        return MultiData(self.connexion, self.id, datas)

    @exception_handler
    @beartype
    def _do_list_data(
        self,
        q: Optional[str],
        order_by: Optional[List[str]],
        filenames: Optional[List[str]],
        object_names: Optional[List[str]],
        limit: int,
        offset: int,
    ) -> Tuple[List[Data], int]:
        params = {"limit": limit, "offset": offset}

        if order_by is not None:
            params["order_by"] = order_by
        if q is not None:
            params["q"] = q

        if filenames or object_names:
            # PIC-27 Large filenames and object names list can't be used in GET method
            payload = {}
            if filenames:
                payload["filenames"] = filenames
            if object_names:
                payload["object_names"] = object_names

            r = self.connexion.xget(
                f"/sdk/datalake/{self.id}/datas",
                params=params,
                data=orjson.dumps(payload),
            ).json()
        else:
            r = self.connexion.get(
                f"/sdk/datalake/{self.id}/datas", params=params
            ).json()

        return list(map(partial(Data, self.connexion, self.id), r["items"])), r["count"]

    @exception_handler
    @beartype
    def create_data_tag(self, name: str) -> Tag:
        """Create a data tag used in this datalake

        Examples:
            ```python
            tag_car = lake.create_data_tag("car")
            ```
        Arguments:
            name (str): Name of this tag

        Returns:
            A (Tag) object
        """
        payload = {"name": name}
        r = self.connexion.post(
            f"/sdk/datalake/{self.id}/tags", data=orjson.dumps(payload)
        ).json()
        return Tag(self.connexion, r)

    @exception_handler
    @beartype
    def get_data_tag(self, name: str) -> Tag:
        """Retrieve a data tag used in this datalake.

        Examples:
            ```python
            tag_car = lake.get_data_tag("car")
            ```
        Arguments:
            name (str): Name of the tag you're looking for

        Returns:
            A (Tag) object
        """
        params = {"name": name}
        r = self.connexion.get(
            f"/sdk/datalake/{self.id}/tags/find", params=params
        ).json()
        return Tag(self.connexion, r)

    @exception_handler
    @beartype
    def get_or_create_data_tag(self, name: str) -> Tag:
        """Retrieve a data tag used in this datalake by its name.
        If tag does not exist, create it and return it.

        Examples:
            ```python
            tag = self.get_or_create_data_tag("new_tag")
            ```
        Arguments:
            name (str): Tag to retrieve or create

        Returns:
            A (Tag) object
        """
        try:
            return self.get_data_tag(name)
        except exceptions.ResourceNotFoundError:
            return self.create_data_tag(name)

    @exception_handler
    @beartype
    def list_data_tags(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
    ) -> List[Tag]:
        """List all tags of this datalake

        Examples:
            ```python
            tags = lake.list_data_tags()
            assert tag_car in tags
            ```

        Returns:
            A List of (Tag)
        """
        params = {"limit": limit, "offset": offset, "order_by": order_by}
        params = filter_payload(params)
        r = self.connexion.get(f"/sdk/datalake/{self.id}/tags", params=params).json()
        return list(map(partial(Tag, self.connexion), r["items"]))

    @exception_handler
    @beartype
    @deprecated(
        deprecated_in="6.3.2", details="This method can be replaced by list_data()"
    )
    def find_all_datas(self, object_names: List[str]) -> MultiData:
        return self.list_data(object_names=object_names)
