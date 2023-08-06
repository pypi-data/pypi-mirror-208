from __future__ import annotations

import os
from pydantic.main import BaseModel
from typing import Any

import grpc
from exodusutils.configuration.configs.utils import get_configs


class GPRCConfigs(BaseModel):
    host: str
    port: int

    @classmethod
    def get(cls) -> GPRCConfigs:
        """
        Will either parse config values from `config.ini` or environment variables.

        The variables we will parse are the following:
        - `EXODUS_GRPC_HOST`:                The host. Default is `"localhost"`.
        - `EXODUS_GRPC_PORT`:                An integer. Default is `8080`.
        """
        configs = get_configs()
        if configs is None:
            default_values = {
                f"EXODUS_GRPC_HOST": "localhost",
                f"EXODUS_GRPC_PORT": 8080,
            }
            return cls(
                host=os.environ.get(
                    "EXODUS_GRPC_HOST", default_values["EXODUS_GRPC_HOST"]
                ),
                port=os.environ.get(
                    "EXODUS_GRPC_PORT", default_values["EXODUS_GRPC_PORT"]
                ),
            )
        else:
            configs = configs["gRPC"]
            return cls(
                host=configs["host"],
                port=int(configs["port"]),
            )

    def get_insecure_channel(self) -> Any:
        return grpc.insecure_channel(f"{self.host}:{self.port}")
