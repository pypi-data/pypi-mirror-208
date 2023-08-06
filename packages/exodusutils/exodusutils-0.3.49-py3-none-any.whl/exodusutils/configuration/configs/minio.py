from __future__ import annotations

import os

from minio.api import Minio
from pydantic.main import BaseModel

from exodusutils.configuration.configs.utils import get_configs


class MinioConfigs(BaseModel):
    host: str
    port: int
    username: str
    password: str

    @classmethod
    def get(cls) -> MinioConfigs:
        """
        Will either parse config values from `config.ini` or environment variables.

        The variables we will parse are the following:
        - `EXODUS_MINIO_HOST`:                The host. Default is `"localhost"`.
        - `EXODUS_MINIO_PORT`:                An integer. Default is `9000`.
        - `EXODUS_MINIO_USERNAME`:            The username. Default is `"minioadmin"`.
        - `EXODUS_MINIO_PASSWORD`:            The password for the user. Default is `"minioadmin"`.
        """
        configs = get_configs()
        if configs is None:
            default_values = {
                f"EXODUS_MINIO_HOST": "localhost",
                f"EXODUS_MINIO_PORT": 9000,
                f"EXODUS_MINIO_USERNAME": "minioadmin",
                f"EXODUS_MINIO_PASSWORD": "minioadmin",
            }
            return cls(
                host=os.environ.get(
                    "EXODUS_MINIO_HOST", default_values["EXODUS_MINIO_HOST"]
                ),
                port=os.environ.get(
                    "EXODUS_MINIO_PORT", default_values["EXODUS_MINIO_PORT"]
                ),
                username=os.environ.get(
                    "EXODUS_MINIO_USERNAME", default_values["EXODUS_MINIO_USERNAME"]
                ),
                password=os.environ.get(
                    "EXODUS_MINIO_PASSWORD", default_values["EXODUS_MINIO_PASSWORD"]
                ),
            )
        else:
            configs = configs["minio"]
            return cls(
                host=configs["host"],
                port=int(configs["port"]),
                username=configs["username"],
                password=configs["password"],
            )

    def get_client(self) -> Minio:
        return Minio(
            f"{self.host}:{self.port}",
            access_key=self.username,
            secret_key=self.password,
            secure=False,
        )
