from __future__ import annotations

import json
import traceback
from enum import Enum
from logging import Logger
from typing import Awaitable, Callable, Dict, List, Optional

import pandas as pd
import requests
from minio import Minio
from pydantic import BaseModel
from pydantic.class_validators import validator
from pydantic.fields import Field

from exodusutils import internal
from exodusutils.enums import DataType
from exodusutils.exceptions.exceptions import ExodusBadRequest
from exodusutils.schemas import Column
from exodusutils.schemas.responses import FailedResp, ModelRespBase
from exodusutils.schemas.uri import MinioURI


class AwaitableReq(BaseModel):
    url: Optional[str] = Field(
        description="The url for the Exodus pod to report to. Default is None",
        default=None,
    )

    def callback(self, stuff: Dict) -> None:
        if self.url is not None:
            requests.post(self.url, data=json.dumps(stuff, allow_nan=True))

    async def run(
        self, func: Callable[[AwaitableReq], Awaitable[ModelRespBase]], logger: Logger
    ) -> None:
        try:
            resp = await func(self)
            logger.info(
                f"Response = {json.dumps(resp.dict(), indent=4, allow_nan=True)}"
            )
            self.callback(resp.dict())
        except Exception:
            reason = traceback.format_exc()
            logger.warn(f"Failed to finish request, reason = {reason}")
            self.callback(FailedResp(reason=reason).dict())


class TrainReqBodyBase(AwaitableReq):
    """
    The base schema for training requests.

    Attributes
    ----------
    training_data : str
        The URI for the training data.
    feature_types : List[Column]
        The features present in training data.
    target : Column
        The target column. Must be present in `feature_types`.
    folds : int
        Number of folds for this experiment.
    """

    training_data: str = Field(description="The training data uri")
    feature_types: List[Column] = Field(
        default=[Column(name="foo", data_type="double")],
        description="The features present in training data",
    )
    target: Column = Field(
        default=Column(name="foo", data_type="double"),
        description="The target column. Must be present in feature_types",
    )
    folds: int = Field(
        default=5, ge=1, le=10, description="Number of folds for this experiment"
    )

    @validator("target")
    def check_column(cls, v, values):
        if v not in values.get("feature_types", []):
            raise ExodusBadRequest(
                f"target {v} not found in feature_types {values.get('feature_types', [])}"
            )
        return v

    def get_feature_names(self) -> List[str]:
        """
        Returns the names of the features.
        """
        return [f.name for f in self.feature_types]

    def get_training_df(self, client: Minio) -> pd.DataFrame:
        """
        Returns the Pandas DataFrame from the bytes in training_data field.
        """
        return internal.get_df(
            MinioURI.parse(self.training_data), client, self.feature_types
        )

    def get_features(self, data_type: DataType) -> List[Column]:
        """
        Returns the features with the specified data type.

        Parameters
        ----------
        data_type : DataType
            The specified data type.

        Returns
        -------
        List[Column]
            The features.

        """
        return [f for f in self.feature_types if f.data_type == data_type]

    def get_feature_names_by_data_type(self, data_type: DataType) -> List[str]:
        """
        Helper function for extracting names for features with a specified type.

        Parameters
        ----------
        data_type : DataType
            The specified data type.

        Returns
        -------
        List[str]
            Names of the features.
        """
        return [f.name for f in self.get_features(data_type)]


