from typing import Optional

from minio.api import Minio
from pandas.io import json
from pydantic import BaseModel
from pydantic.fields import Field

from exodusutils.schemas.input_file import InputFile
from exodusutils.schemas.requests import TrainIIDReqBody

description = """
The path to the local configuration file.

The JSON file should contain the following:
- **features**: A `dict` from `name` to `data_type` for all the column you wish to use.
- **target_column_name**: The `name` of the target column.
- **keep_cols**: The name of the columns you wish to keep.
- **folds**: The number of folds you want to train with.
"""


class Loaded:
    def __init__(
        self,
        training_file: InputFile,
        holdout_file: Optional[InputFile],
        validation_file: Optional[InputFile],
        req: TrainIIDReqBody,
        minio: Minio,
    ) -> None:
        self.training_file = training_file
        self.holdout_file = holdout_file
        self.validation_file = validation_file
        self.req = req
        self.minio = minio

    def __enter__(self) -> TrainIIDReqBody:
        return self.req

    def __exit__(self, *args):
        self.training_file.delete(self.minio)
        if self.holdout_file is not None:
            self.holdout_file.delete(self.minio)
        if self.validation_file is not None:
            self.validation_file.delete(self.minio)
        return self


class SimpleIIDTrainRequest(BaseModel):
    """
    Contains the following:
    - Absolute path to a local JSON file containing the configuration values
    - A `InputFile` object containing the absolute path to the local input training CSV file.
    - A optional `InputFile` object containing the absolute path to the local input holdout CSV file.
    - A optional `InputFile` object containing the absolute path to the local input validation CSV file.
    """

    config_path: str = Field(description=description)
    training_file: InputFile = Field(
        description="The absolute path to the local input training file."
    )
    holdout_file: Optional[InputFile] = Field(
        description="The absolute path to the local input holdout file. Optional",
        default=None,
    )
    validation_file: Optional[InputFile] = Field(
        description="The absolute path to the local input validation file. Optional",
        default=None,
    )

    def load(self, minio: Minio) -> Loaded:
        """
        Loads the JSON config into a `TrainIIDReqBody`.
        """
        with open(self.config_path) as f:
            meta_data = json.loads(f.read())
            features = meta_data["features"]
            feature_types = [{"name": k, "data_type": v} for k, v in features.items()]
            target = [
                f for f in feature_types if f["name"] == meta_data["target_column_name"]
            ][0]
        training_data = self.training_file.upload(minio)
        validation_data = (
            None if self.validation_file is None else self.validation_file.upload(minio)
        )
        holdout_data = (
            None if self.holdout_file is None else self.holdout_file.upload(minio)
        )
        req = TrainIIDReqBody(
            experiment_id="",
            training_data=training_data,
            target=target,
            feature_types=feature_types,
            folds=int(meta_data.get("folds", 5)),
            validation_data=validation_data,
            holdout_data=holdout_data,
            fold_assignment_column_name=meta_data.get(
                "fold_assignment_column_name", None
            ),
            random_seed=int(meta_data.get("random_seed", 9999)),
        )
        return Loaded(
            self.training_file, self.holdout_file, self.validation_file, req, minio
        )
