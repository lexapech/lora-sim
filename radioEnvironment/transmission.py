from dataclasses import dataclass, field
from typing import Any

from .transmissionState import RadioTransmissionState
from .IModem import IModem


@dataclass()
class RadioTransmission:
    def __init__(self):
        self.central_frequency: float = 0
        self.bandwidth: float = 0
        self.power: float = 0
        self.transmitter: IModem = IModem()
        self.flags: list[RadioTransmissionState] = []
        self.data: object = None
