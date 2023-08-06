import datetime
from typing import Callable, Protocol

import pandas as pd

from pyalgotrader_protocols.indicator import Indicator_Protocol
from pyalgotrader_protocols.symbol import Symbol_Protocol


class Chart_Protocol(Protocol):
    symbol: Symbol_Protocol

    timeframe: datetime.timedelta

    data: pd.DataFrame | pd.Series

    async def add_indicator(
        self, fn: Callable[[pd.DataFrame], pd.DataFrame | pd.Series | None]
    ) -> Indicator_Protocol:
        ...
