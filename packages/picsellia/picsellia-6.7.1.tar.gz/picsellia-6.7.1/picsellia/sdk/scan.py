import logging
import warnings
from functools import partial
from typing import Dict, List, Optional, Union
from uuid import UUID

import orjson
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning

from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.exceptions import BadConfigurationScanError
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.dataset_version import DatasetVersion
from picsellia.sdk.model_version import ModelVersion
from picsellia.sdk.run import Run
from picsellia.sdk.scan_file import ScanFile
from picsellia.types.schemas import ScanSchema
from picsellia.utils import filter_payload, generate_requirements_json

logger = logging.getLogger("picsellia")
warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


class Scan(Dao):
    def __init__(self, connexion: Connexion, data: dict) -> None:
        Dao.__init__(self, connexion, data)

    @property
    def name(self) -> str:
        """Name of this (Scan)"""
        return self._name

    def __str__(self):
        return f"{Colors.BLUE}Scan '{self.name}' {Colors.ENDC} (id: {self.id})"

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/scan/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def refresh(self, data: dict) -> ScanSchema:
        schema = ScanSchema(**data)
        self._name = schema.name
        return schema

    @exception_handler
    @beartype
    def update(
        self,
        name: Optional[str] = None,
        metric_name: Optional[str] = None,
        metric_goal: Optional[str] = None,
        requirements: Union[List[Dict], str, None] = None,
        base_model: Optional[ModelVersion] = None,
        base_dataset: Optional[DatasetVersion] = None,
        script: Optional[ScanFile] = None,
        image: Optional[str] = None,
    ) -> None:
        """Update this data source with a new name.

        Examples:
            ```python
            sdk_source.update(name="new name")
            ```
        """
        payload = {
            "name": name,
            "metric_name": metric_name,
            "metric_goal": metric_goal,
            "image": image,
        }
        filtered_payload = filter_payload(payload)
        if base_model is not None:
            filtered_payload["base_model_id"] = base_model.id
        if base_dataset is not None:
            filtered_payload["base_dataset_id"] = base_dataset.id
        if script is not None:
            filtered_payload["script_id"] = script.id
        if isinstance(requirements, str):
            filtered_payload["requirements"] = generate_requirements_json(requirements)
        elif isinstance(requirements, List):
            filtered_payload["requirements"] = requirements
        r = self.connexion.patch(
            f"/sdk/scan/{self.id}", data=orjson.dumps(filtered_payload)
        ).json()
        self.refresh(r)
        logger.info(f"{self} updated")

    @exception_handler
    @beartype
    def launch(self, gpus: int = 1) -> None:
        """Distribute runs remotely for this scan.

        :information-source: The remote environment has to be setup prior launching the experiment.
        It defaults to our remote training engine.

        Examples:
            ```python
            scan.launch()
            ```
        """
        payload = {
            "gpus": gpus,
        }
        self.connexion.post(f"/sdk/scan/{self.id}/launch", data=orjson.dumps(payload))
        logger.info(f"{self} launched.")

    @exception_handler
    @beartype
    def list_runs(self) -> List[Run]:
        """Retrieve all runs of this scan

        Examples:
            ```python
            scan.list_runs()
            ```

        Returns:
            A list of (Run) object manipulable
        """
        r = self.connexion.get(f"/sdk/scan/{self.id}/runs").json()
        return list(map(partial(Run, self.connexion), r["items"]))

    @exception_handler
    @beartype
    def get_run(self, order: int) -> Run:
        """Retrieve a run object by its order in its scan

        Examples:
            ```python
            scan.get_run(1)
            ```
        Arguments:
            order (int): order of the run

        Returns:
            A (Run) object manipulable
        """
        params = {"order": order}
        r = self.connexion.get(f"/sdk/scan/{self.id}/runs/find", params=params).json()
        return Run(self.connexion, r)

    @exception_handler
    @beartype
    def get_run_by_id(self, id: Union[UUID, str]) -> Run:
        """Retrieve a run object by its id.

        Examples:
            ```python
            scan.get_run_by_id("cb750009-4e09-42bb-8c84-cc78aa004bf0")
            ```
        Arguments:
            id (str): id (primary key) of the run on Picsellia

        Returns:
            A (Run) object manipulable
        """
        if isinstance(id, str):
            id = UUID(id)
        params = {"id": id}
        r = self.connexion.get(f"/sdk/scan/{self.id}/runs/find", params=params).json()
        return Run(self.connexion, r)

    @exception_handler
    @beartype
    def get_next_run(self) -> Run:
        """Get next available Run for Scan.

        Examples:
            ```python
            scan.get_next_run()
            ```

        Returns:
            A (Run) object manipulable
        """
        r = self.connexion.get(f"/sdk/scan/{self.id}/run/next").json()
        return Run(self.connexion, r)

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete this scan from the platform.

        :warning: **DANGER ZONE**: Be very careful here!

        Examples:
            ```python
            scan.delete()
            ```
        """
        self.connexion.delete(f"/sdk/scan/{self.id}")
        logger.info(f"{self} deleted.")

    @exception_handler
    @beartype
    def get_script(
        self,
    ) -> ScanFile:
        """Retrieve the script of this scan.

        Returns:
            A (ScanFile) object
        """
        r = self.sync()

        if "script_id" not in r or r["script_id"] is None:
            raise BadConfigurationScanError("This scan has no script.")

        r = self.connexion.get(f"/sdk/scan/file/{r['script_id']}").json()
        return ScanFile(self.connexion, r)

    @exception_handler
    @beartype
    def list_data_files(
        self,
    ) -> List[ScanFile]:
        """List all data files of this scan

        Examples:
            ```python
            files = scan.list_data_files()
            ```

        Returns:
            List of (ScanFile) object
        """
        r = self.connexion.get(f"/sdk/scan/{self.id}/scanfiles").json()
        return list(map(partial(ScanFile, self.connexion), r["items"]))
