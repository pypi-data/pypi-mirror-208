import datetime
from typing import Callable, List, Protocol

from pyalgotrader_core.data import Data


class Feed_Protocol(Protocol):
    async def fetch_data(
        self, symbol: str, timeframe: datetime.timedelta, fetch_from: int, fetch_to: int
    ) -> List[Data]:
        ...

    async def subscribe(
        self, symbol: str, on_messages: Callable[[List[Data]], None]
    ) -> None:
        ...

    async def unsubscribe(self, symbol: str) -> None:
        ...
