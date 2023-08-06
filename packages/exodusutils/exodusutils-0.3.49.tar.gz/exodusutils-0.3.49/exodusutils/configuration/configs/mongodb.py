from __future__ import annotations

import os
import sys
from typing import Dict

from pydantic import BaseModel
from pymongo.encryption_options import AutoEncryptionOpts
from pymongo.mongo_client import MongoClient

from exodusutils.configuration.configs.utils import get_configs


class MongoDBConfigs(BaseModel):
    host: str
    port: int
    database: str
    username: str
    password: str
    migrations: str
    encryption_key: str
    encrypted: bool
    key_vault_col_name: str = "__keyVault"

    @property
    def mongo_host(self) -> str:
        return f"mongodb://{self.host}:{self.port}/{self.database}"

    @property
    def key_vault_namespace(self) -> str:
        return f"{self.database}.{self.key_vault_col_name}"

    @property
    def kms_providers(self) -> Dict:
        return {"local": {"key": str.encode(self.encryption_key)}}

    @classmethod
    def get(cls) -> MongoDBConfigs:
        """
        Will either parse config values from `config.ini` or environment variables.

        The variables we will parse are the following:
        - `EXODUS_MONGO_HOST`:                The host. Default is localhost.
        - `EXODUS_MONGO_PORT`:                An integer. Default is 27017.
        - `EXODUS_MONGO_DATABASE`:            The name of the database. Default is exodus.
        - `EXODUS_MONGO_USERNAME`:            The username. Default is exodus.
        - `EXODUS_MONGO_PASSWORD`:            The password for the user. Default is exodus.
        - `EXODUS_MONGO_MIGRATIONS`:          The name of the migration directory.
        - `EXODUS_MONGO_ENCRYPTION_KEY`:      The encryption key.
        - `EXODUS_MONGO_ENCRYPTED`:           Whether the collection should be encrypted. Default is false.
        """
        configs = get_configs()
        if configs is None:
            default_values = {
                f"EXODUS_MONGO_HOST": "localhost",
                f"EXODUS_MONGO_PORT": 27017,
                f"EXODUS_MONGO_DATABASE": "exodus",
                f"EXODUS_MONGO_USERNAME": "exodus",
                f"EXODUS_MONGO_PASSWORD": "exodus",
                f"EXODUS_MONGO_MIGRATIONS": "migrations",
                f"EXODUS_MONGO_ENCRYPTION_KEY": "0b9980d09b410450d176ae130d20c4a237a882dae0ac366b8699a76d20e6ffe010ebbf90a312499f177693665a517f78",
            }
            encrypted = os.environ.get("EXODUS_MONGO_ENCRYPTED", "False") == "True"
            return cls(
                host=os.environ.get(
                    "EXODUS_MONGO_HOST", default_values["EXODUS_MONGO_HOST"]
                ),
                port=int(
                    os.environ.get(
                        "EXODUS_MONGO_PORT", default_values["EXODUS_MONGO_PORT"]
                    )
                ),
                database=os.environ.get(
                    "EXODUS_MONGO_DATABASE", default_values["EXODUS_MONGO_DATABASE"]
                ),
                username=os.environ.get(
                    "EXODUS_MONGO_USERNAME", default_values["EXODUS_MONGO_USERNAME"]
                ),
                password=os.environ.get(
                    "EXODUS_MONGO_PASSWORD", default_values["EXODUS_MONGO_PASSWORD"]
                ),
                migrations=os.environ.get(
                    "EXODUS_MONGO_MIGRATIONS", default_values["EXODUS_MONGO_MIGRATIONS"]
                ),
                encryption_key=os.environ.get(
                    "EXODUS_MONGO_ENCRYPTION_KEY",
                    default_values["EXODUS_MONGO_ENCRYPTION_KEY"],
                ),
                encrypted=encrypted,
            )
        else:
            configs = configs["mongo"]
            return cls(
                host=configs["host"],
                port=int(configs["port"]),
                database=configs["database"],
                username=configs["username"],
                password=configs["password"],
                migrations=configs["migrations"],
                encryption_key=configs["encryption_key"],
                encrypted=bool(configs["encrypted"]),
            )

    def get_client(self) -> MongoClient:
        key_vault_namespace = f"{self.database}.{self.key_vault_col_name}"
        auto_encryption_opts = AutoEncryptionOpts(
            kms_providers=self.kms_providers,
            key_vault_namespace=key_vault_namespace,
            bypass_auto_encryption=True,
        )
        client = MongoClient(
            host=self.mongo_host,
            username=self.username,
            password=self.password,
            auto_encryption_opts=auto_encryption_opts,
        )
        try:
            # Try find the encryption key here. If it throws it means MongoDB is unreachable.
            # Note: this would not work if the uvicorn reload flag is turned on.
            client.get_database(self.database).get_collection(
                self.key_vault_col_name
            ).find_one(None)
            return client
        except Exception:
            print("Failed to connect to MongoDB, exiting")
            sys.exit(1)
