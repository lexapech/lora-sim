from dataclasses import dataclass
from typing import Any
from .enums import LoraBandwidth, LoraSpreadFactor, LoraCodingRate
from IHaveProperties import IHaveProperties
from Property import Property

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
            "Частота": Property(self,'frequency'),
            "Spread Factor": Property(self,'spread_factor'),
            "Coding Rate": Property(self,'coding_rate'),
            "Ширина канала": Property(self,'bandwidth'),
            "Low DR": Property(self,'low_date_rate'),
            "Header": Property(self,'header'),
            "CRC": Property(self,'crc'),
            "Длина преамбулы": Property(self,'preamble'),
            "Мощность": Property(self,'power')
        }
    def get_minimized(self):
        return ""


