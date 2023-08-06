import math
from abc import ABC
from typing import List, Union, Dict
import pandas as pd
from pydantic import BaseModel, Field


class AUCMetric(ABC, BaseModel):
    pass


class EmptyAUCMetric(AUCMetric):
    typeHint: str = Field(
        default="core.bagelml.attribute.EmptyAUCMetric$",
        alias="_typeHint",
        exclude=False,
    )

class EmptyAUCObjReport(BaseModel):
    typeHint: str = Field(
        default="core.bagelml.attribute.EmptyAUCObjReport$",
        alias="_typeHint",
        exclude=False,
    )


class FullAUCObjReport(BaseModel):
    """
    Represents a binary model's AUC related metrics. Will be used by GP-FE to
    plot confusion matrix and ROC curve.
    """

    auc: float
    """
    The AUC score.
    """
    ths: List[float]
    """
    The thresholds.
    """
    nonparametric_ths: List[float]
    """
    TODO can't find anything describing what this is... perhaps just read the code and figure
    out what it is?
    """
    fps: List[float]
    """
    False positives.
    """
    tps: List[float]
    """
    True positives.
    """
    fns: List[float]
    """
    False negatives.
    """
    tns: List[float]
    """
    True negatives.
    """
    th_max_by: Dict
    """
    Max thresholds based on different metrics.
    """
    positive_label: str
    """
    The positive label.
    """
    negative_label: str
    """
    The negative label.
    """

    typeHint: str = Field(
        default="core.bagelml.attribute.FullAUCObjReport",
        alias="_typeHint",
        exclude=False,
    )


AUCReport = Union[
    FullAUCObjReport, EmptyAUCObjReport
]  # Don't change the order of these two classes!


class FullAUCMetric(AUCMetric):
    cv_average: AUCReport
    valid: AUCReport
    test: AUCReport
    cv_full: List[AUCReport] = []
    """
    FIXME in gp-fe this is explicitly removed from the API response body.
    I keep this here so that CoreX can still parse it, but in the future
    this field ought to be removed.
    """

    typeHint: str = Field(
        default="core.bagelml.attribute.FullAUCMetric",
        alias="_typeHint",
        exclude=False,
    )
