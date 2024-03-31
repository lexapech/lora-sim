from enum import Enum

class LoraSpreadFactor(Enum):
    UNDEFINED = 0
    SF_5 = 5
    SF_6 = 6
    SF_7 = 7
    SF_8 = 8
    SF_9 = 9
    SF_10 = 10
    SF_11 = 11
    SF_12 = 12


class LoraBandwidth(Enum):
    UNDEFINED = 0
    BW_125 = 1
    BW_250 = 2
    BW_500 = 3


class LoraCodingRate(Enum):
    UNDEFINED = 0
    CR_4_5 = 1
    CR_4_6 = 2
    CR_4_7 = 3
    CR_4_8 = 4


class LoraModemState(Enum):
    IDLE = 0
    STARTED = 1
    TRANSMITTING = 2
    TX_DONE = 3
    RECEIVING = 4
    RX_DONE = 5
    PREAMBLE_DETECTED = 6

