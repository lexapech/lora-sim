from .modemSettings import ModemSettings
from .enums import LoraBandwidth, LoraSpreadFactor, LoraCodingRate
import math


def calculate_lora_bandwidth(bw: LoraBandwidth):
    if bw == LoraBandwidth.BW_125:
        return 125000
    elif bw == LoraBandwidth.BW_250:
        return 250000
    elif bw == LoraBandwidth.BW_500:
        return 500000


def calculate_lora_symbol_time(settings: ModemSettings):
    if settings.spread_factor not in LoraSpreadFactor:
        raise Exception("Wrong LoRa spreading factor")
    if settings.coding_rate not in LoraCodingRate:
        raise Exception("Wrong LoRa coding rate")
    if settings.bandwidth == LoraBandwidth.BW_125:
        bw_pow = 1
    elif settings.bandwidth == LoraBandwidth.BW_250:
        bw_pow = 2
    elif settings.bandwidth == LoraBandwidth.BW_500:
        bw_pow = 4
    else:
        raise Exception("Wrong LoRa bandwidth")
    return (1 << settings.spread_factor.value) * 8 / bw_pow


def calculate_lora_preamble_time(settings: ModemSettings):
    symbol_time = calculate_lora_symbol_time(settings)
    return settings.preamble * symbol_time


def calculate_lora_payload_time(settings: ModemSettings, payload_len: int):
    symbol_time = calculate_lora_symbol_time(settings)
    h = 1 if settings.header is True else 0
    de = 1 if settings.low_date_rate is True else 0
    n_bit_crc = 16 if settings.crc is True else 0

    n_symbol_payload = math.ceil(max((8 * payload_len + n_bit_crc - 4 * settings.spread_factor.value
                                      + (8 if settings.spread_factor.value >= 7 else 0) + 20 * h), 0.0) /
                                 (4 * (settings.spread_factor.value - 2 * de)))*(settings.coding_rate.value + 4)
    return n_symbol_payload * symbol_time


def calculate_lora_packet_time(settings: ModemSettings, payload_len: int):
    symbol_time = calculate_lora_symbol_time(settings)
    h = 1 if settings.header is True else 0
    de = 1 if settings.low_date_rate is True else 0
    n_bit_crc = 16 if settings.crc is True else 0

    n_symbol_payload = math.ceil(max((8 * payload_len + n_bit_crc - 4 * settings.spread_factor.value
                                      + (8 if settings.spread_factor.value >= 7 else 0) + 20 * h), 0.0) /
                                 (4 * (settings.spread_factor.value - 2 * de))) * (settings.coding_rate.value + 4)
    symbols = settings.preamble + (4.25 if settings.spread_factor.value >= 7 else 6.25) + 8.0 + n_symbol_payload
    return symbol_time * symbols

