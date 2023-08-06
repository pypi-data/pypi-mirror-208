import os

from minio import Minio
from pydantic.main import BaseModel
from typing import Any

from exodusutils.configuration.configs.grpc import GPRCConfigs
from exodusutils.configuration.configs.minio import MinioConfigs
from exodusutils.configuration.configs.mongodb import MongoDBConfigs
from exodusutils.configuration.configs.utils import get_configs
from exodusutils.configuration.mongo_instance import MongoInstance


class Configs(BaseModel):
    mongodb_configs: MongoDBConfigs
    minio_configs: MinioConfigs
    grpc_configs: GPRCConfigs
    cores: int

    @classmethod
    def get(cls, name: str):
        mongodb_configs = MongoDBConfigs.get()
        minio_configs = MinioConfigs.get()
        grpc_configs = GPRCConfigs.get()
        configs = get_configs()
        if configs is None:
            cores_key = f"EXODUS_{name.upper()}_CORES"
            cpus = os.cpu_count()
            default_values = {cores_key: 1 if cpus is None else cpus}
            cores = int(os.environ.get(cores_key, default_values[cores_key]))
        else:
            configs = configs["exodus"]
            cores = int(configs["cores"])
        return cls(
            mongodb_configs=mongodb_configs, minio_configs=minio_configs, grpc_configs=grpc_configs, cores=cores
        )

    @property
    def mongo_instance(self) -> MongoInstance:
        return MongoInstance(self.mongodb_configs)

    @property
    def minio_instance(self) -> Minio:
        return self.minio_configs.get_client()

    @property
    def grpc_channel(self) -> Any:
        return self.grpc_configs.get_insecure_channel()