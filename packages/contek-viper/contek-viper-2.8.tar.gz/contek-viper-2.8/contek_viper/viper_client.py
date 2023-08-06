from __future__ import annotations

import grpc

from contek_viper.account_session import AccountSession
from contek_viper.execution.execution_service_pb2_grpc import ExecutionServiceStub
from contek_viper.trigger_api import TriggerApi


class ViperClient:

    def __init__(self, stub: ExecutionServiceStub) -> None:
        self._stub = stub

    @classmethod
    def create(cls, server_address: str) -> ViperClient:
        channel = grpc.insecure_channel(server_address)
        stub = ExecutionServiceStub(channel)
        return cls(stub)

    def session(self, exchange: str, account: str) -> AccountSession:
        return AccountSession(exchange, account, self._stub)

    def trigger(self, trigger_name: str) -> TriggerApi:
        return TriggerApi(trigger_name, self._stub)
