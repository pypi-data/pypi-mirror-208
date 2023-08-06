from typing import Any

from prefect.logging.loggers import get_run_logger
from pydantic import BaseModel

from src.external.grpc.prefect_routing_pb2 import (ExodusPredictResult,
                                                   FailedResult,
                                                   TrainAutoMLResult,
                                                   TrainAutoTSFResult)
from src.external.grpc.prefect_routing_pb2_grpc import \
    PrefectRoutingServiceStub


class GRPCClient(BaseModel):
    stub: PrefectRoutingServiceStub = None

    class Config:
        arbitrary_types_allowed = True

    def init_app(self, grpc_channel: str):
        try:
            self.stub = PrefectRoutingServiceStub(grpc_channel)
            # We need echo function to test remote grpc server is live
        except:
            self.stub = None
            get_run_logger().warn("Cannot find route stubs, ignoring gRPC messages")

    async def send_train_iid_result(self, result: TrainAutoMLResult) -> None:
        try:
            if self.stub:
                get_run_logger().info(f"Sending TrainAutoMLResult via gRPC = {result}")
                self.stub.trainAutoML(result)
        except Exception as e:
            get_run_logger().warn(str(e))

    async def send_train_tsf_result(self, result: TrainAutoTSFResult) -> None:
        try:
            if self.stub:
                get_run_logger().info(f"Sending TrainAutoTSFResult via gRPC = {result}")
                self.stub.trainAutoTSF(result)
        except Exception as e:
            get_run_logger().warn(str(e))

    async def send_predict_result(self, result: ExodusPredictResult) -> None:
        try:
            if self.stub:
                get_run_logger().info(f"Sending prediction result via gRPC = {result}")
                self.stub.exodusPredict(result)
        except Exception as e:
            get_run_logger().warn(str(e))

    async def send_failed_result(self, result: FailedResult) -> None:
        try:
            if self.stub:
                get_run_logger().info(f"Sending failed result via gRPC = {result}")
                self.stub.failed(result)
        except Exception as e:
            get_run_logger().warn(str(e))
