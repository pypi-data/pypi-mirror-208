import logging
import os
import warnings
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

import orjson
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from deprecation import deprecated
from picsellia_annotations.coco import Category, COCOFile
from picsellia_annotations.coco import Image as COCOImage
from picsellia_annotations.voc import Object

import picsellia.pxl_multithreading as mlt
from picsellia import exceptions
from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.exceptions import NoDataError, ResourceNotFoundError
from picsellia.sdk.annotation import Annotation, MultiAnnotation
from picsellia.sdk.asset import Asset, MultiAsset
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.data import Data, MultiData
from picsellia.sdk.job import Job
from picsellia.sdk.label import Label
from picsellia.sdk.tag import Tag, TagTarget
from picsellia.sdk.taggable import Taggable
from picsellia.sdk.worker import Worker
from picsellia.services import coco_importer, voc_importer, yolo_importer
from picsellia.services.asset_splitter import AssetSplitter
from picsellia.services.coco_file_builder import COCOFileBuilder
from picsellia.types.enums import (
    AnnotationFileType,
    AnnotationStatus,
    ImportAnnotationMode,
    InferenceType,
)
from picsellia.types.schemas import DatasetVersionSchema, DatasetVersionStats
from picsellia.utils import (
    combine_two_ql,
    convert_tag_list_to_query_language,
    filter_payload,
    flatten_dict,
)

warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)
logger = logging.getLogger("picsellia")


