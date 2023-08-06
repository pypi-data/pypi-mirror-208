from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from picsellia.types.enums import (
    AnnotationStatus,
    DataType,
    ExperimentStatus,
    Framework,
    InferenceType,
    JobRunStatus,
    JobStatus,
    LogType,
    RunStatus,
    TagTarget,
)


class DaoSchema(BaseModel):
    # Might not be defined if refresh is done manually
    id: Optional[UUID]


class DatalakeSchema(DaoSchema):
    name: str
    connector_id: Optional[UUID]


class OrganizationSchema(DaoSchema):
    name: str
    default_connector_id: Optional[UUID]


class DatasetSchema(DaoSchema):
    name: str


class DatasetVersionSchema(DaoSchema):
    name: str = Field(alias="origin_name")
    origin_id: UUID = Field(alias="origin_id")
    version: str
    type: InferenceType


class DatasetVersionStats(BaseModel):
    label_repartition: Dict[str, int]
    nb_objects: int
    nb_annotations: int


class ModelSchema(DaoSchema):
    name: str
    type: InferenceType
    framework: Framework
    private: bool


class ModelVersionSchema(DaoSchema):
    origin: ModelSchema
    name: str
    version: int
    labels: Optional[dict]
    type: InferenceType
    framework: Framework


class ModelDataSchema(DaoSchema):
    name: str
    version_id: UUID
    repartition: dict


class ModelContextSchema(DaoSchema):
    experiment_id: Optional[UUID]
    datas: Optional[List[ModelDataSchema]]
    parameters: dict


class ModelFileSchema(DaoSchema):
    name: str
    object_name: str
    filename: str
    large: bool
    url: Optional[str] = Field(alias="presigned_url")


class ProjectSchema(DaoSchema):
    name: str


class DeploymentSchema(DaoSchema):
    name: str
    type: InferenceType
    oracle_host: Optional[str]
    serving_host: Optional[str]


class ImageMetaSchema(BaseModel):
    width: int
    height: int


class VideoMetaSchema(BaseModel):
    duration: int


class DataSchema(DaoSchema):
    object_name: str
    filename: str
    type: DataType
    url: Optional[str] = Field(alias="presigned_url")


class ImageSchema(DataSchema):
    meta: ImageMetaSchema


class VideoSchema(DataSchema):
    meta: VideoMetaSchema


class DataSourceSchema(DaoSchema):
    name: str


class AssetSchema(DaoSchema):
    data: Union[ImageSchema, VideoSchema]


class ExperimentSchema(DaoSchema):
    name: str
    status: ExperimentStatus


class EvaluationSchema(DaoSchema):
    asset_id: UUID


class UserSchema(DaoSchema):
    username: str


class CollaboratorSchema(DaoSchema):
    user: UserSchema
    organization_id: UUID


class UsernameCollaboratorSchema(DaoSchema):
    username: str


class WorkerSchema(DaoSchema):
    collaborator: UsernameCollaboratorSchema


class ScanSchema(DaoSchema):
    name: str


class RunSchema(DaoSchema):
    order: int
    status: RunStatus
    parameters: dict
    scan_id: UUID
    experiment_id: UUID


class ScanFileSchema(DaoSchema):
    name: str
    object_name: str
    large: bool
    url: Optional[str] = Field(alias="presigned_url")


class ArtifactSchema(DaoSchema):
    name: str
    object_name: str
    filename: str
    large: bool
    url: Optional[str] = Field(alias="presigned_url")


class LoggingFileSchema(DaoSchema):
    object_name: str
    url: Optional[str] = Field(alias="presigned_url")


LogDataType = Union[list, dict, float, int, str]


class LogSchema(DaoSchema):
    name: str
    type: LogType
    data: LogDataType


class TagSchema(DaoSchema):
    name: str
    target_type: TagTarget


class LabelSchema(DaoSchema):
    name: str


class AnnotationSchema(DaoSchema):
    worker_id: UUID
    duration: float
    status: AnnotationStatus


class ShapeSchema(DaoSchema):
    label: LabelSchema


class RectangleSchema(ShapeSchema):
    x: int
    y: int
    w: int
    h: int


class PolygonSchema(ShapeSchema):
    coords: List = Field(alias="polygon")


class LineSchema(ShapeSchema):
    coords: List = Field(alias="line")


class PointSchema(ShapeSchema):
    coords: List = Field(alias="point")
    order: int


class ClassificationSchema(ShapeSchema):
    pass


class ConfigRequirementScan(BaseModel):
    package: str
    version: str


class ExecutionConfigScan(BaseModel):
    type: str


class ConfigScan(BaseModel):
    execution: str
    script: Optional[str]
    requirements: Union[str, List[ConfigRequirementScan], None]
    data: Optional[List[str]]


class ConnectorSchema(DaoSchema):
    bucket_name: str


class JobSchema(DaoSchema):
    status: JobStatus


class JobRunSchema(DaoSchema):
    status: JobRunStatus
