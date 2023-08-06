import base64
import pickle
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

import numpy as np
import pandas as pd
from minio import Minio
from exodusutils import closest_string
from exodusutils.model_store import load_stuff_from_minio
from exodusutils.enums import TimeUnit

class TimeGroupInfo(BaseModel):
    """
    The ID for the model we trained for a time group value, along with the minimum target value in the time group value's dataframe, and the last date in the dataframe.

    Could contain an actual `LGBMRegressor` model.
    """

    model_id: str
    last_date: datetime
    min_target: Optional[float] = None
    model: Optional[Any] = None

    def load(self, prefix: str, minio: Minio):
        uri = f"{prefix}_{self.model_id}"
        self.model = pickle.loads(load_stuff_from_minio(uri, minio))
        return self

    def get_last_date_for_prediction(self, time_unit: TimeUnit) -> np.datetime64:
        return np.datetime64(time_unit.format_datetime(self.last_date))

    def to_downloadable(self, minio: Minio) -> Dict[str, Any]:
        stuff = self.load(minio).dict(exclude={"model_id"})

        # FIXME dumping with pickle and then encoding with base64 is too much work.
        #       Use a better mechanism when time permits.
        stuff["model"] = base64.b64encode(pickle.dumps(stuff["model"]))

        return stuff

    class Config:
        arbitrary_types_allowed = True

def load_time_group_models_from_minio(
    prefix: str,
    time_group_infos: List[TimeGroupInfo],
    minio: Minio
    ) -> Dict[str, TimeGroupInfo]:
    """
    Loads all the time group models and infos from minio.

    Parameters
    ----------
    minio : Minio
        minio

    Returns
    -------
    Dict[str, TimeGroupInfo]

    """
    return {k: v.load(prefix, minio) for k, v in time_group_infos.items()}


def extract_time_group_value_keys_from_df(time_group_infos: List[TimeGroupInfo], df: pd.DataFrame, TGVal_key: str) -> List[str]:
    """
    Extracts the valid time group value keys from the dataframe.

    If there is no time group column, there will only be one single item.

    Parameters
    ----------
    df : DataFrame
        The dataframe

    Returns
    -------
    List[str]
        The time group value keys found in the dataframe.
    """
    valid_time_group_values = list(time_group_infos.keys())
    if len(valid_time_group_values) != 1:
        # only had `no time group` this timegroup 
        time_group_values_in_df = list(df[TGVal_key].unique())
        return [
            closest_string(words=valid_time_group_values, ref=v)
            for v in time_group_values_in_df
        ]
    else:
        return valid_time_group_values
