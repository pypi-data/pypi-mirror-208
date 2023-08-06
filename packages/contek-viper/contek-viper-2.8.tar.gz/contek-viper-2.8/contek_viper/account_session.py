from typing import Iterable

from contek_viper.execution.execution_service_pb2 import MarketSignal, SubmitMarketSignalsRequest
from contek_viper.execution.execution_service_pb2_grpc import ExecutionServiceStub


class AccountSession:

    def __init__(
        self,
        exchange: str,
        account: str,
        stub: ExecutionServiceStub,
    ) -> None:
        self._exchange = exchange
        self._account = account
        self._stub = stub

    def submit(self, market_signals: Iterable[MarketSignal]) -> None:
        self._stub.SubmitMarketSignals(
            SubmitMarketSignalsRequest(
                market_signal=list(market_signals),
                exchange=self._exchange,
                account=self._account,
            ))
