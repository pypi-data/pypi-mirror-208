import datetime
from abc import ABC, abstractmethod

from pyalgotrader_protocols.chart import Chart_Protocol


class Store_Protocol(ABC):
    @abstractmethod
    async def add_watch_chart(
        self, symbol: str, timeframe: datetime.timedelta, warmups: int
    ) -> Chart_Protocol:
        ...

    @abstractmethod
    async def add_trade_chart(self, symbol: str) -> Chart_Protocol:
        ...

    async def boot(self) -> None:
        ...

    async def run(self) -> None:
        ...
