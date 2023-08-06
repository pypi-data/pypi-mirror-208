import abc
from typing import Any, Dict, List, Type

from pyalgotrader_protocols.broker import Broker_Protocol


class BrokerManager_Protocol(abc.ABC):
    available_brokers: List[str]
    available_modes: List[str]
    modes: Dict[str, Type[Broker_Protocol]]
    brokers: Dict[str, Type[Broker_Protocol]]

    @abc.abstractmethod
    def instance(self) -> "BrokerManager_Protocol":
        raise NotImplementedError

    @abc.abstractmethod
    async def get_broker(
        self, mode: str, broker_name: str, broker_config: Dict[str, str]
    ) -> Broker_Protocol:
        raise NotImplementedError