class DatasetVersion(Dao, Taggable):
    def __init__(self, connexion: Connexion, data: dict):
        Dao.__init__(self, connexion, data)
        Taggable.__init__(self, TagTarget.DATASET_VERSION)

    @property
    def origin_id(self) -> UUID:
        """UUID of the (Dataset) origin"""
        return self._origin_id

    @property
    def name(self) -> str:
        """Name of the (Dataset) origin"""
        return self._name

    @property
    def version(self) -> str:
        """Version of this (DatasetVersion)"""
        return self._version

    @property
    def type(self) -> InferenceType:
        """Type of this (DatasetVersion)"""
        return self._type

    def __str__(self):
        return f"{Colors.YELLOW}Version '{self.version}' of dataset {self.name} {Colors.ENDC} (id: {self.id})"

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

        return f"{self.connexion.host}/dataset/version/{self.id}"

    @exception_handler
    @beartype
    def refresh(self, data: dict):
        schema = DatasetVersionSchema(**data)
        self._name = schema.name
        self._version = schema.version
        self._type = schema.type
        self._origin_id = schema.origin_id
        return schema

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/dataset/version/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def get_tags(self) -> List[Tag]:
        """Retrieve tags of your dataset version.

        Examples:
            ```python
            tags = foo_dataset_version.get_tags()
            assert tags[0].name == "training-dataset"
            ```

        Returns:
            List of (Tag) objects
        """
        r = self.sync()
        return list(map(partial(Tag, self.connexion), r["tags"]))

    @exception_handler
    @beartype
    def add_data(
        self,
        data: Union[Data, List[Data], MultiData],
        tags: Optional[List[Union[str, Tag]]] = None,
    ) -> Job:
        """Feed this version with data coming from a datalake.

        A versioned dataset (DatasetVersion) takes (Data) from (Datalake) and transform it as annotable (Asset).
        You can give tags that will be added as asset tags to every created asset.

        Examples:
            ```python
            foo_dataset = client.create_dataset('foo_dataset')
            foo_dataset_version_1 = foo_dataset.create_version('first')
            some_data = client.get_datalake().list_data(limit=1000)
            foo_dataset_version_1.add_data(some_data)
            ```

        Arguments:
            data ((Data), List[(Data)] or (MultiData)): data to add to dataset
            tags (List of str or Tag) : tags to add to every asset created
        """
        if isinstance(data, Data):
            payload = {"data_ids": [data.id]}
        else:
            payload = {"data_ids": [data.id for data in data]}

        assert payload["data_ids"] != [], "Please specify the assets to add to dataset"

        asset_tag_ids = set()
        asset_tag_names = set()
        if tags:
            for tag in tags:
                tag_name = tag.name if isinstance(tag, Tag) else tag
                tag_created = self.get_or_create_asset_tag(tag_name)
                asset_tag_ids.add(tag_created.id)
                asset_tag_names.add(tag_created.name)

        payload["asset_tag_ids"] = list(asset_tag_ids)

        r = self.connexion.post(
            f"/sdk/dataset/version/{self.id}/assets", data=orjson.dumps(payload)
        ).json()
        self.refresh(r["dataset_version"])
        logger.info(
            f"Data are being added as assets to {self}.\n"
            "This operation can take some time (depending on how much asset you're adding)."
        )
        if asset_tag_names:
            tag_names = ", ".join(asset_tag_names)
            logger.info(f"Each asset created will have tags: {tag_names}")
        return Job(self.connexion, r["job"], version=1)

    @exception_handler
    @beartype
    def fork(
        self,
        version: str,
        description: Optional[str] = None,
        assets: Union[List[Asset], MultiAsset, Asset, None] = None,
        type: Union[InferenceType, str] = InferenceType.NOT_CONFIGURED,
        with_tags: bool = False,
    ) -> Tuple["DatasetVersion", Job]:
        """Fork this dataset version into another dataset version, with the same origin.

        Will create a new dataset version, with the same origin and the given version.
        You can give a description and a default type.
        You can give a list of asset coming from this dataset version to add into the new dataset version.
        Only these assets will be added to the new dataset.
        If with_tags is True, tags of each asset will be transferred to the new dataset version.

        Examples:
            ```python
            foo_dataset_version = client.get_dataset('my_datatest').get_version('first')
            assets = foo_dataset_version.list_assets(limit=100)
            bar_dataset_version = foo_dataset_version.fork('second', assets)
            ```

        Arguments:
            version (str): new version name
            description (str): description, defaults to "Forked from version '<version_name>'"
            assets ((MultiAsset) or (Asset)): assets to add to the new dataset version, defaults will be all assets
            type (InferenceType): inference type of the new dataset version, defaults to NOT_CONFIGURED
            with_tags (bool): if true tags of assets will be added to the new dataset version, defaults to false

        Returns:
            A (DatasetVersion) with given assets
        """
        type = InferenceType.validate(type)

        if version == "":
            raise ValueError("Version name can't be empty")

        if description is None:
            description = f"Fork from {self.version}"

        payload = {
            "parent_id": self.id,
            "version": version,
            "description": description,
            "type": type,
            "with_tags": with_tags,
        }

        if assets is not None:
            if isinstance(assets, Asset):
                assets: List[Asset] = [assets]
            payload["asset_ids"] = [asset.id for asset in assets]

        r = self.connexion.post(
            f"/sdk/dataset/{self.origin_id}/fork", data=orjson.dumps(payload)
        ).json()
        logger.info(
            f"{self} forked with {len(assets) if assets is not None else 'all'} assets"
        )
        return DatasetVersion(self.connexion, r["dataset_version"]), Job(
            self.connexion, r["job"], version=1
        )

    @exception_handler
    @beartype
    def find_asset(
        self,
        data: Optional[Data] = None,
        filename: Optional[str] = None,
        object_name: Optional[str] = None,
    ) -> Asset:
        """Find an asset into this dataset version

        You can find it by giving its supposed Data object, its filename or its object name

        Examples:
            ```python
            my_asset = my_dataset_version.find_asset(filename="test.png")
            ```
        Arguments:
            data (Data, optional): data linked to asset. Defaults to None.
            filename (str, optional): filename of the asset. Defaults to None.
            object_name (str, optional): object name in the storage S3. Defaults to None.

        Raises:
            If no asset match the query, it will raise a NotFoundError.
            In some case, it can raise an InvalidQueryError,
                it might be because platform stores 2 assets matching this query (for example if filename is duplicated)

        Returns:
            The (Asset) found
        """
        assert not (
            data is None and filename is None and object_name is None
        ), "Select at least one criteria to find an asset"

        params = {}
        if data is not None:
            params["data_id"] = data.id

        if filename is not None:
            params["filename"] = filename

        if object_name is not None:
            params["object_name"] = object_name

        r = self.connexion.get(
            f"/sdk/dataset/version/{self.id}/assets/find", params=params
        ).json()
        return Asset(self.connexion, self.id, r)

    @exception_handler
    @beartype
    @deprecated(
        deprecated_in="6.4.0", details="This method can be replaced by list_assets()"
    )
    def find_all_assets(
        self,
        filenames: Optional[List[str]] = None,
        object_names: Optional[List[str]] = None,
        ids: Optional[List[Union[str, UUID]]] = None,
    ) -> MultiAsset:
        """Find some assets of this dataset version from their filenames

        Examples:
            ```python
            my_asset = my_dataset_version.find_all_assets(filenames=["test.png", "image2.jpg"])
            ```
        Arguments:
            ids: (List[UUID]): ids of the assets you're looking for. Defaults to None.
            filenames (List[str]): filenames of the assets you're looking for. Defaults to None.
            object_names (List[str]): object names of the assets you're looking for. Defaults to None.

        Returns:
            A list of (Asset) found
        """
        return self.list_assets(filenames=filenames, object_names=object_names, ids=ids)

    @exception_handler
    @beartype
    def list_assets(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        page_size: Optional[int] = None,
        order_by: Optional[List[str]] = None,
        tags: Union[Tag, List[Tag], str, List[str], None] = None,
        data_tags: Union[Tag, List[Tag], str, List[str], None] = None,
        intersect_tags: bool = False,
        intersect_data_tags: bool = False,
        filenames: Optional[List[str]] = None,
        object_names: Optional[List[str]] = None,
        ids: Optional[List[Union[str, UUID]]] = None,
        filenames_startswith: Optional[List[str]] = None,
        q: Optional[str] = None,
    ) -> MultiAsset:
        """List assets of this dataset version

        It will retrieve all assets object of this dataset.
        You will then be able to manipulate them or add them to another dataset.

        Examples:
            ```python
            assets = foo_dataset_version.list_assets()
            ```

        Arguments:
            limit (int): limit to a certain number of assets
            offset (int): offset to access some new objects, if 0 will retrieve starting from the beginning
            page_size (int): page size when paginating.
            order_by (str): a list of string to use for sorting data, if None will not sort
            tags (str, (Tag), list[(Tag) or str], optional): if given, will return assets that have one of given tags
                                                            by default. if `intersect_tags` is True,
                                                            it will return assets that have all the given tags
            intersect_tags (bool, optional): if True, and a list of tags is given, will return assets that have
                                             all the given tags. Defaults to False.
            data_tags (str, (Tag), list[(Tag) or str], optional): if given, will return assets that have one of given
                                                            data tags by default. if `intersect_data_tags` is True,
                                                            it will return assets that have all the given data tags
            intersect_data_tags (bool, optional): if True, and a list of data tags is given, will return assets that have
                                             all the given data tags. Defaults to False.
            filenames (list[str], optional): if given, will return assets that have filename equals to one of given filenames
            filenames_startswith (list[str], optional): if given, will return assets that have filename starting with to one of given filenames
            object_names (list[str], optional): if  given, will return assets that have object name equals to one of given object names
            ids: (List[UUID]): ids of the assets you're looking for. Defaults to None.
            q (str, optional): if given, will filter data with given query. Defaults to None.

        Returns:
            A (MultiAsset) object that wraps some (Asset) that you can manipulate.
        """
        qt = convert_tag_list_to_query_language(tags, intersect_tags)
        qd = convert_tag_list_to_query_language(
            data_tags, intersect_data_tags, prefix="data."
        )
        query = combine_two_ql(qt, combine_two_ql(q, qd))

        assets = mlt.do_paginate(
            limit,
            offset,
            page_size,
            partial(
                self._do_list_assets,
                query,
                order_by,
                filenames,
                object_names,
                ids,
                filenames_startswith,
            ),
        )

        if len(assets) == 0:
            raise NoDataError("No asset retrieved")

        return MultiAsset(self.connexion, self.id, assets)

    @exception_handler
    @beartype
    def _do_list_assets(
        self,
        q: Optional[str],
        order_by: Optional[List[str]],
        filenames: Optional[List[str]],
        object_names: Optional[List[str]],
        ids: Optional[List[Union[str, UUID]]],
        filenames_startswith: Optional[List[str]],
        limit: int,
        offset: int,
    ) -> Tuple[List[Asset], int]:
        params = {"limit": limit, "offset": offset}
        if order_by is not None:
            params["order_by"] = order_by
        if q is not None:
            params["q"] = q

        if filenames or object_names or ids:
            payload = {}
            if filenames:
                payload["filenames"] = filenames
            if object_names:
                payload["object_names"] = object_names
            if ids:
                payload["ids"] = ids
            if filenames_startswith:
                payload["filename_startswith"] = filenames_startswith

            r = self.connexion.xget(
                f"/sdk/dataset/version/{self.id}/assets",
                params=params,
                data=orjson.dumps(payload),
            ).json()
        else:
            r = self.connexion.get(
                f"/sdk/dataset/version/{self.id}/assets", params=params
            ).json()

        return (
            list(map(partial(Asset, self.connexion, self.id), r["items"])),
            r["count"],
        )

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete a dataset version.

        :warning: **DANGER ZONE**: Be very careful here!

        It will remove this dataset version from our database, all of its assets and annotations will be removed.

        Examples:
            ```python
            foo_dataset_version.delete()
            ```
        """
        self.connexion.delete(f"/sdk/dataset/version/{self.id}")
        logger.info(f"{self} deleted")

    @exception_handler
    @beartype
    def set_type(self, type: Union[str, InferenceType]) -> None:
        """Set inference type of this DatasetVersion.
            You can pass a string with the exact key corresponding to inference type or an enum value InferenceType.

        Examples:
            ```python
            dataset.set_type('object_detection')
            dataset.set_type(InferenceType.SEGMENTATION)
            ```

        Args:
            type (str or InferenceType): type to give to this dataset version

        """
        inference_type = InferenceType.validate(type)
        payload = {"type": inference_type}
        r = self.connexion.patch(
            f"/sdk/dataset/version/{self.id}", data=orjson.dumps(payload)
        ).json()
        self.refresh(r)
        logger.info(f"{self} is now of type {inference_type.name}")

    @exception_handler
    @beartype
    def update(
        self,
        version: Optional[str] = None,
        description: Optional[str] = None,
        type: Union[str, InferenceType, None] = None,
    ) -> None:
        """Update version, description and type of a Dataset.

        Examples:
            ```python
            dataset.update(description='My favourite dataset')
            ```
        """
        payload = {"version": version, "description": description}
        if type:
            payload["type"] = InferenceType.validate(type)
        filtered_payload = filter_payload(payload)
        r = self.connexion.patch(
            f"/sdk/dataset/version/{self.id}",
            data=orjson.dumps(filtered_payload),
        ).json()
        self.refresh(r)
        logger.info(f"{self} updated")

    @exception_handler
    @beartype
    def download(
        self,
        target_path: Union[str, Path, None] = None,
        force_replace: bool = False,
        max_workers: Optional[int] = None,
    ) -> None:
        """Downloads assets of a dataset.

        It will download all assets from a dataset into specified folder.
        If target_path is None, it will download into ./<dataset_name>/<dataset_version>
        You can precise a number of threads to use while downloading.

        Examples:
            ```python
            foo_dataset.download('~/Downloads/dataset_pics')
            ```
        Arguments:
            target_path (str or Path, optional): Target folder. Defaults to None.
            force_replace: (bool, optional): Replace an existing file if exists. Defaults to False.
            max_workers (int, optional): Number of max workers used to download. Defaults to os.cpu_count() + 4.
        """
        if target_path is not None:
            path = target_path
        else:
            path = os.path.join("./", self.name, self.version)

        Path(path).mkdir(parents=True, exist_ok=True)

        logger.debug(f"Retrieving assets of {self}...")
        multi_assets = self.list_assets()

        logger.debug("Downloading assets...")
        multi_assets.download(path, force_replace, max_workers)

        logger.info(f"Assets of {self} downloaded into {path}")

    @exception_handler
    @beartype
    def list_labels(self) -> List[Label]:
        """Get all labels of a dataset

        It will retrieve a list of label objects.

        Examples:
            ```python
            foo_dataset.create_label("today")
            labels = foo_dataset.get_labels()
            assert labels[0].name == "today"
            ```

        Returns:
            List of (Label)
        """
        r = self.connexion.get(f"/sdk/dataset/version/{self.id}/labels").json()
        return list(map(partial(Label, self.connexion), r["items"]))

    @exception_handler
    @beartype
    def create_label(self, name: str) -> Label:
        """Add label to a dataset version.

        You have to give a name to the label.

        Examples:
            ```python
            foo_dataset.create_label("today")
            ```
        Arguments:
            name (str): label name to add

        Returns:
            A (Label) object
        """

        payload = {"name": name}
        r = self.connexion.post(
            f"/sdk/dataset/version/{self.id}/labels", data=orjson.dumps(payload)
        ).json()
        label = Label(self.connexion, r)
        logger.info(f"{label} has been added to {self}")
        return label

    @exception_handler
    @beartype
    def get_label(self, name: str) -> Label:
        """Find label in a dataset version.

        Examples:
            ```python
            label = foo_dataset.get_label("today")
            ```
        Arguments:
            name (str): label name to find

        Returns:
            A (Label) object
        """

        params = {"name": name}
        r = self.connexion.get(
            f"/sdk/dataset/version/{self.id}/labels/find", params=params
        ).json()
        return Label(self.connexion, r)

    @exception_handler
    @beartype
    def get_or_create_label(self, name: str) -> Label:
        """Retrieve a label used in this dataset by its name.
        If label does not exist, create it and return it.

        Examples:
            ```python
            label = self.get_or_create_label("new_label")
            ```
        Arguments:
            name (str): label to retrieve or create

        Returns:
            A (label) object
        """
        try:
            return self.get_label(name)
        except ResourceNotFoundError:
            return self.create_label(name)

    @exception_handler
    @beartype
    def list_annotations(
        self,
        worker: Optional[Worker] = None,
        status: Union[AnnotationStatus, str, None] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
        page_size: Optional[int] = None,
    ) -> MultiAnnotation:
        """Retrieve annotations of a dataset.

        Examples:
            ```python
            annotations = foo_dataset.list_annotations()
            ```
        Arguments:
            limit (Optional[int], optional): Limit number of annotations to retrieve.
                Defaults to None, all annotations will be retrieved.
            offset (Optional[int], optional): Offset to begin with when listing annotations.
                Defaults to None, starting at 0.
            page_size (Optional[int], optional): Size of each page when retrieving .
                Defaults to None, page will be equals to default pagination.
            order_by (Optional[List[str]], optional): Order annotation by some criteria.
                Defaults to None.
            worker (Optional[Worker], optional): Worker filter.
                Defaults to None.
            status (Optional[AnnotationStatus], optional): Status of annotations to retrieve.
                Defaults to None.

        Raises:
            NoDataError: When no annotations retrieved

        Returns:
            A (MultiAnnotation) object
        """
        if status:
            status = AnnotationStatus.validate(status)

        annotations = mlt.do_paginate(
            limit,
            offset,
            page_size,
            partial(self._do_list_annotations, status, worker, order_by),
        )

        if len(annotations) == 0:
            raise NoDataError("No annotation retrieved")

        return MultiAnnotation(self.connexion, self.id, annotations)

    def _do_list_annotations(
        self,
        status: Optional[AnnotationStatus],
        worker: Optional[Worker],
        order_by: Optional[List[str]],
        limit: int,
        offset: int,
    ) -> Tuple[List[Annotation], int]:
        params = {"limit": limit, "offset": offset}
        if order_by is not None:
            params["order_by"] = order_by
        if worker is not None:
            params["worker_id"] = worker.id
        if status is not None:
            params["status"] = status.value

        r = self.connexion.get(
            f"/sdk/dataset/version/{self.id}/annotations", params=params
        ).json()
        return (
            list(
                map(
                    lambda item: Annotation(
                        self.connexion, self.id, UUID(item["asset_id"]), item
                    ),
                    r["items"],
                )
            ),
            r["count"],
        )

    @exception_handler
    @beartype
    def load_annotations(
        self,
        worker: Optional[Worker] = None,
        status: Optional[AnnotationStatus] = None,
        chunk_size: int = 1000,
        max_workers: Optional[int] = None,
        skip_error: bool = False,
    ) -> dict:
        """Load these annotation by retrieving shapes with labels, asset_id and worker_id

        Examples:
            ```python
            dict_annotations = foo_dataset.load_annotations()
            ```
        Arguments:
            worker (Optional[Worker], optional): Worker filter. Defaults to None.
            status (Optional[AnnotationStatus], optional): Status of annotations to retrieve. Defaults to None.
            chunk_size (int, optional): Size of chunk of annotations to load by request. Defaults to 1000.
            max_workers (int, optional): Number of max workers used to load annotations. Defaults to os.cpu_count() + 4.
            skip_error (bool, optional): skip error of a chunk and return partial annotations. Default to False
        """
        if chunk_size < 1 or chunk_size > 10000:
            raise exceptions.BadRequestError(
                "Impossible to load less than 1 or more than 10000 annotations by chunk. Please give another chunk_size"
            )

        params = {}
        if worker is not None:
            params["worker_id"] = worker.id
        if status is not None:
            params["status"] = status.value

        ids = self.connexion.get(
            f"/sdk/dataset/version/{self.id}/annotations/ids", params=params
        ).json()

        return MultiAnnotation.load_annotations_from_ids(
            self.connexion, self.id, ids, chunk_size, max_workers, skip_error
        )

    @exception_handler
    @beartype
    def export_annotation_file(
        self,
        annotation_file_type: Union[AnnotationFileType, str],
        target_path: Union[str, Path] = "./",
        assets: Union[MultiAsset, List[Asset], None] = None,
        worker: Optional[Worker] = None,
        status: Union[AnnotationStatus, str, None] = None,
        force_replace: bool = True,
    ) -> str:
        """Export annotations of this dataset version into a file, and download it.

        Giving 'worker' argument, you will retrieve only annotations of this worker if they exist.
        If you don't give 'worker', it will only export the last created annotation and its shapes.

        Examples:
            ```python
            dataset_v0.export_annotation_file(AnnotationFileType.COCO, "./")
            ```
        Arguments:
            annotation_file_type (AnnotationFileType): choose to export in Pascal VOC format or COCO format.
            target_path (str or Path, optional): directory path where file is downloaded. Defaults to current directory.
            assets (Union[(MultiAsset), List[(Asset)], None], optional): a list of assets of this dataset version.
                Only these assets will be concerned by this export. Defaults to None.
            worker ((Worker), optional): worker of annotations. Defaults to None.
            status (AnnotationStatus, optional): status of annotations. Defaults to None.
            force_replace (bool, optional): if true, will replace an existing file annotation. Defaults to True.

        Returns:
            Path of downloaded file.
        """
        payload = {"type": AnnotationFileType.validate(annotation_file_type)}
        if assets is not None:
            payload["asset_ids"] = [asset.id for asset in assets]

        if worker is not None:
            payload["worker_id"] = worker.id

        if status is not None:
            payload["status"] = AnnotationStatus.validate(status)

        r = self.connexion.post(
            f"/sdk/dataset/version/{self.id}/annotations/export",
            data=orjson.dumps(payload),
        ).json()

        path = os.path.join(target_path, r["object_name"])
        self.connexion.do_download_file(
            path=path,
            url=r["presigned_url"],
            is_large=True,
            force_replace=force_replace,
        )
        return path

    @exception_handler
    @beartype
    def build_coco_file_locally(
        self,
        worker: Optional[Worker] = None,
        status: Union[AnnotationStatus, str, None] = None,
        enforced_ordered_categories: Optional[List[str]] = None,
    ) -> COCOFile:
        """
            Build a coco file locally instead of exporting it from the platform.
            This method will load annotations of a dataset with given filters, then build all coco annotations,
            then load all assets and labels from platform needed in this coco file and return a coco file.

            Returned coco file can be then written into a file

        Args:
            worker ((Worker), optional): worker of annotations. Defaults to None.
            status (AnnotationStatus, optional): status of annotations. Defaults to None.
            enforced_ordered_categories (List of str, optional): use this parameter to enforce an order of categories
                                                                 for the coco file. Defaults to None.

        Returns:
            A COCO File object
        """
        label_names = [label.name for label in self.list_labels()]
        if enforced_ordered_categories:
            for enforced_category in enforced_ordered_categories:
                if enforced_category not in label_names:
                    raise ResourceNotFoundError(
                        f"Category {enforced_category} is not a label of this dataset version"
                    )

        builder = COCOFileBuilder(enforced_ordered_categories)
        asset_ids = builder.load_coco_annotations(self.load_annotations(worker, status))
        builder.load_coco_images(self.list_assets(ids=asset_ids))
        builder.load_coco_categories(label_names)
        return builder.build()

    @exception_handler
    @beartype
    def _assert_import_annotation_possible(self):
        self.sync()
        if self.type not in [
            InferenceType.OBJECT_DETECTION,
            InferenceType.SEGMENTATION,
            InferenceType.CLASSIFICATION,
        ]:
            raise TypeError(
                f"You need to set up type of this dataset before importing annotation files."
                f"This dataset is {self.type} at the moment. Call .set_type() to change type."
            )

    @exception_handler
    @beartype
    def _assert_labels_created(
        self, labels_retrieved: List[str], labels_file: List[str]
    ):
        if len(labels_retrieved) != len(labels_file):
            labels_not_found = set(labels_retrieved).difference(set(labels_file))
            raise ResourceNotFoundError(
                f"Labels {labels_not_found} were not found during upload."
                f"Call import with force_create_label=True or create missing labels manually"
            )

    @exception_handler
    @beartype
    def import_annotations_yolo_files(
        self,
        configuration_yaml_path: Union[str, Path],
        file_paths: List[Union[str, Path]],
        worker: Optional[Worker] = None,
        mode: Union[ImportAnnotationMode, str] = ImportAnnotationMode.REPLACE,
        force_create_label: bool = True,
        fail_on_asset_not_found: bool = True,
        status: Optional[AnnotationStatus] = None,
    ) -> Dict[str, int]:
        """Read a yolo annotation configuration file, then read all given file paths with annotations parse it and create annotations and shape for all assets

        Examples:
            ```python
            dataset_v0.import_annotations_yolo_files(configuration_yaml_path="data.yaml", file_paths=["asset1.txt"])
            ```

        Arguments:
            configuration_yaml_path (str, Path): Path to file of configuration
            file_paths (List of str or Path): Paths of annotation files to import
            worker (Worker, optional): Worker to use. Defaults to current user.
            mode (ImportAnnotationMode, optional): Mode used to import.
                    REPLACE will delete worker annotation if exists and replace it.
                    CONCATENATE will create shapes on existing annotation.
                    SKIP will do nothing on existing annotation.
                    Defaults to ImportAnnotationMode.REPLACE.
            force_create_label (bool): Ensures labels are created if they don't exist. Defaults to True.
            fail_on_asset_not_found (bool): If one filename is not found in dataset, fail before importing annotations. Defaults to True.
            status (AnnotationStatus): Annotation status to set to created annotations.

        Raises:
            FileNotFoundException: if file is not found
        """
        mode = ImportAnnotationMode.validate(mode)

        if not file_paths:
            logger.info("No file given ")
            return {}

        self._assert_import_annotation_possible()

        logger.info("Reading filenames")
        # filename -> file_path
        files: Dict[str, Path] = yolo_importer.read_filenames_from_file_paths(
            file_paths
        )

        logger.info("Reading labels from configuration file")
        label_names: List[str] = yolo_importer.parse_configuration_file(
            configuration_yaml_path
        )
        labels: List[Label] = self._create_labels_from_names(
            label_names, force_create_label
        )

        logger.info("Retrieving assets")
        multi_assets = self.list_assets(filenames_startswith=list(files.keys()))
        assets: Dict[str, Asset] = yolo_importer.match_assets_with_filenames(
            files, multi_assets
        )
        yolo_importer.assert_coherence_files_assets(
            files, assets, fail_on_asset_not_found
        )

        logger.info("Parsing yolo files")
        annotations = yolo_importer.parse_files_to_annotations(
            self.type, files, assets, labels
        )

        logger.info("Creating annotations..")
        worker_id = worker.id if worker else None
        results = mlt.do_chunk_called_function(
            annotations, partial(self._bulk_create_annotations, mode, worker_id, status)
        )
        return flatten_dict(results, lambda value: value >= 0)

    @exception_handler
    @beartype
    def _create_labels_from_names(
        self, label_names: List[str], force_create_label: bool
    ):
        if force_create_label:
            self._bulk_get_or_create_labels(label_names)

        return [self.get_label(label_name) for label_name in label_names]

    @exception_handler
    @beartype
    def import_annotation_voc_file(
        self,
        file_path: Union[str, Path],
        worker: Optional[Worker] = None,
        mode: Union[ImportAnnotationMode, str] = ImportAnnotationMode.REPLACE,
        force_create_label: bool = True,
        status: Optional[AnnotationStatus] = None,
    ) -> Dict[str, int]:
        """Read a Pascal VOC file, parse it and create some annotations and shape for one given asset

        Examples:
            ```python
            dataset_v0.import_annotation_voc_file(file_path="voc.xml")
            ```

        Arguments:
            file_path (str or Path): Path of file to import
            worker (Worker, optional): Worker to use. Defaults to current user.
            mode (ImportAnnotationMode, optional): Mode used to import.
                    REPLACE will delete worker annotation if exists and replace it.
                    CONCATENATE will create shapes on existing annotation.
                    KEEP will do nothing on existing annotation.
                    Defaults to ImportAnnotationMode.REPLACE.
            force_create_label (bool): Ensures labels are created if they don't exist. Defaults to True.
            status (AnnotationStatus, optional): status given to created annotations. Defaults to None.

        Returns:
            A dict with annotation id as string keys and number of shapes created as integer.

        Raises:
            FileNotFoundException: if file is not found
        """
        self._assert_import_annotation_possible()

        mode = ImportAnnotationMode.validate(mode)

        logger.info("Parsing VOC file")
        vocfile = voc_importer.parse_file(file_path)
        objects = voc_importer.parse_objects(vocfile)

        logger.info("Reading labels")
        labels: Dict[str, str] = self._read_labels_from_voc_objects(
            objects, force_create_label
        )

        logger.info("Retrieving asset")
        asset = self.find_asset(filename=vocfile.annotation.filename)

        logger.info("Reading shapes..")
        annotations = voc_importer.read_annotations_from_voc_objects(
            self.type, objects, labels, asset
        )

        worker_id = worker.id if worker else None

        logger.info("Creating annotations..")
        return self._bulk_create_annotations(mode, worker_id, status, annotations)

    @exception_handler
    @beartype
    def _read_labels_from_voc_objects(
        self, objects: List[Object], force_create_label: bool
    ) -> Dict[str, str]:
        label_names = list(set([obj.name for obj in objects]))
        if force_create_label:
            self._bulk_get_or_create_labels(label_names)

        labels: Dict[str, str] = {}
        for label in self.list_labels():
            if label.name in label_names:
                labels[label.name] = str(label.id)

        self._assert_labels_created(list(labels.keys()), label_names)
        return labels

    @exception_handler
    @beartype
    def import_annotations_coco_file(
        self,
        file_path: Union[Path, str],
        worker: Optional[Worker] = None,
        mode: Union[ImportAnnotationMode, str] = ImportAnnotationMode.REPLACE,
        force_create_label: bool = True,
        fail_on_asset_not_found: bool = True,
        status: Optional[AnnotationStatus] = None,
    ) -> Dict[str, int]:
        """Read a COCO file, parse it and create some annotations and shape for given assets

        Examples:
            ```python
            dataset_v0.import_annotations_coco_file(file_path="coco.json")
            ```

        Arguments:
            file_path (str): Path of file to import
            worker (Worker, optional): Worker to use. Defaults to current user.
            mode (ImportAnnotationMode, optional): Mode used to import.
                    REPLACE will delete worker annotation if exists and replace it.
                    CONCATENATE will create shapes on existing annotation.
                    KEEP will do nothing on existing annotation.
                    Defaults to ImportAnnotationMode.REPLACE.
            force_create_label (bool): Ensure labels are created if they don't exist. Defaults to True
            fail_on_asset_not_found (bool): Raise an error if asset is not found. Defaults to True
            status (AnnotationStatus, optional): Annotation Status of imported annotations, default will be PENDING.
                                                 Defaults to None.

        Raises:
            FileNotFoundException: if file is not found

        Returns:
            A dict with annotation id as string keys and number of shapes created as integer.

        """
        self._assert_import_annotation_possible()

        mode = ImportAnnotationMode.validate(mode)

        logger.info(f"Parsing file {file_path}..")
        cocofile = coco_importer.parse_coco_file(file_path)

        logger.info("Reading categories as labels..")
        labels: Dict[int, Label] = self._find_labels_from_coco_categories(
            cocofile.categories, force_create_label
        )

        logger.info("Reading images as assets...")
        asset_ids_map: Dict[int, str] = self._read_images_and_retrieve_assets(
            cocofile.images, fail_on_asset_not_found
        )

        logger.info("Reading shapes..")
        annotations: List[dict] = coco_importer.read_annotations(
            self.type, cocofile.annotations, labels, asset_ids_map
        )

        worker_id = worker.id if worker else None

        logger.info("Creating annotations..")
        results = mlt.do_chunk_called_function(
            annotations, partial(self._bulk_create_annotations, mode, worker_id, status)
        )
        return flatten_dict(results, lambda value: value >= 0)

    @exception_handler
    @beartype
    def _find_labels_from_coco_categories(
        self, categories: List[Category], force_create_label: bool
    ) -> Dict[int, Label]:
        categories_map: Dict[str, int] = {}
        for category in categories:
            categories_map[category.name] = category.id

        if force_create_label:
            self._bulk_get_or_create_labels(list(categories_map.keys()))

        labels: Dict[int, Label] = {}
        for label in self.list_labels():
            if label.name in categories_map:
                labels[categories_map[label.name]] = label

        self._assert_labels_created(
            list(categories_map.keys()), [label.name for label in labels.values()]
        )
        return labels

    @exception_handler
    @beartype
    def _bulk_get_or_create_labels(self, label_names: List[str]) -> List[Label]:
        payload = {"names": label_names}
        r = self.connexion.xget(
            f"/sdk/dataset/version/{self.id}/bulk-labels",
            data=orjson.dumps(payload),
        ).json()
        return list(map(partial(Label, self.connexion), r))

    @exception_handler
    @beartype
    def _read_images_and_retrieve_assets(
        self, images: List[COCOImage], fail_on_asset_not_found: bool
    ):
        filenames = {image.file_name: image.id for image in images}
        multi_assets = self.list_assets(filenames=list(filenames.keys()))

        if fail_on_asset_not_found and len(multi_assets) != len(filenames):
            raise ResourceNotFoundError(
                "Some filenames were not found in this dataset version."
            )

        return {filenames[asset.filename]: str(asset.id) for asset in multi_assets}

    @exception_handler
    @beartype
    def _bulk_create_annotations(
        self,
        import_type: ImportAnnotationMode,
        worker_id: Optional[UUID],
        status: Optional[AnnotationStatus],
        annotations: List[Dict],
    ):
        payload = {
            "import_type": import_type,
            "annotations": annotations,
        }
        if worker_id:
            payload["worker_id"] = worker_id
        if status:
            payload["status"] = status

        return self.connexion.post(
            f"/sdk/dataset/version/{self.id}/bulk-annotations",
            data=orjson.dumps(payload),
        ).json()

    @exception_handler
    @beartype
    def delete_all_annotations(self, workers: Optional[List[Worker]] = None) -> None:
        """Delete all annotations of this dataset

        :warning: **DANGER ZONE**: Be very careful here!

        It will remove all annotation of every asset of this dataset
        You can give workers on which it will be effectively erased.

        Examples:
            ```python
            foo_dataset.delete_all_annotations()
            ```
        """
        payload = {"asset_ids": ["__all__"]}
        if workers is not None:
            payload["worker_ids"] = [worker.id for worker in workers]

        self.connexion.delete(
            f"/sdk/dataset/version/{self.id}/annotations",
            data=orjson.dumps(payload),
        )
        logger.info(f"All annotations in {self} were removed.")

    @exception_handler
    @beartype
    def synchronize(
        self, target_dir: str, do_download: bool = False
    ) -> Optional[MultiAsset]:
        """Synchronize this dataset with target dir by comparing assets in target dir with assets uploaded in dataset.

        Examples:
            ```python
            foo_dataset.synchronize('./foo_dataset/first')
            ```
        Arguments:
            target_dir (str): directory to synchronize against
            do_download (bool): do download files when they are not in local directory
        """
        assert os.path.isdir(target_dir), "Please select a valid directory path"
        logger.info("⌛️ Scanning Dataset Assets..")
        assets: MultiAsset = self.list_assets()
        filenames = set(map(lambda asset: asset.filename, assets.items))
        logger.info("🔍 Scanning Local Dataset Folder ..")
        local_filenames = set(
            [
                e
                for e in os.listdir(target_dir)
                if os.path.isfile(os.path.join(target_dir, e))
            ]
        )

        not_uploaded = local_filenames - filenames
        if len(not_uploaded) > 0:
            logger.info(
                f"📚 {len(not_uploaded)} assets not uploaded. You need to add data to the datalake first with :"
            )
            filepaths = list(
                map(
                    lambda filename: str(os.path.join(target_dir, filename)),
                    not_uploaded,
                )
            )
            logger.info(f"filepaths = {filepaths}")
            logger.info("list_data = client.get_datalake().upload_data(filepaths)")
            logger.info(
                f'client.get_dataset_by_id({self.origin_id}).get_version("{self.version}").add_data(list_data)'
            )

        not_downloaded = filenames - local_filenames
        if len(not_downloaded) > 0:
            assets_to_download = list(
                filter(
                    lambda asset: asset.filename in not_downloaded,
                    assets.items,
                )
            )
            multi_assets = MultiAsset(self.connexion, self.id, assets_to_download)
            logger.info(f"📚 {len(not_downloaded)} assets not downloaded")
            if do_download:
                logger.info(f"📚 Downloading {len(not_downloaded)} assets")
                multi_assets.download(target_dir)
            else:
                logger.info(
                    "📚 Call this method again with do_download=True if you want to download these assets"
                )
            return multi_assets
        else:
            logger.info("✅ Dataset is up-to-date.")
            return None

    @exception_handler
    @beartype
    def retrieve_stats(self) -> DatasetVersionStats:
        """Retrieve statistics of this dataset version (label repartition, number of objects, number of annotations).

        Examples:
            ```python
            stats = foo_dataset.retrieve_stats()
            assert stats.label_repartition == {"cat": 23, "dog": 2}
            assert stats.nb_objects == 25
            assert stats.nb_annotations == 5
            ```

        Returns:
            A DatasetVersionStats schema with keys:
                - label_repartition: dict with label names as keys and number of shape with these labels as value
                - nb_objects: total number of objects (sum of label_repartition values)
                - nb_annotations: total number of (Annotation) objects of this dataset version
        """
        r = self.connexion.get(f"/sdk/dataset/version/{self.id}/stats").json()
        return DatasetVersionStats(**r)

    @exception_handler
    @beartype
    def get_or_create_asset_tag(self, name: str) -> Tag:
        """Retrieve an asset tag used in this dataset version by its name.
        If tag does not exist, create it and return it.

        Examples:
            ```python
            tag = self.get_or_create_asset_tag("new_tag")
            ```
        Arguments:
            name (str): Tag to retrieve or create

        Returns:
            A (Tag) object
        """
        try:
            return self.get_asset_tag(name)
        except exceptions.ResourceNotFoundError:
            return self.create_asset_tag(name)

    @exception_handler
    @beartype
    def create_asset_tag(self, name: str) -> Tag:
        """Create asset tag only available in this dataset version.

        Examples:
            ```python
            tag_dog = dataset_v0.create_asset_tag("dog")
            ```
        Arguments:
            name (str): name of tag

        Returns:
            A (Tag) object
        """
        payload = {"name": name}
        r = self.connexion.post(
            f"/sdk/dataset/version/{self.id}/tags", data=orjson.dumps(payload)
        ).json()
        return Tag(self.connexion, r)

    @exception_handler
    @beartype
    def get_asset_tag(self, name: str) -> Tag:
        """Retrieve an asset tag used in this dataset version.

        Examples:
            ```python
            tag_dog = dataset_v0.get_asset_tag("dog")
            ```
        Arguments:
            name (str): Name of the tag you're looking for

        Returns:
            A (Tag) object
        """
        params = {"name": name}
        r = self.connexion.get(
            f"/sdk/dataset/version/{self.id}/tags/find", params=params
        ).json()
        return Tag(self.connexion, r)

    @exception_handler
    @beartype
    def convert_tags_to_classification(
        self, tag_type: TagTarget, tags: List[Tag]
    ) -> Job:
        assert (
            self.type == InferenceType.CLASSIFICATION
        ), "You cannot convert tags on this dataset."
        assert (
            tag_type == TagTarget.ASSET or tag_type == TagTarget.DATA
        ), "You can only convert asset tags or data tags"

        tag_ids = []
        for tag in tags:
            if tag.target_type != tag_type:
                raise TypeError(f"{tag} is not a {tag_type} type of tag.")

            tag_ids.append(tag.id)

        payload = {"tag_ids": tag_ids, "tag_type": tag_type}

        r = self.connexion.post(
            f"/sdk/dataset/version/{self.id}/tags/convert", data=orjson.dumps(payload)
        ).json()
        logger.info(
            f"Tags (of type {tag_type}) are being converted into classifications."
            "This operation can take some time, please wait for returned job to end."
        )
        return Job(self.connexion, r, version=1)

    @exception_handler
    @beartype
    def list_asset_tags(self) -> List[Tag]:
        """List asset tags created in this dataset version

        Examples:
            ```python
            tags = dataset_v0.list_asset_tags()
                assert tag_dog in tags
            ```

        Returns:
            A list of (Tag)
        """
        r = self.connexion.get(f"/sdk/dataset/version/{self.id}/tags").json()
        return list(map(partial(Tag, self.connexion), r["items"]))

    @beartype
    def train_test_split(
        self,
        prop: float = 0.8,
        random_seed: Optional[Any] = None,
        load_asset_page_size: int = 100,
    ) -> Tuple[MultiAsset, MultiAsset, Dict[str, list], Dict[str, list], List[Label]]:
        """Train test split

        Examples:
            ```python
            train_assets, eval_assets, count_train, count_eval, labels = dataset.train_test_split()
            ```
        Arguments:
            prop (float, optional): Percentage of data for training set. Defaults to 0.8.
            random_seed (Any, optional): Use a seed to ensures same result if run multiple times. Defaults to None.
            load_asset_page_size (int, optional): Page size when loading assets. Defaults to 100.

        Returns:
            A tuple with all of this information (
                list of train assets,
                list of test assets,
                dict of repartition of classes for train assets, with {"x": list of labels, "y":  list of label count},
                dict of repartition of classes for test assets, with {"x": list of labels, "y":  list of label count},
                list of labels
            )
        """
        if prop > 1 or prop < 0:
            raise ValueError("Please give a 'prop' parameter between 0 and 1")

        multi_assets, label_distributions, labels = self.split_into_multi_assets(
            [prop, 1.0 - prop], random_seed, load_asset_page_size
        )
        distributions = [
            {
                "x": list(label_repartition.keys()),
                "y": list(label_repartition.values()),
            }
            for label_repartition in label_distributions
        ]

        return (
            multi_assets[0],
            multi_assets[1],
            distributions[0],
            distributions[1],
            labels,
        )

    @beartype
    def train_test_val_split(
        self,
        ratios: List[float] = None,
        random_seed: Optional[Any] = None,
        load_asset_page_size: int = 100,
    ) -> Tuple[
        MultiAsset,
        MultiAsset,
        MultiAsset,
        Dict[str, list],
        Dict[str, list],
        Dict[str, list],
        List[Label],
    ]:
        """Split a DatasetVersion into 3 MultiAssets and return their label repartition.
        By default, will split with a ratio of 0.64, 0.16 and 0.20

        Examples:
            ```python
            train_assets, test_assets, val_assets, count_train, count_test, count_val, labels = dataset.train_test_val_split()
            ```
        Arguments:
            ratios (list of float, optional): Ratios of split used for training and eval set.
                Defaults to [0.64, 0.16, 0.20]
            random_seed (Any, optional): Use a seed to ensures same result if run multiple times. Defaults to None.
            load_asset_page_size (int, optional): Page size when loading assets. Defaults to 100.

        Returns:
            A tuple with all of this information (
                list of train assets,
                list of test assets
                list of val assets,
                dict of repartition of classes for train assets, with {"x": list of labels, "y":  list of label count},
                dict of repartition of classes for test assets, with {"x": list of labels, "y":  list of label count},
                dict of repartition of classes for val assets, with {"x": list of labels, "y":  list of label count},
                list of labels
            )
        """
        if not ratios:
            ratios = [0.64, 0.16, 0.20]

        if len(ratios) != 3:
            raise ValueError("Ratios list should be a list of 3 elements")

        multi_assets, label_distributions, labels = self.split_into_multi_assets(
            ratios, random_seed, load_asset_page_size
        )
        distributions = [
            {
                "x": list(label_repartition.keys()),
                "y": list(label_repartition.values()),
            }
            for label_repartition in label_distributions
        ]

        return (
            multi_assets[0],
            multi_assets[1],
            multi_assets[2],
            distributions[0],
            distributions[1],
            distributions[2],
            labels,
        )

    @beartype
    def split_into_multi_assets(
        self,
        ratios: List[Union[float, int]],
        random_seed: Optional[Any] = None,
        load_asset_page_size: int = 100,
    ) -> Tuple[List[MultiAsset], List[Dict[str, int]], List[Label]]:
        """Split dataset into multiple MultiAsset, proportionally according to given ratios.

        Examples:
            ```python
            split_assets, counts, labels = dataset.split_into_multi_assets([0.2, 0.5, 0.3])
            train_assets = split_assets[0]
            test_assets = split_assets[1]
            val_assets = split_assets[2]
            ```
        Arguments:
            ratios (list of float): Percentage of data that will go into each category.
                Will be normalized but sum should be equals to one if you don't want to be confused.
            random_seed (Any, optional): Use a seed to ensures same result if run multiple times. Defaults to None.
            load_asset_page_size (int, optional): Page size when loading assets. Defaults to 100.

        Returns:
            A tuple with all of this information (
                list of MultiAsset,
                dict of repartition of classes for each MultiAsset,
                list of labels
            )
        """
        if not ratios or len(ratios) < 2:
            raise NoDataError("Please give at least two proportions")

        # Fetch assets and annotation
        fetched_raw_assets = self._do_list_items_with_annotations(load_asset_page_size)

        # Fetch labels
        labels = self.list_labels()
        label_names = {str(label.id): label.name for label in labels}

        # Split annotations according to ratios
        ratios = AssetSplitter.normalize_ratios(ratios)
        AssetSplitter.shuffle_items(fetched_raw_assets, random_seed)
        split_items = AssetSplitter.split_with_ratios(fetched_raw_assets, ratios)

        multi_assets: List[MultiAsset] = []
        distributions: List[Dict[str, int]] = []
        for raw_items in split_items:
            assets, label_distribution = AssetSplitter.convert_items_to_assets(
                self.connexion, self.id, raw_items, label_names
            )
            multi_assets.append(MultiAsset(self.connexion, self.id, assets))
            distributions.append(label_distribution)

        return (
            multi_assets,
            distributions,
            labels,
        )

    @exception_handler
    @beartype
    def _do_list_items_with_annotations(self, load_asset_page_size: int):
        # Retrieve assets
        extended_assets = mlt.do_paginate(
            None, None, load_asset_page_size, self._do_list_assets_extended
        )
        if not extended_assets:
            raise NoDataError("No asset with annotation found in this dataset")

        # Retrieve annotations
        items = []
        for item in extended_assets:
            if not item["annotations"]:
                logger.debug(f"No annotation for asset {item['data']['filename']}")
                continue

            items.append(item)

        return items

    @exception_handler
    @beartype
    def _do_list_assets_extended(
        self, limit: int, offset: int
    ) -> Tuple[List[Dict], int]:
        params = {"limit": limit, "offset": offset}
        r = self.connexion.get(
            f"/sdk/dataset/version/{self.id}/assets/extended", params=params
        ).json()
        return r["items"], r["count"]
