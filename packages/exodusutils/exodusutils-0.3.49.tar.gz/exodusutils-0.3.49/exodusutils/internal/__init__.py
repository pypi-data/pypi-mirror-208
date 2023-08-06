import math
from typing import List, Optional, Tuple, DefaultDict, Dict

import numpy as np
import pandas as pd
from minio import Minio
from pandas.api.types import is_datetime64tz_dtype, is_object_dtype
from sklearn.metrics import accuracy_score, auc, confusion_matrix, f1_score, roc_curve
from exodusutils.constants import DATETIME_COMPONENTS_PREFIX
from exodusutils.enums import DataType, TimeUnit
from exodusutils.exceptions import ExodusBadRequest
from exodusutils.exceptions.exceptions import ExodusError
from exodusutils.schemas import Column
from exodusutils.schemas.uri import MinioURI
from exodusutils.schemas.auc_metric import FullAUCObjReport

def cast_columns(
    df: pd.DataFrame, columns: List[str], target_type: DataType
) -> pd.DataFrame:
    """
    Casts the specified columns to the target `DataType`.
    """
    for col in columns:
        if target_type == DataType.double:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        elif target_type == DataType.timestamp:
            df[col] = pd.to_datetime(pd.Series(df[col]), errors="coerce")
            # If the Timestamp has been cast successfully but the column contains timezone info,
            # Remove the timezone info from the timestamp column to make it ordinary timestamp type
            if is_datetime64tz_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)
            # If the Timestamp column hasn't been cast successfully,
            # The main resaon is there are two kinds of Timestamp formats in the column, the one with timezone info and the one without it
            # Transform it again with timezone parsing
            if is_object_dtype(df[col]):
                df[col] = pd.to_datetime(
                    pd.Series(df[col]), errors="coerce", utc=True
                ).dt.tz_localize(None)
        else:
            df[col] = df[col].fillna("").astype(str).replace("", np.nan)
    return df


def cast_df_types(df: pd.DataFrame, feature_types: List[Column]) -> pd.DataFrame:
    feature_types = [f for f in feature_types if f.name in df.columns]
    numeric_columns = [f.name for f in feature_types if f.data_type == DataType.double]
    datetime_columns = [
        f.name for f in feature_types if f.data_type == DataType.timestamp
    ]
    categorical_columns = [
        f.name
        for f in feature_types
        if f.name not in numeric_columns + datetime_columns
    ]
    return (
        df.pipe(cast_columns, numeric_columns, DataType.double)
        .pipe(cast_columns, datetime_columns, DataType.timestamp)
        .pipe(cast_columns, categorical_columns, DataType.string)
    )


def get_df(uri: MinioURI, client: Minio, feature_types: List[Column]) -> pd.DataFrame:
    df = uri.get_df(client, header=[f.name for f in feature_types])
    if df is None:
        raise ExodusError(f"Failed to get data, uri = {uri.url}")
    validate_columns(df.columns.to_list(), feature_types)
    return df.pipe(cast_df_types, feature_types)


def postfix_datetime_cols_with_time_components(col: str) -> List[str]:
    """
    Returns a list of str, representing the new time component names

    Parameters
    ----------
    col : str
        a datetime column

    Returns
    -------
    List[str]
        A list of new column names
    """
    return [f"{col}_{t}" for t in DATETIME_COMPONENTS_PREFIX]


def get_time_components(
    df: pd.DataFrame, time_unit: TimeUnit, col: str
) -> List[Optional[pd.Series]]:
    """
    Returns a list of `pd.Series`s, representing the time components for the given column name. \
A time component is a series of `np.int64`.

    Parameters
    ----------
    df : pd.DataFrame
        Original dataframe that features are to be derived from
    time_unit : TimeUnit
        The `smallest` time unit that the new features should include
    col : str
        One of the datetime columns of df

    Returns
    -------
    List of time components.
    """
    # Time components
    dt = df[col].dt
    components = [dt.year]

    # quarter, month and week component
    if time_unit not in {TimeUnit.year}:
        components += [dt.quarter, dt.month, dt.week]
    else:
        components += [None, None, None]

    # weekday and date component
    if time_unit not in {TimeUnit.year, TimeUnit.month}:
        components += [dt.weekday]
    else:
        components += [None]

    # hour component
    if time_unit not in {TimeUnit.year, TimeUnit.month, TimeUnit.day}:
        components += [dt.hour.replace(0, 24), dt.minute, dt.second]
    else:
        components += [None, None, None]

    return components


def get_columns(df: pd.DataFrame, dtype) -> List[str]:
    return df.select_dtypes(dtype).columns.tolist()


def merge_training_holdout(
    training: pd.DataFrame, holdout: pd.DataFrame
) -> pd.DataFrame:
    holdout["holdout"] = 1
    training["holdout"] = 0
    return pd.concat([training, holdout])


