import logging
import os
import warnings
from functools import partial
from typing import List, Optional, Union
from uuid import UUID

import orjson
from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning

import picsellia
from picsellia import utils
from picsellia.colors import Colors
from picsellia.decorators import exception_handler
from picsellia.exceptions import PicselliaError
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.datalake import Datalake
from picsellia.sdk.dataset import Dataset
from picsellia.sdk.dataset_version import DatasetVersion
from picsellia.sdk.datasource import DataSource
from picsellia.sdk.deployment import Deployment
from picsellia.sdk.experiment import Experiment
from picsellia.sdk.job import Job
from picsellia.sdk.model import Model
from picsellia.sdk.model_version import ModelVersion
from picsellia.sdk.project import Project
from picsellia.sdk.tag import Tag
from picsellia.services.datasource import DataSourceService
from picsellia.types.enums import Framework, InferenceType, TagTarget
from picsellia.types.schemas import OrganizationSchema
from picsellia.utils import filter_payload

warnings.filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)

logger = logging.getLogger("picsellia")


class Client:
    """Picsellia SDK Client can be used to communicate with Picsellia services.
    You need an API Token, available on web platform in Profile Settings > Token.
    From this client object, you will be able to retrieve python objects representing your data in the platform.

    Examples:
        ```python
        client = Client(api_token="a0c9f3bbf7e8bc175494fc44bfc6f89aae3eb9d0")
        ```

    Arguments:
        api_token (str, optional): your api token, that can be found on the web platform.
            Defaults to None, client will try to find it into your environment variable as 'PICSELLIA_TOKEN'
        organization_id: (str or UUID, optional): Specify an organization to connect to by giving its id.
            Defaults to None, you will be connected to your main Organization.
        organization_name: (str, optional): Specify an organization to connect to by giving its name.
            If id is also given, client will use organization_id.
            Defaults to None, you will be connected to your main Organization.
        host (str, optional): Define a custom host used for platform.
            Defaults to our Picsellia environment "https://app.picsellia.com".
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        organization_id: Union[str, UUID, None] = None,
        organization_name: Optional[str] = None,
        host: str = "https://app.picsellia.com",
    ):
        if api_token is None:
            if "PICSELLIA_TOKEN" in os.environ:
                token = os.environ["PICSELLIA_TOKEN"]
            else:
                raise Exception(
                    "Please set up the PICSELLIA_TOKEN environment variable or specify your token"
                )
        else:
            token = api_token

        self.connexion = Connexion(host, token)

        # Ping platform to get username and version matching api_token
        try:
            ping_response = self.connexion.get("/sdk/home/ping").json()
        except Exception as e:  # pragma: no cover
            raise PicselliaError(
                "Cannot connect to the platform. Please check api_token, organization and host given.\n"
                f"Error is : {e}"
            )

        sdk_version = ping_response["sdk_version"]

        if sdk_version != picsellia.__version__:  # pragma: no cover
            logger.warning(
                f"\033[93mYou are using an outdated version of the picsellia package ({picsellia.__version__})\033[0m"
            )
            logger.warning(
                f"\033[93mPlease consider upgrading to {sdk_version} with pip install picsellia --upgrade\033[0m"
            )

        if organization_id is not None:
            if isinstance(organization_id, str):
                organization_id = UUID(organization_id)
            self._id = organization_id
            self.sync()
        elif organization_name is not None:
            r = self.connexion.get(
                path="/sdk/organizations/find", params={"name": organization_name}
            ).json()
            self._id = r["id"]
            self.sync()
        else:
            self._id = ping_response["default_organization"]
            self.sync()

        if self._id == ping_response["default_organization"]:
            message = "your"
        else:  # pragma: no cover
            message = self.name + "'s"

        username = ping_response["username"]
        logger.info(f"Hi {Colors.BLUE}{username}{Colors.ENDC}, welcome back. 🥑")
        logger.info(f"Workspace: {Colors.YELLOW}{message}{Colors.ENDC} organization.")

    def __str__(self) -> str:
        return f"Client initialized for organization `{self.name}`"

    def __enter__(self):
        self.connexion = self.connexion.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connexion.__exit__(exc_type, exc_val, exc_tb)

    @property
    def id(self) -> UUID:
        """Organization UUID connected with this (Client)"""
        return self._id

    @property
    def name(self) -> str:
        """Organization name connected with this (Client)"""
        return self._name

    @exception_handler
    @beartype
    def sync(self) -> dict:
        r = self.connexion.get(f"/sdk/organization/{self.id}").json()
        self.refresh(r)
        return r

    @exception_handler
    @beartype
    def refresh(self, data: dict) -> OrganizationSchema:
        schema = OrganizationSchema(**data)
        self._name = schema.name
        if schema.default_connector_id is not None:
            self.connexion.connector_id = schema.default_connector_id
            self.connexion.organization_id = schema.id
        return schema

    @exception_handler
    @beartype
    def get_resource_url_on_platform(self) -> str:
        """Get platform url of this resource.

        Examples:
            ```python
            print(foo_dataset.get_resource_url_on_platform())
            >>> "https://app.picsellia.com/organization/62cffb84-b92c-450c-bc37-8c4dd4d0f590"
            ```

        Returns:
            Url on Platform for this resource
        """

        return f"{self.connexion.host}/organization/{self.id}"

    @exception_handler
    @beartype
    def get_datalake(self) -> Datalake:
        """Retrieve default datalake of this organization

        Examples:
            ```python
            datalake = client.get_datalake()
            ```

        Returns:
            The (Datalake) of the client that you are using
        """
        # Retrieve default datalake
        r = self.connexion.get(f"/sdk/organization/{self.id}/datalake").json()

        return Datalake(self.connexion, self.id, r)

    @exception_handler
    @beartype
    def list_datalakes(self) -> List[Datalake]:
        """Retrieve all datalakes linked to this organization

        Examples:
            ```python
            datalakes = client.list_datalakes()
            ```

        Returns:
            List of (Datalake) of the client that you are using
        """
        # Retrieve default datalake
        r = self.connexion.get(f"/sdk/organization/{self.id}/datalakes").json()
        return list(map(partial(Datalake, self.connexion, self.id), r["items"]))

    @exception_handler
    @beartype
    def create_dataset(
        self,
        name: str,
        description: str = "",
        private: bool = True,
    ) -> Dataset:
        """Create a (Dataset) in this organization.

        This method allows user to create a dataset into the organization currently connected.
        A dataset can then be versioned into (DatasetVersion).
        User can specify name of the dataset, a description and if the dataset is private or not.

        Examples:
            Create a dataset named datatest with data from datalake and version it
            ```python
            foo_dataset = client.create_dataset('foo_dataset')
            foo_dataset_version_1 = foo_dataset.create_version('first')
            some_data = client.get_datalake().list_data(limit=10)
            foo_dataset_version_1.add_data(some_data)
            ```

        Arguments:
            name (str): Name of the dataset. It must be unique in the organization.
            description (str, optional): A description of the dataset. Defaults to ''.
            private (bool, optional): Specify if the dataset is private. Defaults to True.

        Returns:
            A (Dataset) that you can manipulate, connected to Picsellia
        """
        assert name != "", "Dataset name can't be empty"

        payload = {"name": name, "description": description, "private": private}
        r = self.connexion.post(
            f"/sdk/organization/{self.id}/datasets",
            data=orjson.dumps(payload),
        ).json()
        return Dataset(self.connexion, r)

    @exception_handler
    @beartype
    def get_dataset(self, name: str) -> Dataset:
        """Retrieve a dataset by its name

        Examples:
            ```python
            foo_dataset = client.get_dataset('datatest')
            foo_dataset_version = foo_dataset.get_version('first')
            ```

        Arguments:
            name (str): Name of the dataset

        Returns:
            A (Dataset) that you can use and manipulate
        """
        params = {"name": name}
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/datasets/find",
            params=params,
        ).json()
        return Dataset(self.connexion, r)

    @exception_handler
    @beartype
    def get_dataset_by_id(self, id: Union[UUID, str]) -> Dataset:
        """Get a dataset by its id

        Examples:
            ```python
            dataset = client.get_dataset('918351d2-3e96-4970-bb3b-420f33ded895')
            ```

        Arguments:
            id (str): id of the dataset to retrieve

        Returns:
            A (Dataset) that you can use and manipulate
        """
        if isinstance(id, str):
            id = UUID(id)
        params = {"id": id}
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/datasets/find", params=params
        ).json()
        return Dataset(self.connexion, r)

    @exception_handler
    @beartype
    def list_datasets(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
    ) -> List[Dataset]:
        """Retrieve all dataset of current organization

        Examples:
            ```python
            datasets = client.list_datasets()
            ```

        Returns:
            A list of (Dataset) object that belongs to your organization
        """
        params = {"limit": limit, "offset": offset, "order_by": order_by}
        params = filter_payload(params)
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/datasets", params=params
        ).json()
        return list(map(partial(Dataset, self.connexion), r["items"]))

    @exception_handler
    @beartype
    def get_dataset_version_by_id(self, id: Union[UUID, str]) -> DatasetVersion:
        """Get a dataset version by its id

        Examples:
            ```python
            dataset_version = client.get_dataset_version_by_id('918351d2-3e96-4970-bb3b-420f33ded895')
            ```

        Arguments:
            id (str or UUID): id of the dataset version to retrieve

        Returns:
            A (DatasetVersion)
        """
        if isinstance(id, str):
            id = UUID(id)
        params = {"id": id}
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/datasetversions/find", params=params
        ).json()
        return DatasetVersion(self.connexion, r)

    @exception_handler
    @beartype
    def create_model(
        self,
        name: str,
        type: Union[str, InferenceType] = None,
        framework: Union[str, Framework] = None,
        private: bool = True,
        description: str = "A brand new model!",
    ) -> Model:
        """Create a new model.

        Arguments:
            name (str): Model name to create.
            type (InferenceType): Model type can only be one of (classification, detection, segmentation).
            framework (Framework): Framework used by this model.
            private (bool): A public model can be seen by everyone. Defaults to true.
            description (str): Description of this model


        Returns:
            A (Model) object that you can manipulate
        """
        if type:
            logging.warning(
                "'type' parameter is deprecated and will be removed in future versions. "
                "If you want to give a type to your model version, call update() on ModelVersion."
            )

        if framework:
            logging.warning(
                "'framework' parameter is deprecated and will be removed in future versions. "
                "If you want to give a framework to your model version, call update() on your ModelVersion."
            )

        payload = {
            "name": name,
            "private": private,
            "description": description,
        }
        r = self.connexion.post(
            f"/sdk/organization/{self.id}/models",
            data=orjson.dumps(payload),
        ).json()
        created_model = Model(self.connexion, r)
        logger.info(
            f"📚 Model {created_model.name} created\n📊 🌐 Platform url: {created_model.get_resource_url_on_platform()}"
        )
        return created_model

    @exception_handler
    @beartype
    def get_model_by_id(self, id: Union[UUID, str]) -> Model:
        """Retrieve a model by its id

        Examples:
            ```python
            model = client.get_model_by_id(UUID("d8fae655-5c34-4a0a-a59a-e49c89f20998"))
            ```
        Arguments:
            id (str): id of the model that you are looking for

        Returns:
            A (Model) object that you can manipulate
        """
        if isinstance(id, str):
            id = UUID(id)
        params = {"id": id}
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/models/find", params=params
        ).json()
        return Model(self.connexion, r)

    def _do_get_model_by_name(self, url: str, name: str):
        params = {"name": name}
        r = self.connexion.get(url, params=params).json()
        return Model(self.connexion, r)

    @exception_handler
    @beartype
    def get_model(self, name: str) -> Model:
        """Retrieve a model by its name.

        Examples:
            ```python
            model = client.get_model("foo_model")
            ```
        Arguments:
            name (str): name of the model you are looking for

        Returns:
            A (Model) object that you can manipulate
        """
        return self._do_get_model_by_name(
            f"/sdk/organization/{self.id}/models/find", name
        )

    @exception_handler
    @beartype
    def get_public_model(self, name: str) -> Model:
        """Retrieve a public model by its name.
           It can only retrieve *public* model.

        Examples:
            ```python
            model = client.get_public_model("foo_public_model")
            ```
        Arguments:
            name (str): name of the public model you are looking for

        Returns:
            A (Model) object that you can manipulate
        """
        return self._do_get_model_by_name("/sdk/public/models/find", name)

    def _do_list_models(self, url: str, params: dict):
        params = filter_payload(params)
        r = self.connexion.get(url, params=params).json()
        return list(map(partial(Model, self.connexion), r["items"]))

    @exception_handler
    @beartype
    def list_models(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
    ) -> List[Model]:
        """List all models stored in this organization

        This will return all the models stored
        If no project is found, will throw a ResourceNotFoundError

        Examples:
            ```python
            models = client.list_models()
            ```

        Returns:
            A list of all (Model) that belong to this organization
        """
        params = {"limit": limit, "offset": offset, "order_by": order_by}
        return self._do_list_models(
            f"/sdk/organization/{self.id}/models", params=params
        )

    @exception_handler
    @beartype
    def list_public_models(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
        name: Optional[str] = None,
        type: Union[str, InferenceType, None] = None,
    ) -> List[Model]:
        """List all public models of Picsellia Hub
        This will return all public models of the hub

        Arguments:
            limit (int, optional): Limit number of public models to retrieve.
                Defaults to None, all public models will be retrieved.
            offset (int, optional): Offset to begin with when listing public models.
                Defaults to None, starting at 0.
            order_by (List[str], optional): Some fields to order models against.
                Defaults to None, models will not be sorted
            name (str, optional): A name to filter public models. It will return models with name *containing*
                this parameter. Defaults to None, models will not be filtered

        Examples:
            ```python
            public_detection_models = client.list_public_models(name="yolo")
            ```

        Returns:
            A list of all public (Model) objects
        """
        if type:
            logging.warning(
                "'type' parameter is deprecated and will be removed in future versions."
            )

        params = {
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "name": name,
        }
        return self._do_list_models("/sdk/public/models", params=params)

    @exception_handler
    @beartype
    def get_model_version_by_id(self, id: Union[UUID, str]) -> ModelVersion:
        """Get a model version by its id

        Examples:
            ```python
            model_version = client.get_model_version_by_id('918351d2-3e96-4970-bb3b-420f33ded895')
            ```

        Arguments:
            id (str or UUID): id of the model version to retrieve

        Returns:
            A (ModelVersion)
        """
        if isinstance(id, str):
            id = UUID(id)
        params = {"id": id}
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/modelversions/find", params=params
        ).json()
        return ModelVersion(self.connexion, r)

    @exception_handler
    @beartype
    def create_project(
        self, name: str, description: Optional[str] = None, private: bool = True
    ) -> Project:
        """Create a project with given name and parameters

        This project will be registered into used organization.

        Examples:
            ```python
            my_project = client.create_project("my_project", description="My first project!")
            ```
        Arguments:
            name (str): name of the project
            description (str): description of the project
            private (bool): shall be true if its only visible by the contributor of the project

        Returns:
            A (Project) that you can manipulate to run experiments, or attach dataset
        """
        payload = {"name": name, "private": private}
        if description is not None:
            payload["description"] = description

        r = self.connexion.post(
            f"/sdk/organization/{self.id}/projects",
            data=orjson.dumps(payload),
        ).json()
        created_project = Project(self.connexion, r)
        logger.info(
            f"📚 Project {name} created\n📊 Description: {description if description is not None else ''}\n🌐 Platform url: {created_project.get_resource_url_on_platform()}"
        )
        return created_project

    @exception_handler
    @beartype
    def get_project(self, project_name: str) -> Project:
        """Get a project from its name

        Retrieve a project from its name.
        Project must belong to used organization.

        Examples:
            ```python
            my_project = client.get_project("my_project")
            ```
        Arguments:
            project_name (str): name of the project to retrieve

        Returns:
            A (Project) of your organization, you can manipulate to run experiments, or attach dataset
        """
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/projects/find",
            params={"name": project_name},
        ).json()
        return Project(self.connexion, r)

    @exception_handler
    @beartype
    def get_project_by_id(self, id: Union[UUID, str]) -> Project:
        """Get a project from its id

        Retrieve a project from its id.
        Project must belong to used organization.
        If no project is found, will throw a ResourceNotFoundError

        Examples:
            ```python
            my_project = client.get_project("2214aacc-b884-41e1-b70f-420c0cd7eefb")
            ```
        Arguments:
            id (str): id of the project to retrieve

        Returns:
            A (Project) of your organization, you can manipulate to run experiments, or attach dataset
        """
        if isinstance(id, str):
            id = UUID(id)
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/projects/find?id={id}"
        ).json()
        return Project(self.connexion, r)

    @exception_handler
    @beartype
    def list_projects(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
    ) -> List[Project]:
        """List all projects of your organization.

        Retrieve all projects of your organization

        Examples:
            ```python
            projects = client.list_projects()
            ```

        Returns:
            A list of Project of your organization
        """
        params = {"limit": limit, "offset": offset, "order_by": order_by}
        params = filter_payload(params)
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/projects", params=params
        ).json()
        return list(map(partial(Project, self.connexion), r["items"]))

    @exception_handler
    @beartype
    def get_experiment_by_id(self, id: Union[UUID, str]) -> Experiment:
        """Get an experiment by its id

        Examples:
            ```python
            experiment = client.get_experiment_by_id('918351d2-3e96-4970-bb3b-420f33ded895')
            ```

        Arguments:
            id (str or UUID): id of the experiment to retrieve

        Returns:
            A (Experiment)
        """
        if isinstance(id, str):
            id = UUID(id)

        params = {"id": id}
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/experiments/find", params=params
        ).json()
        return Experiment(self.connexion, r)

    @exception_handler
    @beartype
    def get_deployment(self, name: str) -> Deployment:
        """Get a (Deployment) from its name.

        Examples:
            ```python
            deployment = client.get_deployment(
                name="awesome-deploy"
            )
            ```
        Arguments:
            name (str): auto-generated name of your deployment.

        Returns:
            A (Deployment) object connected and authenticated to all the services.
        """
        params = {"name": name}
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/deployments/find", params=params
        ).json()
        return Deployment(self.connexion, r)

    @exception_handler
    @beartype
    def get_deployment_by_id(self, id: Union[UUID, str]) -> Deployment:
        """Get a (Deployment) from its name.

        Examples:
            ```python
            deployment = client.get_deployment_id(
                id="YOUR DEPLOYMENT ID"
            )
            ```
        Arguments:
            id (str): deployment id displayed in your deployment settings.

        Returns:
            A (Deployment) object connected and authenticated to all the services.
        """
        if isinstance(id, str):
            id = UUID(id)
        params = {"id": id}
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/deployments/find", params=params
        ).json()
        return Deployment(self.connexion, r)

    @exception_handler
    @beartype
    def list_deployments(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
    ) -> List[Deployment]:
        """List all (Deployment) of your organization

        Examples:
            ```python
            our_deployments = client.list_deployments()
            ```
        Arguments:
            limit (int, optional): number max of results to return
            offset (int, optional): offset of page for pagination
            order_by (list[str], optional): keys on which deployments shall be sorted

        Returns:
            List of (Deployment): all deployments object connected and authenticated to all the services.
        """
        params = {"limit": limit, "offset": offset, "order_by": order_by}
        params = filter_payload(params)
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/deployments", params=params
        ).json()
        return list(map(partial(Deployment, self.connexion), r["items"]))

    @exception_handler
    @beartype
    def create_deployment(
        self,
        model_version: ModelVersion,
        shadow_model_version: Optional[ModelVersion] = None,
        name: Optional[str] = None,
        min_threshold: Optional[float] = None,
        target_datalake: Optional[Datalake] = None,
        disable_serving: Optional[bool] = False,
    ):
        """Create a (Deployment) from a model.

        This method allows you to create a (Deployment) on Picsellia. You will then have
        access to the monitoring dashboard and eventually a hosted endpoint.

        Examples:
            Create a serverless deployment
            ```python
            model = client.get_model(name="my-awesome-model")
            deployment = model.create_deployment()
            ```

        Arguments:
            model_version (ModelVersion): ModelVersion to deploy.
            shadow_model_version (ModelVersion, optional): ModelVersion to perform shadow predictions.
            name (str, optional): Name of your deployment. Defaults to a random name.
            min_threshold (float, optional): Threshold of detection scores used by models when predicting. Defaults to 0.
            target_datalake (Datalake, optional): Datalake to use when data are pushed into Picsellia.
                Defaults to organization default Datalake.
            disable_serving (bool, optional): Whether to not use Picsellia Serving. Defaults to False.


        Returns:
            A (Deployment)
        """
        from picsellia.sdk.deployment import Deployment

        payload = {
            "model_version_id": model_version.id,
            "name": name,
            "min_threshold": min_threshold,
        }
        if target_datalake is not None:
            payload["target_datalake_id"] = target_datalake.id
        if shadow_model_version:
            payload["shadow_model_version_id"] = shadow_model_version.id
        if disable_serving:
            payload["disable_serving"] = disable_serving

        filtered_payload = utils.filter_payload(payload)
        r = self.connexion.post(
            f"/sdk/organization/{self.id}/deployments",
            data=orjson.dumps(filtered_payload),
        ).json()
        deployment = Deployment(self.connexion, r)
        logger.info(f"{model_version} is deployed on {deployment}")
        return deployment

    @exception_handler
    @beartype
    def create_datasource(self, name: str) -> DataSource:
        """Create a data source into this organization

        Examples:
            ```python
            data_source = client.create_datasource()
            ```

        Returns:
            A  (DataSource) object that belongs to your organization
        """
        return DataSourceService.create_datasource(self.connexion, self._id, name)

    @exception_handler
    @beartype
    def get_datasource(self, name: str) -> DataSource:
        """Retrieve all data source of current organization

        Examples:
            ```python
            data_sources = client.list_datasources()
            ```

        Returns:
            A list of (DataSource) object that belongs to your organization
        """
        return DataSourceService.get_datasource(self.connexion, self._id, name)

    @exception_handler
    @beartype
    def get_or_create_datasource(self, name: str) -> DataSource:
        """Retrieve a datasource by its name.
        If tag datasource not exist, create it and return it.

        Examples:
            ```python
            tag = self.get_or_create_datasource("new_source")
            ```
        Arguments:
            name (str): Datasource name to retrieve or create

        Returns:
            A (Tag) object
        """
        return DataSourceService.get_or_create_datasource(
            self.connexion, self._id, name
        )

    @exception_handler
    @beartype
    def list_datasources(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
    ) -> List[DataSource]:
        """Retrieve all data source of current organization

        Examples:
            ```python
            data_sources = client.list_datasources()
            ```

        Returns:
            A list of (DataSource) object that belongs to your organization
        """
        return DataSourceService.list_datasources(
            self.connexion, self._id, limit, offset, order_by
        )

    @exception_handler
    @beartype
    def _create_tag_organization_scoped(self, name: str, target: TagTarget) -> Tag:
        payload = {"name": name, "target_type": target}
        r = self.connexion.post(
            f"/sdk/organization/{self.id}/tags",
            data=orjson.dumps(payload),
        ).json()
        return Tag(self.connexion, r)

    @exception_handler
    @beartype
    def create_dataset_tag(self, name: str) -> Tag:
        """Create a Dataset Tag, usable only on Dataset objects

        Examples:
            ```python
            tag = organization.create_dataset_tag("global")
            ```
        Arguments:
            name (str): Name of the tag

        Returns:
            A (Tag) object
        """
        return self._create_tag_organization_scoped(name, TagTarget.DATASET)

    @exception_handler
    @beartype
    def create_dataset_version_tag(self, name: str) -> Tag:
        """Create a Dataset Version Tag, usable only on Dataset Version objects

        Examples:
            ```python
            tag = organization.create_dataset_version_tag("train")
            ```
        Arguments:
            name (str): Name of the tag

        Returns:
            A (Tag) object
        """
        return self._create_tag_organization_scoped(name, TagTarget.DATASET_VERSION)

    @exception_handler
    @beartype
    def create_model_tag(self, name: str) -> Tag:
        """Create a Model Tag, usable only on Model objects

        Examples:
            ```python
            tag = organization.create_model_tag("model")
            ```
        Arguments:
            name (str): Name of the tag

        Returns:
            A (Tag) object
        """
        return self._create_tag_organization_scoped(name, TagTarget.MODEL)

    @exception_handler
    @beartype
    def create_model_version_tag(self, name: str) -> Tag:
        """Create a Model Version Tag, usable only on Model Version objects

        Examples:
            ```python
            tag = organization.create_model_version_tag("initial")
            ```
        Arguments:
            name (str): Name of the tag

        Returns:
            A (Tag) object
        """
        return self._create_tag_organization_scoped(name, TagTarget.MODEL_VERSION)

    @exception_handler
    @beartype
    def create_deployment_tag(self, name: str) -> Tag:
        """Create a Deployment Tag, usable only on Deployment objects

        Examples:
            ```python
            tag = organization.create_deployment_tag("operation")
            ```
        Arguments:
            name (str): Name of the tag

        Returns:
            A (Tag) object
        """
        return self._create_tag_organization_scoped(name, TagTarget.DEPLOYMENT)

    @exception_handler
    @beartype
    def _list_tags_organization_scoped(self, target: TagTarget) -> List[Tag]:
        params = {"target_type": target.value}
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/tags", params=params
        ).json()
        return list(map(partial(Tag, self.connexion), r["items"]))

    @exception_handler
    @beartype
    def list_dataset_tags(self) -> List[Tag]:
        """List all Dataset tags, usable only on Dataset objects

        Examples:
            ```python
            tags = organization.list_dataset_tags()
            ```

        Returns:
            A list of (Tag) objects
        """
        return self._list_tags_organization_scoped(TagTarget.DATASET)

    @exception_handler
    @beartype
    def list_dataset_version_tags(self) -> List[Tag]:
        """List all Dataset Version tags, usable only on Dataset Version objects

        Examples:
            ```python
            tags = organization.list_dataset_version_tags()
            ```

        Returns:
            A list of (Tag) objects
        """
        return self._list_tags_organization_scoped(TagTarget.DATASET_VERSION)

    @exception_handler
    @beartype
    def list_model_tags(self) -> List[Tag]:
        """List all Model tags, usable only on Model objects

        Examples:
            ```python
            tags = organization.list_model_tags()
            ```

        Returns:
            A list of (Tag) objects
        """
        return self._list_tags_organization_scoped(TagTarget.MODEL)

    @exception_handler
    @beartype
    def list_model_version_tags(self) -> List[Tag]:
        """List all Model Version tags, usable only on Model Version objects

        Examples:
            ```python
            tags = organization.list_model_version_tags()
            ```

        Returns:
            A list of (Tag) objects
        """
        return self._list_tags_organization_scoped(TagTarget.MODEL_VERSION)

    @exception_handler
    @beartype
    def list_deployment_tags(self) -> List[Tag]:
        """List all Deployment tags, usable only on Deployment Version objects

        Examples:
            ```python
            tags = organization.list_deployment_tags()
            ```

        Returns:
            A list of (Tag) objects
        """
        return self._list_tags_organization_scoped(TagTarget.DEPLOYMENT)

    @exception_handler
    @beartype
    def _find_tag_organization_scoped(self, target: TagTarget, name: str) -> Tag:
        params = {"name": name, "target_type": target.value}
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/tags/find",
            params=params,
        ).json()
        return Tag(self.connexion, r)

    @exception_handler
    @beartype
    def find_dataset_tag(self, name: str) -> Tag:
        """Find a Dataset tag, usable only on Dataset objects, from its name

        Examples:
            ```python
            tag = organization.find_dataset_tag("global")
            ```

        Returns:
            A (Tag) object
        """
        return self._find_tag_organization_scoped(TagTarget.DATASET, name)

    @exception_handler
    @beartype
    def find_dataset_version_tag(self, name: str) -> Tag:
        """Find a Dataset Version tag, usable only on Dataset Version objects, from its name

        Examples:
            ```python
            tag = organization.find_dataset_version_tag("train")
            ```

        Returns:
            A (Tag) object
        """
        return self._find_tag_organization_scoped(TagTarget.DATASET_VERSION, name)

    @exception_handler
    @beartype
    def find_model_tag(self, name: str) -> Tag:
        """Find a Model tag, usable only on Model objects, from its name

        Examples:
            ```python
            tag = organization.find_dataset_version_tag("model")
            ```

        Returns:
            A (Tag) object
        """
        return self._find_tag_organization_scoped(TagTarget.MODEL, name)

    @exception_handler
    @beartype
    def find_model_version_tag(self, name: str) -> Tag:
        """Find a Model Version tag, usable only on Model version objects, from its name

        Examples:
            ```python
            tag = organization.find_model_version_tag("initial")
            ```

        Returns:
            A (Tag) object
        """
        return self._find_tag_organization_scoped(TagTarget.MODEL_VERSION, name)

    @exception_handler
    @beartype
    def find_deployment_tag(self, name: str) -> Tag:
        """Find a Deployment tag, usable only on Deployment objects, from its name

        Examples:
            ```python
            tag = organization.find_deployment_tag("operation")
            ```

        Returns:
            A (Tag) object
        """
        return self._find_tag_organization_scoped(TagTarget.DEPLOYMENT, name)

    @exception_handler
    @beartype
    def get_job_by_id(self, id: Union[UUID, str]) -> Job:
        """Get a (Job) from its id.

        Examples:
            ```python
            deployment = client.get_job_by_id(
                id="YOUR JOB ID"
            )
            ```
        Arguments:
            id (str): deployment id displayed in your deployment settings.

        Returns:
            A (Job) object .
        """
        if isinstance(id, str):
            id = UUID(id)
        params = {"id": id}
        r = self.connexion.get(
            f"/sdk/organization/{self.id}/jobv2s/find", params=params
        ).json()
        return Job(self.connexion, r, version=2)
