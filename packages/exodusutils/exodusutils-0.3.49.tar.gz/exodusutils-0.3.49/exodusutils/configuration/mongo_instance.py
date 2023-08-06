from typing import Any, Dict

from bson import Binary
from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from bson.objectid import ObjectId
from gridfs import GridFS
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.encryption import Algorithm, ClientEncryption

from exodusutils.configuration.configs.mongodb import MongoDBConfigs


class MongoInstance:
    def __init__(self, configs: MongoDBConfigs) -> None:
        """
        Initializes a MongoInstaListnce containing a MongoDB client and an encryption client.
        """

        self.is_encrypted = configs.encrypted
        self.client: MongoClient = configs.get_client()
        self.db = self.client.get_database(configs.database)

        self.encryption_client = ClientEncryption(
            kms_providers=configs.kms_providers,
            key_vault_namespace=configs.key_vault_namespace,
            key_vault_client=self.client,
            codec_options=CodecOptions(uuid_representation=STANDARD),
        )

        key_vault = self.db.get_collection(configs.key_vault_col_name)
        key = key_vault.find_one(None)
        if key is not None:
            self.data_key_id = Binary(key["_id"], 4)
        else:
            key_vault.create_index(
                "keyAltNames",
                unique=True,
                partialFilterExpression={"keyAltNames": {"$exists": True}},
            )
            self.data_key_id = self.encryption_client.create_data_key(
                "local", key_alt_names=["pymongo_encryption"]
            )

    def gen_id(self) -> Any:
        return str(ObjectId())

    def get_collection(self, name: str) -> Collection:
        """
        Returns a handle to a MongoDB collection. Will create one if there's none with the given `name`.
        """
        return self.db.get_collection(name)

    def get_gridfs(self) -> GridFS:
        """
        Returns a handle to the MongoDB `GridFS`, where you can store arbitrary objects that might exceed 4MB.
        """
        return GridFS(self.db)

    def encrypt(self, value: Any) -> Any:
        """
        Either encrypts `value` if `encrypted` is set to `True` in `config.ini`, or returns it as if otherwise.
        """
        if self.is_encrypted:
            return self.encryption_client.encrypt(
                value, Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Random, self.data_key_id
            )
        else:
            return value


def identify(model_id: str) -> Dict:
    return {"_id": ObjectId(model_id)}
