
# send

# freq
# spread factor
# code rate
# power
# bandwidth
# crc
# preamble
# header
# payload
# payload_len

# receive

# freq
# spread factor
# code rate
# power
# bandwidth
# crc
# preamble
# header
# payload
# payload_len
# rssi
# snr

# channel activity
from eventSimulator.IEventQueue import IEventQueue
from eventSimulator.event import DiscreteEvent
from eventSimulator.IEventSubscriber import IEventSubscriber
from loraPHY.enums import LoraModemState
from loraPHY.modemSettings import ModemSettings
from loraPHY.lora import calculate_lora_preamble_time, calculate_lora_packet_time, calculate_lora_bandwidth
from radioEnvironment.IModem import IModem
from radioEnvironment.transmission import RadioTransmission
from radioEnvironment.radioEnvironment import RadioEnvironment
from loraPHY.loraPacket import LoraPacket
from typing import Callable


class LoraModem(IEventSubscriber, IModem):
    def __init__(self, event_queue: IEventQueue, radio_env: RadioEnvironment):
        self.modem_settings = ModemSettings()
        self.modem_state = LoraModemState.IDLE
        self.current_transmission: RadioTransmission or None = None
        self.modem_busy = False
        self.tx_callback = None
        self.position = (0, 0)
        self.rx_callback: Callable[[LoraPacket], None] or None = None
        self.preamble_callback = None
        self.received_buffer_size = 10
        self.event_queue = event_queue
        self.radio_env = radio_env
        self.last_received: LoraPacket or None = None
        self.radio_env.register_modem(self)
        self.event_queue.subscribe(self, (self, "STATE"))

    def calculate_modem_startup_time(self):
        return 0.0015

    def send(self, payload, length: int or None = None):
        # radio startup
        if length is None:
            length = len(payload)
        if length > len(payload):
            raise ValueError("Length greater than payload length")

        self.current_transmission = RadioTransmission()
        self.current_transmission.central_frequency = self.modem_settings.frequency
        self.current_transmission.transmitter = self
        self.current_transmission.power = self.modem_settings.power
        self.current_transmission.bandwidth = calculate_lora_bandwidth(self.modem_settings.bandwidth)
        self.current_transmission.data = LoraPacket(self.modem_settings.spread_factor,
                                                    self.modem_settings.coding_rate,
                                                    self.modem_settings.bandwidth)
        self.current_transmission.data.crc = self.modem_settings.crc
        self.current_transmission.data.data = payload
        self.current_transmission.data.low_date_rate = self.modem_settings.low_date_rate
        self.current_transmission.data.header = self.modem_settings.header
        self.current_transmission.data.preamble = self.modem_settings.preamble
        self.current_transmission.data.length = length
        self.modem_busy = True
        self.process_state_change(LoraModemState.STARTED)

    def change_state_after(self, new_state: LoraModemState, delay: float):
        e = DiscreteEvent()
        e.tags = [(self, "STATE")]
        e.sender = self
        e.data = new_state
        self.event_queue.schedule_event_after(e, delay)

    def set_tx_done_callback(self, cb):
        self.tx_callback = cb

    def set_rx_done_callback(self, cb):
        self.rx_callback = cb

    def set_preamble_callback(self, cb):
        self.preamble_callback = cb

    def process_state_change(self, new_state: LoraModemState):
        if new_state == LoraModemState.STARTED:
            self.modem_state = new_state
            self.change_state_after(LoraModemState.TRANSMITTING, self.calculate_modem_startup_time())
        elif new_state == LoraModemState.TRANSMITTING:
            if isinstance(self.current_transmission, RadioTransmission) \
                    and isinstance(self.current_transmission.data, LoraPacket):
                duration = calculate_lora_packet_time(self.modem_settings, self.current_transmission.data.length)
                self.modem_state = new_state
                self.radio_env.start_transmission(self.current_transmission, duration / 1000000.0)
        elif new_state == LoraModemState.PREAMBLE_DETECTED:
            self.modem_busy = True
            self.modem_state = LoraModemState.RECEIVING
            if self.preamble_callback is not None:
                self.preamble_callback()
        elif new_state == LoraModemState.TX_DONE:
            self.modem_busy = False
            self.current_transmission = None
            self.modem_state = LoraModemState.IDLE
            if self.tx_callback is not None:
                self.tx_callback()
        elif new_state == LoraModemState.RX_DONE:
            self.modem_busy = False
            self.modem_state = LoraModemState.IDLE
            if isinstance(self.current_transmission.data, LoraPacket):
                self.last_received = self.current_transmission.data
                if self.rx_callback is not None:
                    self.rx_callback(self.last_received)

            self.current_transmission = None

    def notify(self, env: IEventQueue, event: DiscreteEvent):
        if (self, "STATE") in event.tags and isinstance(event.data, LoraModemState):
            self.process_state_change(event.data)
        else:
            raise Exception(f'Unknown event received {event.data}')

        pass

    def transmission_start_notify(self, transmission: RadioTransmission):
        if isinstance(transmission.transmitter, LoraModem) \
                and transmission.transmitter != self \
                and isinstance(transmission.data, LoraPacket) \
                and self.modem_state in [LoraModemState.IDLE] \
                and abs(transmission.central_frequency - self.modem_settings.frequency) < 1000\
                and transmission.data.bandwidth == self.modem_settings.bandwidth \
                and transmission.data.coding_rate == self.modem_settings.coding_rate\
                and transmission.data.spread_factor == self.modem_settings.spread_factor:

            preamble_time = calculate_lora_preamble_time(transmission.transmitter.modem_settings)
            self.current_transmission = transmission
            self.change_state_after(LoraModemState.PREAMBLE_DETECTED, preamble_time / 1000000.0)

    def transmission_end_notify(self, transmission: RadioTransmission):
        if self.modem_state in [LoraModemState.TRANSMITTING] and transmission.transmitter == self:
            self.process_state_change(LoraModemState.TX_DONE)
        elif self.modem_state in [LoraModemState.RECEIVING]:
            print(transmission.power)
            self.process_state_change(LoraModemState.RX_DONE)

    def get_position(self) -> tuple[float, float]:
        return self.position
