import logging
import os
import warnings
from functools import partial
from typing import List, Optional, Union
from uuid import UUID

import orjson
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning

from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.exceptions import BadConfigurationScanError, FileNotFoundException
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.dataset_version import DatasetVersion
from picsellia.sdk.experiment import Experiment
from picsellia.sdk.model_version import ModelVersion
from picsellia.sdk.scan import Scan
from picsellia.types.enums import ObjectDataType
from picsellia.types.schemas import ProjectSchema
from picsellia.utils import filter_payload, generate_requirements_json

logger = logging.getLogger("picsellia")
warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


class Project(Dao):
    def __init__(self, connexion: Connexion, data: dict):
        Dao.__init__(self, connexion, data)

    @property
    def name(self) -> str:
        """Name of this (Project)"""
        return self._name

    def __str__(self):
        return f"{Colors.BOLD}Project '{self.name}' {Colors.ENDC} (id: {self.id})"

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/project/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def refresh(self, data: dict) -> ProjectSchema:
        schema = ProjectSchema(**data)
        self._name = schema.name
        return schema

    @exception_handler
    @beartype
    def get_resource_url_on_platform(self) -> str:
        """Get platform url of this resource.

        Examples:
            ```python
            print(foo_dataset.get_resource_url_on_platform())
            >>> "https://app.picsellia.com/project/62cffb84-b92c-450c-bc37-8c4dd4d0f590"
            ```

        Returns:
            Url on Platform for this resource
        """

        return f"{self.connexion.host}/project/{self.id}"

    @exception_handler
    @beartype
    def list_experiments(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
    ) -> List[Experiment]:
        """List all project's experiments

        Examples:
            ```python
            experiments = my_project.list_experiments()
            ```

        Returns:
            A list of (Experiment) objects, that you can manipulate
        """
        params = {"limit": limit, "offset": offset, "order_by": order_by}
        params = filter_payload(params)
        experiments_response = self.connexion.get(
            f"/sdk/project/{self.id}/experiments", params=params
        ).json()
        return list(
            map(partial(Experiment, self.connexion), experiments_response["items"])
        )

    @exception_handler
    @beartype
    def delete_all_experiments(self) -> None:
        """Delete all experiments of this project

        :warning: **DANGER ZONE**: Be very careful here!

        Examples:
            ```python
            my_project.delete_all_experiments()
            ```
        """
        payload = ["__all__"]
        self.connexion.delete(
            f"/sdk/project/{self.id}/experiments", data=orjson.dumps(payload)
        )
        logger.info(f"All experiments of {self} deleted.")

    @exception_handler
    @beartype
    def create_experiment(
        self,
        name: str,
        description: Optional[str] = None,
        base_experiment: Optional[Experiment] = None,
        base_model_version: Optional[ModelVersion] = None,
    ) -> Experiment:
        """Create an experiment in this project.

        You have the same options as when creating experiments from the UI.
            - You can attach a dataset
            - You can fork a Model (it will automatically attach its files and parameters
                to the experiment)
            - You can start from a previous experiment (it will automatically attach its files and parameters
                to the new experiment)

        Examples:
            ```python
            base_model_version = client.get_model("picsellia/yolov5")
            my_experiment = my_project.create_experiment(
                name="new_experiment",
                source=base_model,
            )
            ```
        Arguments:
            name (str, optional): Name of experiment. Defaults to None.
            description (str, optional): Description of experiment. Defaults to ''.
            base_experiment ((Experiment), optional): Previous experiment, if you want to base the new one on it.
                                             Defaults to None.
            base_model_version ((ModelVersion), optional): Model to use as source. Defaults to None.

        Returns:
             A new (Experiment) of this project
        """
        if description is None:
            description = f"A cool experiment {name} in project {self.name}"

        payload = {"name": name, "description": description}
        if base_experiment is not None:
            payload["base_experiment_id"] = base_experiment.id

        if base_model_version is not None:
            payload["base_model_version_id"] = base_model_version.id

        r = self.connexion.post(
            f"/sdk/project/{self.id}/experiments", data=orjson.dumps(payload)
        ).json()
        experiment = Experiment(self.connexion, r)
        logger.info(f"{experiment} created")
        return experiment

    @exception_handler
    @beartype
    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        private: Optional[bool] = None,
    ) -> None:
        """Update a project with a new name, description or privacy

        Examples:
            ```python
            my_project.update(description="This is a cool project")
            ```
        """
        payload = {"name": name, "description": description, "private": private}
        # Filter None values
        filtered_payload = filter_payload(payload)
        r = self.connexion.patch(
            f"/sdk/project/{self.id}", data=orjson.dumps(filtered_payload)
        ).json()
        self.refresh(r)
        logger.info(f"{self} updated.")

    @exception_handler
    @beartype
    def delete(self) -> None:
        """Delete a project.

        :warning: **DANGER ZONE**: Be very careful here!

        It will delete the project and all experiments linked.

        Examples:
            ```python
            my_project.delete()
            ```
        """
        self.connexion.delete(f"/sdk/project/{self.id}")
        logger.info(f"{self} deleted.")

    @exception_handler
    @beartype
    def get_experiment(self, name: str) -> Experiment:
        """Retrieve an existing experiment.

        Examples:
            ```python
            my_experiment = my_project.get_experiment("test_experiment")
            ```
        Arguments:
            name (str, optional): Experiment's name. Defaults to None.

        Raises:
            Exception: Experiment not found

        Returns:
            An (Experiment) object that you can manipulate
        """
        params = {"name": name}
        r = self.connexion.get(
            f"/sdk/project/{self.id}/experiments/find", params=params
        ).json()
        return Experiment(self.connexion, r)

    @exception_handler
    @beartype
    def get_experiment_by_id(self, id: Union[UUID, str]) -> Experiment:
        """Retrieve an existing experiment.

        Examples:
            ```python
            my_experiment = my_project.get_experiment("test_experiment")
            ```
        Arguments:
            id: Experiment's id. Defaults to None.

        Raises:
            Exception: Experiment not found

        Returns:
            An (Experiment) object that you can manipulate
        """
        if isinstance(id, str):
            id = UUID(id)
        params = {"id": id}
        r = self.connexion.get(
            f"/sdk/project/{self.id}/experiments/find", params=params
        ).json()
        return Experiment(self.connexion, r)

    @exception_handler
    @beartype
    def get_scan(self, name: str) -> Scan:
        """Retrieve an existing scan.

        Examples:
            ```python
            my_scan = my_project.get_scan("test_scan")
            ```
        Arguments:
            name (str, optional): Scan's name. Defaults to None.

        Returns:
            A (Scan) object that you can manipulate
        """
        params = {"name": name}
        r = self.connexion.get(
            f"/sdk/project/{self.id}/scans/find", params=params
        ).json()
        return Scan(self.connexion, r)

    @exception_handler
    @beartype
    def attach_dataset(self, dataset_version: DatasetVersion) -> None:
        """Attach a dataset version to this project.

        Retrieve or create a dataset version and attach it to this project.

        Examples:
            ```python
            foo_dataset = client.get_dataset("foo").get_version("first")
            my_project.attach_dataset(foo_dataset)
            ```
        Arguments:
            dataset_version (DatasetVersion): A dataset version to attach to the project.
        """
        payload = {"dataset_version_id": dataset_version.id}
        self.connexion.post(
            f"/sdk/project/{self.id}/datasets", data=orjson.dumps(payload)
        )
        logger.info(f"{dataset_version} successfully attached to {self}")

    @exception_handler
    @beartype
    def detach_dataset(self, dataset_version: DatasetVersion) -> None:
        """Detach a dataset version from this project.

        Examples:
            ```python
            foo_dataset = client.get_dataset("foo").get_version("first")
            my_project.attach_dataset(foo_dataset)
            my_project.detach_dataset(foo_dataset)
            ```
        Arguments:
            dataset_version (DatasetVersion): A dataset version to attach to the project.
        """
        payload = [dataset_version.id]
        self.connexion.delete(
            f"/sdk/project/{self.id}/datasets", data=orjson.dumps(payload)
        )
        logger.info(
            f"{dataset_version} was successfully detached from this project {self}"
        )

    @exception_handler
    @beartype
    def list_dataset_versions(self) -> List[DatasetVersion]:
        """Retrieve all dataset versions attached to this project

        Examples:
            ```python
            datasets = my_project.list_dataset_versions()
            ```

        Returns:
            A list of (DatasetVersion) object attached to this project
        """
        r = self.connexion.get(f"/sdk/project/{self.id}/datasets").json()
        return list(map(partial(DatasetVersion, self.connexion), r["items"]))

    @exception_handler
    @beartype
    def create_scan(
        self,
        name: str,
        metric_name: str,
        metric_goal: str,
        strategy: str,
        execution_type: str,
        execution_max_worker: int = 1,
        max_run: int = 1,
        requirements: Union[List[dict], str, None] = None,
        parameters: Optional[dict] = None,
        early_stopping: Optional[dict] = None,
        image: Optional[str] = None,
        path_script_file: Optional[str] = None,
        files: Optional[List[str]] = None,
        base_model: Optional[ModelVersion] = None,
        base_dataset: Optional[DatasetVersion] = None,
    ) -> Scan:
        """Initialize a new scan.

        See full documentation https://docs.picsellia.com/experiments/hyperparameter-tuning/config

        Returns:
            A (Scan) object that you can manipulate
        """
        assert (image is None and path_script_file is not None) or (
            image is not None and path_script_file is None
        ), "Please specify image or path_script_file but not both."

        payload = {
            "name": name,
            "metric": {"name": metric_name, "goal": metric_goal},
            "strategy": strategy,
            "execution": {
                "type": execution_type,
                "max_worker": execution_max_worker,
            },
            "max_run": max_run,
            "parameters": parameters if parameters else {},
        }

        if path_script_file is not None:
            payload["script"] = self._upload_scan_file(path_script_file)

        if image is not None:
            payload["image"] = image

        if isinstance(requirements, str):
            payload["requirements"] = generate_requirements_json(requirements)
        else:
            payload["requirements"] = requirements if requirements else []

        if files:
            payload["files"] = []
            for path in files:
                payload["files"].append(self._upload_scan_file(path))

        if early_stopping is not None:
            payload["early_stopping"] = early_stopping

        if base_model is not None:
            payload["base_model_id"] = base_model.id

        if base_dataset is not None:
            payload["base_dataset_id"] = base_dataset.id

        r = self.connexion.post(
            f"/sdk/project/{self.id}/scans", data=orjson.dumps(payload)
        ).json()
        return Scan(self.connexion, r)

    def _upload_scan_file(self, path: str):
        scan_file_filename = os.path.split(path)[-1]

        if not os.path.exists(path):
            raise FileNotFoundException(f"This file {path} does not exists")
        scan_file_object_name = self.connexion.generate_project_object_name(
            scan_file_filename, ObjectDataType.SCAN_FILE, self.id
        )
        _, large, _ = self.connexion.upload_file(scan_file_object_name, path)

        return {
            "name": scan_file_filename,
            "object_name": scan_file_object_name,
            "large": large,
        }

    @exception_handler
    @beartype
    def create_scan_from_config(
        self,
        name: str,
        config: dict,
        image: Optional[str] = None,
        path_script_file: Optional[str] = None,
        files: Optional[List[str]] = None,
        base_model: Optional[ModelVersion] = None,
        base_dataset: Optional[DatasetVersion] = None,
    ) -> Scan:
        """Create scan from a config dictionary.

        Arguments:
            name (str): Name of the scan
            config (dict): Config dictionary
            image (str, optional): Docker image name. Defaults to None.
            path_script_file (str, optional): Path of script file. Default will use default picsellia image.
            files (List[str], optional): Some path files to add to scan. Defaults to [].
            base_model (ModelVersion, optional): Base model version of this scan. Defaults to None.
            base_dataset (DatasetVersion, optional): Base dataset version of this scan. Defaults to None.

        Returns:
            A (Scan) object
        """
        try:
            metric_name = config["metric"]["name"]
            metric_goal = config["metric"]["goal"]
            strategy = config["strategy"]
            execution_type = config["execution"]["type"]
            execution_max_worker = (
                config["execution"]["max_worker"]
                if "max_worker" in config["execution"]
                else 1
            )
            max_run = config["max_run"] if "max_run" in config else 1
            requirements = config["requirements"] if "requirements" in config else []
            parameters = config["parameters"]
            early_stopping = (
                config["early_stopping"] if "early_stopping" in config else None
            )
        except KeyError as e:
            raise BadConfigurationScanError(
                f"This configuration can't be used to create a scan: {e}"
            )

        return self.create_scan(
            name,
            metric_name,
            metric_goal,
            strategy,
            execution_type,
            execution_max_worker,
            max_run,
            requirements,
            parameters,
            early_stopping,
            image,
            path_script_file,
            files,
            base_model,
            base_dataset,
        )

    @exception_handler
    @beartype
    def list_scans(self) -> List[Scan]:
        """Retrieve all scans of this project

        Examples:
            ```python
            scans = my_project.list_scans()
            ```

        Returns:
            A list of (Scan) object attached to this project
        """
        r = self.connexion.get(f"/sdk/project/{self.id}/scans").json()
        return list(map(partial(Scan, self.connexion), r["items"]))
