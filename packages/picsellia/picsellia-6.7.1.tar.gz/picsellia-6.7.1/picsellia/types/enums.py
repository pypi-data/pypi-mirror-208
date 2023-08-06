from enum import Enum


class StrEnum(Enum):
    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)

    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def validate(cls, token):
        if isinstance(token, cls):
            return token
        elif isinstance(token, str):
            try:
                return cls[token.upper()]
            except KeyError:
                try:
                    return cls(token.upper())
                except ValueError:
                    raise TypeError(f"Given string should be one of {cls.values()}.")
        else:  # pragma: no cover
            # Should not happen if beartype is set
            raise TypeError(
                f"Given string should be a string one of {cls.values()} or a {cls}"
            )


class ExperimentStatus(StrEnum):
    RUNNING = "RUNNING"
    CANCELED = "CANCELED"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"
    WAITING = "WAITING"
    SUCCESS = "SUCCESS"


class LogType(StrEnum):
    VALUE = "VALUE"
    IMAGE = "IMAGE"
    LINE = "LINE"
    TABLE = "TABLE"
    BAR = "BAR"
    HEATMAP = "HEATMAP"
    LABELMAP = "LABELMAP"
    EVALUATION = "EVALUATION"


class RunStatus(StrEnum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    CANCELED = "CANCELED"
    SUCCESS = "SUCCESS"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"


class DataType(StrEnum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class ObjectDataType(StrEnum):
    ARTIFACT = "ARTIFACT"
    DATA = "DATA"
    LOGGING = "LOGGING"
    LOG_IMAGE = "LOG_IMAGE"
    MODEL_FILE = "MODEL_FILE"
    MODEL_THUMB = "MODEL_THUMB"
    SCAN_FILE = "SCAN_FILE"


class AnnotationStatus(StrEnum):
    PENDING = "PENDING"
    SKIPPED = "SKIPPED"
    ACCEPTED = "ACCEPTED"
    REFUSED = "REFUSED"


class AnnotationFileType(StrEnum):
    PASCAL_VOC = "PASCAL_VOC"
    COCO = "COCO"


class JobRunStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    KILLED = "KILLED"


class JobStatus(StrEnum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"


class Framework(StrEnum):
    TENSORFLOW = "TENSORFLOW"
    PYTORCH = "PYTORCH"
    ONNX = "ONNX"
    NOT_CONFIGURED = "NOT_CONFIGURED"


class InferenceType(StrEnum):
    NOT_CONFIGURED = "NOT_CONFIGURED"
    CLASSIFICATION = "CLASSIFICATION"
    OBJECT_DETECTION = "OBJECT_DETECTION"
    SEGMENTATION = "SEGMENTATION"
    POINT = "POINT"
    LINE = "LINE"
    MULTI = "MULTI"


class TagTarget(StrEnum):
    DATA = "DATA"
    ASSET = "ASSET"
    MODEL_VERSION = "MODEL_VERSION"
    MODEL = "MODEL"
    DATASET_VERSION = "DATASET_VERSION"
    DATASET = "DATASET"
    DEPLOYMENT = "DEPLOYMENT"
    PREDICTED_ASSET = "PREDICTED_ASSET"


class ImportAnnotationMode(StrEnum):
    REPLACE = "REPLACE"
    KEEP = "KEEP"
    CONCATENATE = "CONCATENATE"


class AddEvaluationType(StrEnum):
    KEEP = "KEEP"
    REPLACE = "REPLACE"


class ContinuousTrainingType(StrEnum):
    SCAN = "SCAN"
    EXPERIMENT = "EXPERIMENT"


class ContinuousTrainingTrigger(StrEnum):
    FEEDBACK_LOOP = "FEEDBACK_LOOP"
    NONE = "NONE"


class ContinuousDeploymentPolicy(StrEnum):
    DEPLOY_CHAMPION = "DEPLOY_CHAMPION"
    DEPLOY_SHADOW = "DEPLOY_SHADOW"
    DEPLOY_MANUAL = "DEPLOY_MANUAL"


class ServiceMetrics(str, Enum):
    def __new__(cls, *args, **kwargs):
        value = len(cls.__members__) + 1
        obj = str.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, service, is_aggregation):
        self.service = service
        self.is_aggregation = is_aggregation
        return

    PREDICTIONS_OUTLYING_SCORE = "ae_outlier", False
    PREDICTIONS_DATA = "metrics", False
    REVIEWS_OBJECT_DETECTION_STATS = "object_detection", False
    REVIEWS_CLASSIFICATION_STATS = "classification", False
    REVIEWS_LABEL_DISTRIBUTION_STATS = "label_distribution", False

    AGGREGATED_LABEL_DISTRIBUTION = "label_distribution", True
    AGGREGATED_OBJECT_DETECTION_STATS = "object_detection", True
    AGGREGATED_PREDICTIONS_DATA = "metrics", True
    AGGREGATED_DRIFTING_PREDICTIONS = "ks_drift", True


class ProcessingType(StrEnum):
    PRE_ANNOTATION = "PRE_ANNOTATION"
    DATA_AUGMENTATION = "DATA_AUGMENTATION"
    DATASET_VERSION_CREATION = "DATASET_VERSION_CREATION"
    AUTO_TAGGING = "AUTO_TAGGING"
    AUTO_ANNOTATION = "AUTO_ANNOTATION"


class SupportedContentType(StrEnum):
    PNG = "IMAGE/PNG"
    JPEG = "IMAGE/JPEG"
