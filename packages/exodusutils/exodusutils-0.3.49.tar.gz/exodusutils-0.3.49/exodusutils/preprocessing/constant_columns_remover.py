from typing import List, Optional

import numpy as np
import pandas as pd

from exodusutils.exceptions.exceptions import ExodusMethodNotAllowed
from exodusutils.internal.process_unit import ProcessUnit
from exodusutils.schemas import Column


class ConstantColumnsRemover(ProcessUnit):
    """
    Locates all constant columns in the dataframe during `fit`, then during `transform` remove the constant \
columns found in `fit` from the given dataframe. Will not remove the target column.
    """

    def __init__(self, feature_types: List[Column], target_column_name: str) -> None:
        self.feature_types = feature_types
        self.target_column_name = target_column_name
        self.constant_columns: Optional[List[str]] = None

    def fitted(self) -> bool:
        return self.constant_columns is not None

    def fit(self, df: pd.DataFrame) -> None:
        self.constant_columns = [
            column.name
            for column in self.feature_types
            if column.name != self.target_column_name
            and (
                (df[column.name].isnull().all())  # All NaNs
                or (
                    df[column.name].notnull().all() and df[column.name].nunique() == 1
                )  # Only one kind of value without any NaN
            )
        ]

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.fitted():
            raise ExodusMethodNotAllowed("Has to fit before transform")
        return pd.DataFrame(df.drop(columns=self.constant_columns))
