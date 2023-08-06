from pyalgotrader_protocols.algorithm import Algorithm_Protocol


class Strategy_Protocol(Algorithm_Protocol):
    async def initialize(self) -> None:
        ...

    async def next(self) -> None:
        ...