class TrainIIDReqBody(TrainReqBodyBase):
    """
    The schema for IID training request body.

    Has the following fields:
    - `feature_types`: a list of `Column`s, which is the name of a feature and the feature's data type. Contains the target.
    - `target`: the target `Column`.
    - `folds`: number of cross validation folds we want to train.
    - `random_seed`: random seed. Optional.

    Get dataframes by calling the following methods:
    - `get_training_df`: returns the training data as a Pandas dataframe.
    - `get_holdout_df`: returns the holdout data as a Pandas dataframe if the field is not a `None`. Otherwise returns a `None`.
    - `get_validation_df`: returns the validation data as a Pandas dataframe if the field is not a `None`. Otherwise returns a `None`.
    """

    experiment_id: str = Field(
        description="Experiment id when train callback need it."
    )

    random_seed: Optional[int] = Field(
        default=None, description="The random seed for this experiment. Optional."
    )
    validation_data: Optional[str] = Field(
        default=None, description="The validation data uri. Optional"
    )
    holdout_data: Optional[str] = Field(
        default=None, description="The holdout data uri. Optional"
    )
    fold_assignment_column_name: Optional[str] = Field(
        default=None,
        description="The name of the fold assignment column. If not provided, Exodus will cut cross validation folds in a modulo fashion. If this field is defined, it is required to be a valid column in the input dataframe. This column is not included in `feature_types`, and will be discarded during training.",
    )

    class Config:
        schema_extra = {
            "examples": [
                {
                    "req": {
                        "experiment_id": "id",
                        "training_data": "s3a://some-bucket/foo/bar/train.csv",
                        "feature_types": [
                            {"name": "foo", "data_type": "double"},
                            {"name": "bar", "data_type": "string"},
                        ],
                        "target": [{"name": "foo", "data_type": "double"}],
                        "folds": 3,
                        "holdout_data": "s3a://some-bucket/foo/bar/holdout.csv",
                    }
                },
                {
                    "req": {
                        "experiment_id": "id",
                        "training_data": "don't care",
                        "feature_types": [
                            {"name": "don't care", "data_type": "double"},
                        ],
                        "target": [{"name": "don't care", "data_type": "double"}],
                        "folds": 5,
                        "holdout_data": "s3a://some-bucket/foo/bar/holdout.csv",
                    },
                    "simple_request": {
                        "experiment_id": "id",
                        "config_path": "/home/foo/bar/config.json",
                        "training_file": {
                            "path": "/home/foo/bar/train.csv",
                        },
                        "holdout_file": {
                            "path": "/home/foo/bar/holdout.csv",
                        },
                        "validation_file": {
                            "path": "/home/foo/bar/validation.csv",
                        },
                    },
                },
            ]
        }

    def get_holdout_df(self, client: Minio) -> Optional[pd.DataFrame]:
        """
        Returns the Pandas DataFrame from the bytes in holdout_data field, or `None` if none specified.
        """
        if not self.holdout_data:
            return None
        else:
            return internal.get_df(
                MinioURI.parse(self.holdout_data), client, self.feature_types
            )

    def get_validation_df(self, client: Minio) -> Optional[pd.DataFrame]:
        """
        Returns the Pandas DataFrame from the bytes in holdout_data field, or `None` if none specified.
        """
        if not self.validation_data:
            return None
        else:
            return internal.get_df(
                MinioURI.parse(self.validation_data), client, self.feature_types
            )


class PredictReqBody(AwaitableReq):
    """
    The schema for prediction request body.
    """
    prediction_id: str = Field(description="Prediction id when predicted callback need it.")
    model_id: str = Field(description="The specified model id")
    target: Column = Field(description='Target')
    feature_types: List[Column] = Field(description='Feature types (include target)')
    data: str = Field(description="The prediction data as JSON")
    threshold: Optional[float] = Field(
        default=None, description="The threshold for classification predictions"
    )
    keep_columns: List[str] = Field(
        default=[], description="The columns to keep in the prediction response"
    )

    def get_keep_columns_df(self) -> pd.DataFrame:
        """
        Returns a Pandas DataFrame with only the columns specified in the `keep_columns` parameter
        """
        df = pd.DataFrame(pd.read_json(self.data, orient="records"))
        return df.drop(
            [c for c in df.columns.tolist() if c not in self.keep_columns], axis=1
        )

    def get_prediction_df(self, feature_types: List[Column]) -> pd.DataFrame:
        """
        Returns the Pandas DataFrame from the bytes in data field.

        If the input data contains any column that is not in `feature_types`, that column will be \
dropped from the resulting dataframe.
        """
        valid_columns = [f.name for f in feature_types]
        df = pd.DataFrame(json.loads(self.data))
        valid_features = [f for f in feature_types if f.name in df.columns.tolist()]

        # We only want to keep the columns that are specified in `feature_types`
        return df.drop(
            [c for c in df.columns.tolist() if c not in valid_columns], axis=1
        ).pipe(internal.cast_df_types, valid_features)


class MigrateAction(str, Enum):
    """
    Defines the migration action. Could only be either one of `up` and `down`.
    """

    up = "up"
    down = "down"


class MigrateReqBody(BaseModel):
    """
    The schema for migrate request body.
    """

    action: MigrateAction = Field(description="The migration action")

    class Config:
        use_enum_values = True
