from typing import List

import numpy as np
import pandas as pd

from exodusutils import internal
from exodusutils.enums import TimeUnit
from exodusutils.internal.process_unit import ProcessUnit


class TimeComponentEncoding(ProcessUnit):
    """
    Does time component encoding. The `fit` method does nothing. For `transform`, the encoding extract the \
following:
    - year, to a column named `\"{COL_NAME}_y\"`
    - quarter, to a column named `\"{COL_NAME}_q\"`
    - month, to a column named `\"{COL_NAME}_m\"`
    - week, to a column named `\"{COL_NAME}_w\"`
    - weekday, to a column named `\"{COL_NAME}_d\"`
    - hour, to a column named `\"{COL_NAME}_h\"`
    - minute, to a column named `\"{COL_NAME}_m\"`
    - second, to a column named `\"{COL_NAME}_s\"`
    And then it would calculate the difference in seconds from the values in the column to the Unix Epoch (1970-01-01), \
and substitute the column with the difference.

    """

    def __init__(self, time_unit: TimeUnit = TimeUnit.hour) -> None:
        self.time_unit = TimeUnit(time_unit)
        self.components: List[str] = []

    def fit(self, df: pd.DataFrame) -> None:
        pass

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.components = []
        for column in internal.get_columns(df, np.datetime64):
            for prefixed_column_name, component in zip(
                internal.postfix_datetime_cols_with_time_components(column),
                internal.get_time_components(df, self.time_unit, column),
            ):
                if component is not None:
                    df[prefixed_column_name] = component
                    self.components.append(prefixed_column_name)
            df[column] = (df[column] - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")
        return df
