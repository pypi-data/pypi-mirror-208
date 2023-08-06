import base64
import pickle
import warnings
import minio
from typing import Any, Dict, List, Tuple, Optional
from io import BytesIO
from minio import Minio
from exodusutils.configuration import MongoInstance, identify
from exodusutils.exceptions import ExodusNotFound
from exodusutils.constants import PREDICTION_COLNAME
from exodusutils.schemas.model import SingleModel
from pydantic import BaseModel
from pymongo.collection import Collection

warnings.simplefilter("ignore", FutureWarning)

MINIO_BUCKET_NAME = "models"

def save_stuff_to_minio(uri: str, content: bytes, minio: Minio) -> str:
    """
    Stores stuff to Minio.

    Parameters
    ----------
    stuff : bytes
        Whatever you want to store. For Python classes you might want to pickle them
        before calling this method.

    Returns
    -------
    str
        The stringified id of the stuff you just stored.
    """
    # FIXME Be extra careful when storing sklearn stuff: there is virtually no backwards compatibility if you pickle
    # scikit-learn pipelines!
    # Reference: https://scikit-learn.org/stable/modules/model_persistence.html#security-maintainability-limitations
    # Either use ONNX, PMML (this requires Java), or try to dump your model to a bytearray!
    # content = pickle.dumps(stuff)
    minio.put_object(MINIO_BUCKET_NAME, uri, BytesIO(content), len(content))
    return uri

def load_stuff_from_minio(uri: str, minio: Minio) -> bytes:
    """
    Loads stuff back from Minio.

    Parameters
    ----------
    uri: str
        The URI for the stored stuff.
    minio : Minio
        The Minio instance.

    Returns
    -------
    bytes
        Whatever you just stored during training.
    """
    try:
        content = minio.get_object(MINIO_BUCKET_NAME, uri)
        return content.read()
    except Exception:
        # Some algos. didn't had exist model like arima
        # They save model with time_group_id
        pass
    return None

# FIXME there are probably better ways to do this!
def dump_to_base64(stuff: Any) -> bytes:
    """
    Dumps the thing to pickle format, then encodes the result with `b64encode`.
    """
    return base64.b64encode(pickle.dumps(stuff))

def get_prediction_header(
    has_target: bool, 
    keep_columns: List[str], 
    datetime_column: str, 
    time_groups: List[str],
    target_name: str
) -> List[str]:
    """
    Returns the appropriate header for the predicted results.

    Parameters
    ----------
    has_target : bool
        Whether the target column exists in the prediction's input dataframe.
    keep_columns : List[str]
        A list of column names that the user wants to preserve in the response.

    Returns
    -------
    List[str]
        The column names of the response dataframe.
    """
    return (
        [datetime_column]
        + time_groups
        + [PREDICTION_COLNAME]
        + ([target_name] if has_target else [])
        + keep_columns
    )

class ModelStore(BaseModel):
    """
    We define connector here.
    """
    name: str
    minio: Minio
    mongo: MongoInstance
    db_collection: Collection

    class Config:
        arbitrary_types_allowed = True

    def save(
        self,
        model_id: str,
        single_model: SingleModel,
        model_bytes: bytes = None,
        extra_attributes: Dict[str, bytes] = {},
    ) -> str:
        """
        Saves the `SingleModel` object into MongoDB, and upload the model itself and extra attributes onto Minio.
        Returns the ID of the saved object.

        Parameters
        ----------
        model_id : str
            Identifier for the model. Used to generate URIs in Minio bucket.
        single_model : SingleModel
            The MongoDB document for the model.
        model_bytes : bytes
            The actual model dumped into a sequence of bytes. Note that for algorithms comprising of multiple
            models (i.e. arima, theta, ets, etc.), it does not make sense to store all those models as a single
            pickled model. In those cases user should store them in `extra_attributes`.
        extra_attributes : Dict[str, bytes]
            Any extra attribute that is supposed to be stored by the algorithms goes in here.

        Returns
        -------
        str
            The ID of the saved SingleModel.
        """

        if model_bytes:
            save_stuff_to_minio(
                f"{single_model.experiment}/{self.name}_{model_id}", model_bytes, self.minio
            )
        # Also save other stuff
        for key, value in extra_attributes.items():
            save_stuff_to_minio(
                f"{single_model.experiment}/{self.name}_{key}",
                value,
                self.minio,
            )

        doc = single_model.dict(by_alias=True)
        doc["_id"] = identify(model_id=model_id).get("_id")
        return str(self.db_collection.insert_one(doc).inserted_id)


    def load(
        self,
        model_id: str,
        keys: List[str],
    ) -> Tuple[SingleModel, Optional[bytes], Dict[str, bytes]]:
        """
        Loads the model and extra attributes from Minio.

        Parameters
        ----------
        model_id : str
            ID for the stored model.
        keys : List[str]
            The keys for the extra attributes. Algorithms should keep the list of available keys
            themselves so that it is consistent between training and predicting.

        Returns
        -------
        (SingleModel, bytes, Dict[str, bytes])
            The stored MongoDB document, the model as a sequence of bytes, and the extra attributes.
        """
        obj = self.db_collection.find_one(filter=identify(model_id))
        if not obj:
            raise ExodusNotFound(f"No model found with id = {model_id}")
        single_model = SingleModel.parse_obj(obj)
        minio_path_prefix = f"{single_model.experiment}/{self.name}_"
        model_bytes: Any = load_stuff_from_minio(minio_path_prefix + model_id, self.minio)

        # load other stuff from model_info.options
        extra_attributes = {
            key: load_stuff_from_minio(f"{minio_path_prefix}{key}", self.minio) for key in keys
        }
        return single_model, model_bytes, extra_attributes