def split_to_training_and_holdout(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    if "holdout" not in df.columns:
        return df, None
    else:

        def drop_holdout(df: pd.DataFrame, val: int) -> pd.DataFrame:
            return df.loc[df["holdout"] == val, :].drop(columns="holdout")

        return drop_holdout(df, 0), drop_holdout(df, 1)


def get_numeric_features(df: pd.DataFrame, target: str) -> List[str]:
    return [
        f
        for f in get_columns(df, np.float64) + get_columns(df, np.int64)
        if f != target
    ]


def train_validation_split(
    df: pd.DataFrame, validation_percentage: float
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    if validation_percentage == 0.0:
        return df, None
    else:
        indexed_validation = df.sample(frac=validation_percentage)
        return df.loc[
            ~df.index.isin(indexed_validation.index)
        ], indexed_validation.reset_index(drop=True)


def sanitize_pred_and_actual(
    pred: np.ndarray, actual: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    if pred.size != actual.size:
        raise ValueError(f"pred.size = {pred.size} != actual.size = {actual.size}")

    if np.issubdtype(actual.dtype, np.number):
        if not np.issubdtype(pred.dtype, np.number):
            raise ValueError(f"actual is number while pred is not")
        pred, actual = [
            np.array(t)
            for t in zip(*[(p, a) for p, a in zip(pred, actual) if not np.isnan(a)])
        ]

    if pred.size == 0:
        raise ValueError("empty fold score")

    return pred, actual


def validate_columns(header: List[str], features: List[Column]) -> None:
    """
    Check if there are any required features in `features` that are missing from the dataframe

    Parameters
    ----------
        header : List[str]
            columns that are present in a dataframe
        features : List[Column]
            `features` is a list of `Column`s that is/was required for training

    Returns
    -------
        None

    Raises
    ------
        HTTPException
            the client is notified that the information supplied is invalid
    """
    for f in features:
        if (
            f.name not in header
        ):  # This means that a required field is missing from the dataframe
            raise ExodusBadRequest(f"column {f.name} is missing from the data")


def get_column_mode(col) -> float:
    """
    Returns the most frequent value of a numeric column, or `0.0` if it is impossible to calculate.

    This is used to create labels for the previously unseen values in a label encoded categorical column.
    """
    mode = col.mode().values
    if len(mode) > 0:
        return (
            0.0 if math.isnan(mode[0]) else mode[0]
        )  # Just take the first one if there are ties
    else:
        return 0.0


def append_fold_column(df: pd.DataFrame, name: str, folds: int) -> pd.DataFrame:
    """Appends the fold column to the incoming dataframe. Will return a new dataframe, and leave the old one unchanged.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe.
    name : str
        Name of the fold column.
    folds : int
        Number of folds we want to cut.

    Returns
    -------
    pd.DataFrame
        The resulting dataframe.

    """
    res = df.copy()
    res[name] = np.array((df.index % folds).astype(int))
    return res


def select_and_drop_fold_column(
    df: pd.DataFrame, name: str, fold: int, test: bool
) -> pd.DataFrame:
    """
    Selects the rows that are in fold range, and then drops the fold column.

    If `test` is `True`, selects the rows with `name` equal to `fold`. Otherwise chooses the ones that are not equal.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe.
    name : str
        Name of fold column.
    fold : int
        The fold to select.
    test : bool
        Whether we are selecting test frame or not.

    Returns
    -------
    pd.DataFrame
        The selected dataframe.

    """
    return (
        df.loc[(df[name] == fold) if test else (df[name] != fold)]
        .reset_index(drop=True)
        .drop(columns=[name])
    )

def mean_per_class_error(actual: List[float], pred: List[float]):
    actual = np.array(actual)
    pred = np.array(pred)
    classes = np.unique(actual)
    errors = []
    for c in classes:
        mask = actual == c
        if mask.sum() == 0:
            continue
        c_actual = actual[mask]
        c_pred = pred[mask]
        c_error = 1 - np.mean(c_actual == c_pred)
        errors.append(c_error)
    mean_error = np.mean(errors)
    return mean_error


def get_roc_curve_infomation(actual: pd.Series, pred_proba: np.ndarray) -> Dict:
    actual = actual.astype(float)
    scores = pred_proba[:, 1]
    ths = np.arange(np.min(scores), np.max(scores), 0.0025)
    f1_arrays = np.array([])
    accuracy_arrays = np.array([])
    mean_per_class_error_arrays = np.array([])
    confusion_mat_arrays = np.empty((4, 0))

    for ths_ in ths:
        y_pred = np.where(scores >= ths_, 1, 0)
        confusion_mat_arrays = np.hstack(
            [
                confusion_mat_arrays,
                confusion_matrix(y_true=actual, y_pred=y_pred).ravel().reshape(-1, 1),
            ]
        )

        f1_arrays = np.append(
            f1_arrays, f1_score(y_true=actual, y_pred=y_pred, average="binary")
        )
        accuracy_arrays = np.append(
            accuracy_arrays, accuracy_score(y_true=actual, y_pred=y_pred)
        )
        mean_per_class_error_arrays = np.append(
            mean_per_class_error_arrays,
            mean_per_class_error(pred=y_pred, actual=actual),
        )

    confusion_mat_scores = pd.DataFrame(confusion_mat_arrays.T, dtype=int)
    confusion_mat_scores.columns = ["tns", "fps", "fns", "tps"]

    auc_report = {}
    for val in ["tns", "fps", "fns", "tps"]:
        auc_report[val] = confusion_mat_scores[val].tolist()

    fpr, tpr, _ = roc_curve(actual, scores, pos_label=None)
    # RF: https://stackoverflow.com/questions/53383306/how-to-determine-which-label-is-considered-the-positive-class-in-h2o-binary-cl
    labels = sorted(actual.unique())
    negative_label = str(labels[0])
    positive_label = str(labels[1])
    th_max_by = {
        "accuracy": max(accuracy_arrays),
        "evaluator": max(f1_arrays),
        "f1": max(f1_arrays),
        "mean_per_class_error": min(mean_per_class_error_arrays),
    }
    return FullAUCObjReport(
        auc=auc(fpr, tpr),
        ths=ths.tolist(),
        nonparametric_ths=[],
        fps=auc_report["fps"],
        tps=auc_report["tps"],
        fns=auc_report["fns"],
        tns=auc_report["tns"],
        th_max_by=th_max_by,
        positive_label=positive_label,
        negative_label=negative_label,
    )