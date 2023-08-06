import logging
import mimetypes
import os
import warnings
from io import BufferedReader
from pathlib import Path
from typing import IO, Any, BinaryIO, Dict, Iterable, Mapping, Optional, Tuple, Union
from uuid import UUID

import orjson
import requests
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from picsellia_connexion_services import TokenServiceConnexion
from requests.exceptions import ConnectionError

import picsellia.exceptions as exceptions
from picsellia import __version__
from picsellia.decorators import exception_handler, retry
from picsellia.types.enums import ObjectDataType
from picsellia.utils import (
    handle_response,
    print_line_return,
    print_start_section,
    print_stop_section,
)

warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)

logger = logging.getLogger("picsellia")


class Connexion(TokenServiceConnexion):
    def __init__(
        self, host: str, api_token: str, content_type: str = "application/json"
    ) -> None:
        super().__init__(
            host, api_token, authorization_key="Bearer", content_type=content_type
        )
        self._connector_id = None
        self._organization_id = None
        self.add_header("User-Agent", f"Picsellia-SDK/{__version__}")

    @property
    def connector_id(self):
        if self._connector_id is None:
            raise exceptions.NoConnectorFound(
                "This organization has no default connector, and connect retrieve and upload files."
            )
        return self._connector_id

    @connector_id.setter
    def connector_id(self, value):
        self._connector_id = value

    @property
    def organization_id(self):
        return self._organization_id

    @organization_id.setter
    def organization_id(self, value):
        self._organization_id = value
        self.add_header("X-Picsellia-Organization", str(self._organization_id))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Connexion):
            return self.host == __o.host and self.api_token == __o.api_token

        return False

    @handle_response
    def get(self, path: str, params: Optional[dict] = None, stream=False):
        return super().get(path=path, params=params, stream=stream)

    @handle_response
    def xget(
        self,
        path: str,
        data: Union[
            None, str, bytes, Mapping[str, Any], Iterable[Tuple[str, str, None]], IO
        ] = None,
        params: Optional[dict] = None,
        stream=False,
    ):
        return super().xget(path=path, data=data, params=params, stream=stream)

    @handle_response
    def post(
        self,
        path: str,
        data: Union[
            None, str, bytes, Mapping[str, Any], Iterable[Tuple[str, str, None]], IO
        ] = None,
        params: Optional[dict] = None,
        files: Optional[Any] = None,
    ):
        return super().post(path=path, data=data, params=params, files=files)

    @handle_response
    def put(
        self,
        path: str,
        data: Union[
            None, str, bytes, Mapping[str, Any], Iterable[Tuple[str, str, None]], IO
        ] = None,
        params: Optional[dict] = None,
    ):
        return super().put(path=path, data=data, params=params)

    @handle_response
    def patch(
        self,
        path: str,
        data: Union[
            None, str, bytes, Mapping[str, Any], Iterable[Tuple[str, str, None]], IO
        ] = None,
        params: Optional[dict] = None,
    ):
        return super().patch(path=path, data=data, params=params)

    @handle_response
    def delete(
        self,
        path: str,
        data: Union[
            None, str, bytes, Mapping[str, Any], Iterable[Tuple[str, str, None]], IO
        ] = None,
        params: Optional[dict] = None,
    ):
        return super().delete(path=path, data=data, params=params)

    ##############################################################
    # ------------------------- UPLOAD ------------------------- #
    ##############################################################
    @exception_handler
    @beartype
    def _generate_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        connector_id: Optional[UUID] = None,
        context: Optional[Dict[str, UUID]] = None,
    ) -> str:
        if connector_id is None:
            connector_id = self.connector_id

        payload = {"filename": filename, "type": object_name_type}
        if context:
            payload["context"] = context

        r = self.post(
            path=f"/sdk/organization/{self.organization_id}/connector/{connector_id}/generate_object_name",
            data=orjson.dumps(payload),
        ).json()
        return r["object_name"]

    @beartype
    def generate_data_object_name(
        self, filename: str, connector_id: Optional[UUID] = None
    ):
        return self._generate_object_name(filename, ObjectDataType.DATA, connector_id)

    @beartype
    def generate_job_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        job_id: UUID,
        connector_id: Optional[UUID] = None,
    ):
        if object_name_type not in [ObjectDataType.LOGGING]:
            raise RuntimeError(
                f"Cannot generate job object name with type {object_name_type}"
            )
        return self._generate_object_name(
            filename,
            object_name_type,
            connector_id=connector_id,
            context={"job_id": job_id},
        )

    @beartype
    def generate_experiment_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        experiment_id: UUID,
        connector_id: Optional[UUID] = None,
    ):
        if object_name_type not in (
            ObjectDataType.ARTIFACT,
            ObjectDataType.LOG_IMAGE,
            ObjectDataType.LOGGING,
        ):
            raise RuntimeError(
                f"Cannot generate experiment object name with type {object_name_type}"
            )
        return self._generate_object_name(
            filename,
            object_name_type,
            connector_id=connector_id,
            context={"experiment_id": experiment_id},
        )

    @beartype
    def generate_model_version_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        model_version_id: UUID,
        connector_id: Optional[UUID] = None,
    ):
        if object_name_type not in (
            ObjectDataType.MODEL_THUMB,
            ObjectDataType.MODEL_FILE,
        ):
            raise RuntimeError(
                f"Cannot generate model version object name with type {object_name_type}"
            )
        return self._generate_object_name(
            filename,
            object_name_type,
            connector_id=connector_id,
            context={"model_version_id": model_version_id},
        )

    @beartype
    def generate_project_object_name(
        self,
        filename: str,
        object_name_type: ObjectDataType,
        project_id: UUID,
        connector_id: Optional[UUID] = None,
    ):
        if object_name_type != ObjectDataType.SCAN_FILE:
            raise RuntimeError(
                f"Cannot generate project object name with type {object_name_type}"
            )
        return self._generate_object_name(
            filename,
            object_name_type,
            connector_id=connector_id,
            context={"project_id": project_id},
        )

    @exception_handler
    @beartype
    def _init_upload(self, path: Union[str, Path]) -> Tuple[bool, str]:
        if not os.path.isfile(path):
            raise exceptions.FileNotFoundException(f"{path} not found")

        is_large = Path(path).stat().st_size > 5 * 1024 * 1024
        content_type = mimetypes.guess_type(path, strict=False)[0]
        if content_type is None:
            content_type = "text/plain"

        return is_large, content_type

    @exception_handler
    @beartype
    def _generate_presigned_url(
        self, object_name: str, content_type: str, connector_id: UUID
    ):
        payload = {"object_name": object_name, "content_type": content_type}
        r = self.post(
            path=f"/sdk/connector/{connector_id}/generate_presigned_url",
            data=orjson.dumps(payload),
        )

        if r.status_code != 200:
            raise exceptions.DistantStorageError("Errors while getting a presigned url")

        r = r.json()["presigned_url_data"]
        if "url" not in r:
            raise exceptions.DistantStorageError(
                "Errors while getting a presigned url. Unparsable response"
            )

        return r

    @retry((KeyError, ValueError, exceptions.PicselliaError), total_tries=3)
    @exception_handler
    @beartype
    def _do_upload_file(
        self, object_name: str, path: Union[str, Path], presigned_url_data: dict
    ) -> requests.Response:
        if not os.path.isfile(path):
            raise exceptions.FileNotFoundException(f"{path} not found")

        with open(path, "rb") as file:
            try:
                response = requests.post(
                    url=presigned_url_data["url"],
                    data=presigned_url_data["fields"],
                    files={"file": (object_name, file)},
                )
            except Exception:
                raise exceptions.NetworkError("Impossible to upload file")

        if response.status_code != 204:
            logging.error(
                f"Could not upload {path} into S3. Status code: {response.status_code}"
            )
            raise exceptions.DistantStorageError(f"Could not upload {path} into S3")

        return response

    @exception_handler
    @beartype
    def upload_file(
        self,
        object_name: str,
        path: Union[str, Path],
        connector_id: Optional[UUID] = None,
    ) -> Tuple[requests.Response, bool, str]:
        """Upload a single file to the server.
        If file is bigger than 5Mb, it will send it by multipart.

        Arguments:
            path (str): [Absolute path to the file]
            object_name (str): [Bucket prefix s3]
            connector_id (UUID): Use this custom connector id in some case
        """
        if connector_id is None:
            connector_id = self.connector_id

        is_large, content_type = self._init_upload(path)

        if is_large:
            try:
                return (
                    self._upload_large_file(object_name, path, connector_id),
                    is_large,
                    content_type,
                )
            except exceptions.BadRequestError:
                logger.warning(
                    "This file is large but it is impossible to use multipart for this upload."
                    "Trying to upload in only one upload."
                )

        presigned_url_data = self._generate_presigned_url(
            object_name, content_type, connector_id
        )

        response: requests.Response = self._do_upload_file(
            object_name, path, presigned_url_data
        )

        if response.status_code >= 300:
            raise exceptions.UploadFailed(
                "Something wrong happened while storing this file"
            )

        return response, is_large, content_type

    @exception_handler
    @beartype
    def _init_multipart(self, object_name: str, connector_id: UUID) -> str:
        """Initialize a multipart push

        Arguments:
            object_name (str): object name to download

        Returns:
            The upload id if everything went well
        """

        payload = {"object_name": object_name}

        r = self.post(
            path=f"/sdk/connector/{connector_id}/init_multipart_upload",
            data=orjson.dumps(payload),
        )

        r = r.json()
        if "upload_id" not in r:
            raise exceptions.DistantStorageError(
                "Response when initiating multipart is unparsable"
            )

        return r["upload_id"]

    @exception_handler
    @beartype
    def _get_url_for_part(
        self, object_name: str, upload_id: str, no_part: int, connector_id: UUID
    ) -> str:
        """Get a pre-signed url to upload a part of a large file"""
        payload = {
            "object_name": object_name,
            "upload_id": upload_id,
            "part_no": no_part,
        }
        r = self.post(
            path=f"/sdk/connector/{connector_id}/generate_part_presigned_url",
            data=orjson.dumps(payload),
        )

        r = r.json()
        if "url" not in r:
            raise exceptions.NetworkError(
                "Response when getting an url for a part is unparsable"
            )

        return r["url"]

    @exception_handler
    @beartype
    def _upload_parts(
        self,
        object_name: str,
        upload_id: str,
        path: Union[str, Path],
        connector_id: UUID,
    ) -> list:
        if not os.path.exists(path):
            raise exceptions.FileNotFoundException(
                "Impossible to upload part in an empty filepath"
            )

        max_size = 5 * 1024 * 1024
        file_size = os.path.getsize(path)
        upload_by = int(file_size / max_size) + 1
        print_start_section()
        with open(path, "rb") as file:
            parts = []
            for part in range(1, upload_by + 1):
                etag = self._do_upload_one_part(
                    object_name, upload_id, part, connector_id, file, max_size
                )
                parts.append({"ETag": etag, "PartNumber": part})
        print_stop_section()
        print_line_return()
        return parts

    @exception_handler
    @beartype
    def _do_upload_one_part(
        self,
        object_name: str,
        upload_id: str,
        part: int,
        connector_id: UUID,
        # Ensures backport with beartype and python
        file: Union[BufferedReader, BinaryIO],
        max_size: int,
    ):
        try:
            url = self._get_url_for_part(object_name, upload_id, part, connector_id)
            file_data = file.read(max_size)
            res = requests.put(url, data=file_data)
        except Exception:
            raise exceptions.DistantStorageError("Impossible to get an url for part")

        if res.status_code != 200:
            raise exceptions.DistantStorageError(
                f"Impossible to put part no {part}\n because {res.text}"
            )
        return res.headers["ETag"]

    @exception_handler
    @beartype
    def _complete_part_upload(
        self, object_name: str, upload_id: str, parts: list, connector_id: UUID
    ) -> requests.Response:
        """
        Complete the upload a part of a large file
        """
        payload = {
            "object_name": object_name,
            "upload_id": upload_id,
            "parts": parts,
        }
        try:
            r = self.post(
                path=f"/sdk/connector/{connector_id}/complete_part_upload",
                data=orjson.dumps(payload),
            )
        except Exception as e:
            raise exceptions.NetworkError(f"Impossible to complete part url : {e}")

        return r

    @exception_handler
    @beartype
    def _upload_large_file(
        self, object_name: str, path: Union[str, Path], connector_id: UUID
    ) -> requests.Response:
        """Upload a single large file to the server. It will be sent by multipart.

        Arguments:
            object_name (str): [Bucket prefix s3]
            path (str): [Absolute path to the file]
            connector_id (UUID): [Connector id in Platform to use. Defaults to organization default connector]
        """
        if connector_id is None:
            connector_id = self.connector_id

        upload_id: str = self._init_multipart(object_name, connector_id)
        parts: list = self._upload_parts(object_name, upload_id, path, connector_id)
        response: requests.Response = self._complete_part_upload(
            object_name, upload_id, parts, connector_id
        )

        if response.status_code >= 300:
            raise exceptions.UploadFailed(
                "Something wrong happened while storing this file"
            )

        return response

    ##############################################################
    # ------------------------ DOWNLOAD ------------------------ #
    ##############################################################
    @exception_handler
    @beartype
    def init_download(
        self, object_name: str, connector_id: Optional[UUID] = None
    ) -> str:
        """Retrieve a presigned url of this object name in order to download it"""
        if connector_id is None:
            connector_id = self.connector_id

        payload = {"object_name": object_name}
        r = self.post(
            path=f"/sdk/connector/{connector_id}/retrieve_presigned_url",
            data=orjson.dumps(payload),
        )

        if r.status_code != 200:
            raise exceptions.DistantStorageError("Errors while getting a presigned url")

        r = r.json()
        if "presigned_url" not in r:
            raise exceptions.DistantStorageError(
                "Errors while getting a presigned url. Unparsable response"
            )

        return r["presigned_url"]

    @exception_handler
    @beartype
    def do_download_file(
        self,
        path: Union[str, Path],
        url: str,
        is_large: bool,
        force_replace: bool,
        retry_count: int = 1,
    ) -> bool:
        try:
            return self._do_download_file(path, url, is_large, force_replace)
        except (exceptions.NetworkError, ConnectionError) as e:
            if retry_count <= 0:
                raise exceptions.DownloadError(
                    f"Could not download {url} into {path}"
                ) from e
            logger.error(
                f"Could not download because of a NetworkError. Retrying to download {path}"
            )
            return self.do_download_file(
                path,
                url,
                is_large,
                force_replace,
                retry_count=retry_count - 1,
            )

    @exception_handler
    @beartype
    def _do_download_file(
        self,
        path: Union[str, Path],
        url: str,
        is_large: bool,
        force_replace: bool,
    ) -> bool:
        """Retrieve a presigned url of this object name in order to download it"""
        if os.path.exists(path) and not force_replace:
            return False

        parent_path = Path(path).parent.absolute()
        if not os.path.exists(parent_path):
            os.makedirs(parent_path)

        response = requests.get(url, stream=is_large)

        if response.status_code == 429 or (500 <= response.status_code < 600):
            raise exceptions.NetworkError(
                f"Response status code is {response.status_code}. Could not get {url}"
            )

        response.raise_for_status()

        total_length = response.headers.get("content-length")
        if total_length is None:
            raise exceptions.NetworkError(
                "Downloaded content is empty but response is 200"
            )

        with open(path, "wb") as handler:
            if not is_large:
                handler.write(response.content)
            else:
                for data in response.iter_content(chunk_size=4096):
                    handler.write(data)

        return True
