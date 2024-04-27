from dataclasses import dataclass
from typing import Any
from .enums import LoraBandwidth, LoraSpreadFactor, LoraCodingRate
from interfaces.IHaveProperties import IHaveProperties
from util.Property import Property
from interfaces.ISerializable import ISerializable

@dataclass()
class ModemSettings(IHaveProperties, ISerializable):
    frequency: int = 0
    spread_factor: LoraSpreadFactor = LoraSpreadFactor.UNDEFINED
    coding_rate: LoraCodingRate = LoraCodingRate.UNDEFINED
    bandwidth: LoraBandwidth = LoraBandwidth.UNDEFINED
    low_date_rate = False
    header = False
    crc = False
    preamble = 0
    power = 0

    @staticmethod
    def init(arg):
        return ModemSettings()

    def from_json(self,json,attr_types=None):
        return super().from_json(json,{
            'frequency': int,
            'spread_factor': LoraSpreadFactor,
            'coding_rate':LoraCodingRate,
            'bandwidth': LoraBandwidth,
            'low_date_rate': bool,
            'header':bool,
            'crc': bool,
            'preamble':int,
            'power': float
            })

    def to_json(self,attrs=[]):
        return super().to_json(list(self.__dict__.keys()))

    def get_properties(self):
        return {
            "Частота": Property(self,'frequency',int),
            "Spread Factor": Property(self,'spread_factor'),
            "Coding Rate": Property(self,'coding_rate'),
            "Ширина канала": Property(self,'bandwidth'),
            "Low DR": Property(self,'low_date_rate'),
            "Header": Property(self,'header'),
            "CRC": Property(self,'crc'),
            "Длина преамбулы": Property(self,'preamble'),
            "Мощность": Property(self,'power',float)
        }
    def get_minimized(self):
        return ""


