from typing import Iterable

from contek_viper.execution.execution_service_pb2 import TriggerMarketSignal, SubmitTriggerRequest
from contek_viper.execution.execution_service_pb2_grpc import ExecutionServiceStub


class TriggerApi:

    def __init__(
        self,
        trigger_name: str,
        stub: ExecutionServiceStub,
    ) -> None:
        self._trigger_name = trigger_name
        self._stub = stub

    def submit(self, market_signals: Iterable[TriggerMarketSignal]) -> None:
        self._stub.SubmitTrigger(
            SubmitTriggerRequest(
                trigger_name=self._trigger_name,
                market_signal=list(market_signals),
            ))
