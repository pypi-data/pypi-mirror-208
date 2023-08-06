import datetime
from abc import abstractmethod

from pyalgotrader_protocols.chart import Chart_Protocol
from pyalgotrader_protocols.store import Store_Protocol


class Algorithm_Protocol(Store_Protocol):
    @abstractmethod
    async def initialize(self) -> None:
        ...

    @abstractmethod
    async def next(self) -> None:
        ...

    async def add_watch_chart(
        self, symbol: str, timeframe: datetime.timedelta
    ) -> Chart_Protocol:
        ...

    async def add_trade_chart(self, symbol: str) -> Chart_Protocol:
        ...
