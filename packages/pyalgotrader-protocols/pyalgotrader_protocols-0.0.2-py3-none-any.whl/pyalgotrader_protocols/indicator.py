from typing import Any, Protocol

import pandas as pd


class Indicator_Protocol(Protocol):
    data: pd.DataFrame | pd.Series

    async def run(self, df: pd.DataFrame) -> None:
        ...
