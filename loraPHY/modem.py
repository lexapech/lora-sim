
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
from interfaces.IHaveProperties import IHaveProperties
from networkDevice.INetworkDevice import INetworkDevice
from util.Property import Property
from interfaces.ISerializable import ISerializable

class LoraModem(IEventSubscriber, IModem, IHaveProperties, ISerializable):
    def __init__(self, device: INetworkDevice):
        self.modem_settings = ModemSettings()
        self.modem_state = LoraModemState.IDLE
        self.current_transmission: RadioTransmission or None = None
        self.modem_busy = False
        self.tx_callback = None
        self.device = device
        self.device.add_modem(self)
        self.rx_callback: Callable[[LoraPacket], None] or None = self.device.packet_received
        self.preamble_callback = None
        self.received_buffer_size = 10
        self.event_queue =  device.get_event_queue()
        self.radio_env = device.get_radio_environment()
        self.last_received: LoraPacket or None = None
        self.radio_env.register_modem(self)
        self.event_queue.subscribe(self, (self, "STATE"))

    @staticmethod
    def init(device: INetworkDevice):
        return LoraModem(device)

    def from_json(self,json,attr_types=None):
        return super().from_json(json,{
            'modem_settings': ModemSettings
            })

    def to_json(self,attrs=[]):
        return super().to_json(['modem_settings'])

    def get_properties(self):
        return {"Конфигурация модема": Property(self,'modem_settings', ModemSettings)}

    def get_minimized(self):
        return ""


    def calculate_modem_startup_time(self):
        return 0.0015

    def send(self, payload, length: int or None = None):
        # radio startup
        if length is None:
            length = len(payload)
        if length > len(payload):
            raise ValueError("Length greater than payload length")
        self.current_transmission = RadioTransmission(self.modem_settings.frequency,
        calculate_lora_bandwidth(self.modem_settings.bandwidth),
        self.modem_settings.power,
        self,
        LoraPacket(self.modem_settings,payload).modulate())
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
            if isinstance(self.current_transmission, RadioTransmission):
                #duration = calculate_lora_packet_time(self.modem_settings, self.current_transmission.data.length)
                duration = self.current_transmission.data[1]*1000000
                self.modem_state = new_state
                print("her")
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

            packet = LoraPacket(self.modem_settings)

            data, _ = packet.demodulate(self.current_transmission.data[0],
            self.current_transmission.data[1],
            self.current_transmission.power,
            self.radio_env.noise_floor_db)
             
            if data[1] == 0:
                self.last_received = (data,self.current_transmission.power,self.radio_env.noise_floor_db)
                self.current_transmission = None
                if self.rx_callback is not None:
                    try:
                        self.rx_callback(self.last_received)
                    except Exception as e:
                        self.device.get_logger().log(repr(e),self.device)
            else:
                self.current_transmission = None
            print(self,self.modem_state)
           

    def notify(self, env: IEventQueue, event: DiscreteEvent):
        if (self, "STATE") in event.tags and isinstance(event.data, LoraModemState):
            self.process_state_change(event.data)
        else:
            raise Exception(f'Unknown event received {event.data}')

        pass

    def transmission_start_notify(self, transmission: RadioTransmission):
        print(self,self.modem_state)
        if isinstance(transmission.transmitter, LoraModem) \
                and transmission.transmitter != self \
                and self.modem_state in [LoraModemState.IDLE] \
                and abs(transmission.central_frequency - self.modem_settings.frequency) < 1000:

            preamble_time = calculate_lora_preamble_time(transmission.transmitter.modem_settings)
            self.current_transmission = transmission
           
            self.modem_state=LoraModemState.RECEIVING

    def transmission_end_notify(self, transmission: RadioTransmission):
        if self.modem_state in [LoraModemState.TRANSMITTING] and transmission.transmitter == self:
            self.process_state_change(LoraModemState.TX_DONE)
        elif self.modem_state in [LoraModemState.RECEIVING]:
            self.process_state_change(LoraModemState.RX_DONE)

    def get_position(self) -> tuple[float, float]:
        return (self.device.position.x,self.device.position.y)