import logging
import subprocess
import warnings
from functools import partial
from typing import Dict, List, Union
from uuid import UUID

import orjson
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning

from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.exceptions import BadConfigurationScanError
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.experiment import Experiment
from picsellia.sdk.scan_file import ScanFile
from picsellia.types.enums import RunStatus
from picsellia.types.schemas import RunSchema

logger = logging.getLogger("picsellia")
warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


class Run(Dao):
    def __init__(self, connexion: Connexion, data: dict) -> None:
        Dao.__init__(self, connexion, data)

    @property
    def scan_id(self) -> UUID:
        """UUID of the (Scan) holding this (Run)"""
        return self._scan_id

    @property
    def experiment_id(self) -> UUID:
        """UUID of the (Experiment) of this (Run)"""
        return self._experiment_id

    @property
    def order(self) -> int:
        """Order of this (Run)"""
        return self._order

    @property
    def parameters(self) -> Dict:
        """Parameters of this (Run)"""
        return self._parameters

    @property
    def status(self) -> RunStatus:
        """Status of this (Run)"""
        return self._status

    def __str__(self):
        return f"{Colors.BLUE}Run {self.order}{Colors.ENDC} of scan {self.scan_id} (id: {self.id})"

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/run/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def refresh(self, data: dict) -> RunSchema:
        schema = RunSchema(**data)
        self._order = schema.order
        self._parameters = schema.parameters
        self._status = schema.status
        self._scan_id = schema.scan_id
        self._experiment_id = schema.experiment_id
        return schema

    @exception_handler
    @beartype
    def update(self, status: Union[RunStatus, str]) -> None:
        """Update this run.

        Examples:
            ```python
            run.update(status=RunStatus.TERMINATED)
            ```
        """
        payload = {"status": RunStatus.validate(status)}
        r = self.connexion.patch(
            f"/sdk/run/{self.id}", data=orjson.dumps(payload)
        ).json()
        self.refresh(r)
        logger.info(f"{self} updated")

    @exception_handler
    @beartype
    def end(self) -> None:
        """End a run

        Examples:
            ```python
            run.end()
            ```
        """
        r = self.connexion.post(f"/sdk/run/{self.id}/end").json()
        self.refresh(r["run"])
        logger.info(f"{self} ended: {r['message']}")

    @exception_handler
    @beartype
    def get_script(
        self,
    ) -> ScanFile:
        """Retrieve the script of this run.

        Returns:
            A (ScanFile) object
        """
        r = self.connexion.get(f"/sdk/scan/{self.scan_id}").json()

        if "script_id" not in r or r["script_id"] is None:
            raise BadConfigurationScanError("This scan has no script.")

        r = self.connexion.get(f"/sdk/scan/file/{r['script_id']}").json()
        return ScanFile(self.connexion, r)

    @exception_handler
    @beartype
    def list_data_files(
        self,
    ) -> List[ScanFile]:
        """List all data files of this run

        Examples:
            ```python
            files = run.list_data_files()
            ```

        Returns:
            List of (ScanFile) object
        """
        r = self.connexion.get(f"/sdk/scan/{self.scan_id}/scanfiles").json()
        return list(map(partial(ScanFile, self.connexion), r["items"]))

    @exception_handler
    @beartype
    def install_requirements(self) -> None:
        """Install requirements from the run requirements dictionary.

        Examples:
            ```python
            run.install_requirements()
            ```
        """
        r = self.connexion.get(f"/sdk/scan/{self.scan_id}").json()
        requirements = r["requirements"]

        for module in requirements:
            name = (
                f"{module['package']}=={module['version']}"
                if module["version"] != ""
                else module["package"]
            )
            subprocess.call(["pip", "install", name])

    @exception_handler
    @beartype
    def get_experiment(self) -> Experiment:
        """Retrieve linked experiment

        Examples:
            ```python
            my_experiment = run.get_experiment()
            ```

        Returns:
            An (Experiment) object linked to this run
        """
        r = self.connexion.get(f"/sdk/experiment/{self.experiment_id}").json()
        return Experiment(self.connexion, r)

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete this run from the platform.

        :warning: **DANGER ZONE**: Be very careful here!

        Examples:
            ```python
            run.delete()
            ```
        """
        self.connexion.delete(f"/sdk/run/{self.id}")
        logger.info(f"{self} deleted.")
