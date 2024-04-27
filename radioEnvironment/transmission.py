from dataclasses import dataclass, field
from typing import Any

from .transmissionState import RadioTransmissionState
from .IModem import IModem


class RadioTransmission:
    def __init__(self, central_frequency,bandwidth,power,transmitter,data):
        self.central_frequency: float = central_frequency
        self.bandwidth: float = bandwidth
        self.power: float = power
        self.transmitter: IModem = transmitter
        self.flags: list[RadioTransmissionState] = []
        self.data: object = data
