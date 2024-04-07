from dataclasses import dataclass
from typing import Any
from .enums import LoraBandwidth, LoraSpreadFactor, LoraCodingRate
from IHaveProperties import IHaveProperties

@dataclass()
class ModemSettings(IHaveProperties):
    frequency: int = 0
    spread_factor: LoraSpreadFactor = LoraSpreadFactor.UNDEFINED
    coding_rate: LoraCodingRate = LoraCodingRate.UNDEFINED
    bandwidth: LoraBandwidth = LoraBandwidth.UNDEFINED
    low_date_rate = False
    header = False
    crc = False
    preamble = 0
    power = 0

    def get_properties(self):
        return {
            "Частота": self.frequency,
            "Spread Factor": self.spread_factor,
            "Coding Rate": self.coding_rate,
            "Ширина канала": self.bandwidth,
            "Low DR": self.low_date_rate,
            "Header": self.header,
            "CRC": self.crc,
            "Длина преамбулы": self.preamble,
            "Мощность": self.power
        }

