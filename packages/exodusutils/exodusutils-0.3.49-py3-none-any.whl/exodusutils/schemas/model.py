from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from pydantic.fields import Field

from exodusutils.schemas import Attribute

class ModelAttributeSummary(BaseModel):
    """
    This is `SupervisedModelAttributeSummary` in CoreX. A lot of fields are actually redundant,
    but removing them would make CoreX unable to recognize this class.
    """

    name: str
    """
    FIXME This should really just be a `Dict[str, float]`. Changing it could break GP though.
    """
    training_time: float
    cv_scores: Dict[str, List[float]]
    cv_deviations: Dict[str, float]
    cv_averages: Dict[str, float]
    validation_scores: Optional[Dict[str, float]] = None
    holdout_scores: Optional[Dict[str, float]] = None

    variable_importance: Optional[List[Attribute]] = []

    auc: Dict[str, Union[str, List, Dict]] = {"_typeHint": "core.bagelml.attribute.EmptyAUCMetric$"}
    """
    FIXME we don't need this, cv_scores already have it.
    """
    target_stats: Dict[str, float] = {}
    """
    FIXME having this here makes no sense
    """

    typeHint: str = Field(
        default="core.bagelml.attribute.SupervisedModelAttributeSummary",
        alias="_typeHint",
        exclude=False,
    )
    """
    FIXME hopefully get rid of this when we get rid of CoreX altogether.
    """

class SingleModel(BaseModel):
    key: str
    """
    The key for the model object stored in Minio. E.g. "lgbmaccuracy_1234"
    """
    name: str
    """
    Name of the model. This is the display name for the model. E.g. "LightGBM Accuracy - 1".
    """

    algorithm_name: str
    """
    Name of the algorithm. E.g. "LightGBM Accuracy".
    """

    algorithm_key: str
    """
    Key for the algorithm. E.g. "lgbmaccuracy".
    """

    experiment: str
    """
    Experiment's ID in MongoDB.
    """

    importances: List[Any]
    """
    The feature importances.
    """

    attributes: ModelAttributeSummary
    """
    The model's summary. Contains the scores, training time and variable importances.
    """
    hyperparameters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    completed_at: datetime

    options: Dict[str, str] = {}
    """
    Options for this model. Keys are defined in the enum `SingleModelOption`.
    """

    cross_validation_holdout_predictions_frame_id: Optional[str] = None

    # Since we are storing types that Pydantic cannot recognize, like `RandomForestClassifier` and so on, we need
    # to tell Pydantic to allow arbitrary types for our `ModelInfo`
    class Config:
        arbitrary_types_allowed = True
