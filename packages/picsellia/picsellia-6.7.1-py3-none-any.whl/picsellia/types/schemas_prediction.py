from typing import List

from pydantic import BaseModel, root_validator, validator

from picsellia.types.enums import InferenceType


def labels_validator(v: List[int]) -> List[int]:
    if not isinstance(v, List):
        raise TypeError(v)

    if len(v) < 1:
        raise ValueError("There must be at least one id")

    return v


def boxes_validator(v: List[List[int]]) -> List[List[int]]:
    if not isinstance(v, List):
        raise TypeError(v)

    if len(v) < 1:
        raise ValueError("There must be at least one id")

    return v


def scores_validator(v: List[float]) -> List[float]:
    if not isinstance(v, List):
        raise TypeError(v)

    if len(v) < 1:
        raise ValueError("There must be at least one score")

    return v


def masks_validator(v: List[List[List[int]]]) -> List[List[List[int]]]:
    if not isinstance(v, List):
        raise TypeError(v)

    if len(v) < 1:
        raise ValueError("There must be at least one mask")

    return v


class PredictionFormat(BaseModel):
    @property
    def model_type(cls) -> InferenceType:
        raise Exception()


class ClassificationPredictionFormat(PredictionFormat):
    detection_classes: List[int]
    detection_scores: List[float]

    @property
    def model_type(cls) -> InferenceType:
        return InferenceType.CLASSIFICATION


class DetectionPredictionFormat(PredictionFormat):
    detection_classes: List[int]
    detection_boxes: List[List[int]]
    detection_scores: List[float]

    _validate_labels = validator("detection_classes", allow_reuse=True)(
        labels_validator
    )
    _validate_scores = validator("detection_scores", allow_reuse=True)(scores_validator)
    _validate_boxes = validator("detection_boxes", allow_reuse=True)(boxes_validator)

    @property
    def model_type(cls) -> InferenceType:
        return InferenceType.OBJECT_DETECTION

    @root_validator
    def check_sizes(cls, values):
        labels, scores, boxes = (
            values.get("detection_classes"),
            values.get("detection_scores"),
            values.get("detection_boxes"),
        )

        if (
            labels is None
            or scores is None
            or boxes is None is None
            or len(labels) != len(scores)
            or len(boxes) != len(labels)
        ):
            raise ValueError("incoherent lists")

        return values


class SegmentationPredictionFormat(PredictionFormat):
    detection_classes: List[int]
    detection_boxes: List[List[int]]
    detection_scores: List[float]
    detection_masks: List[List[List[int]]]

    _validate_labels = validator("detection_classes", allow_reuse=True)(
        labels_validator
    )
    _validate_boxes = validator("detection_boxes", allow_reuse=True)(boxes_validator)
    _validate_scores = validator("detection_scores", allow_reuse=True)(scores_validator)
    _validate_masks = validator("detection_masks", allow_reuse=True)(masks_validator)

    @property
    def model_type(cls) -> InferenceType:
        return InferenceType.SEGMENTATION

    @root_validator
    def check_sizes(cls, values):
        labels, boxes, scores, masks = (
            values.get("detection_classes"),
            values.get("detection_boxes"),
            values.get("detection_scores"),
            values.get("detection_masks"),
        )

        if (
            labels is None
            or scores is None
            or boxes is None
            or masks is None
            or len(labels) != len(scores)
            or len(boxes) != len(labels)
            or len(masks) != len(labels)
        ):
            raise ValueError("incoherent lists")

        return values
