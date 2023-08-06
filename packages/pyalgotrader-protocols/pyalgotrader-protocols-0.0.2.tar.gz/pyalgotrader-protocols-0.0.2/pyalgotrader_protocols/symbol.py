from typing import Protocol


class Symbol_Protocol(Protocol):
    segment: str
    name: str
    lot_size: int
    tradable: bool
