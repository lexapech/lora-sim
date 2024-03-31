from dataclasses import dataclass
from typing import Any
from .enums import LoraBandwidth, LoraSpreadFactor, LoraCodingRate


@dataclass()
class ModemSettings:
    frequency: int = 0
    spread_factor: LoraSpreadFactor = LoraSpreadFactor.UNDEFINED
    coding_rate: LoraCodingRate = LoraCodingRate.UNDEFINED
    bandwidth: LoraBandwidth = LoraBandwidth.UNDEFINED
    low_date_rate = False
    header = False
    crc = False
    preamble = 0
    power = 0

