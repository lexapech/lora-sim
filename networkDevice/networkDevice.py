from loraPHY.modem import IModem
from networkDevice.deviceTimer import DeviceTimer
from IHaveProperties import IHaveProperties
from position import Position
from radioEnvironment.radioEnvironment import RadioEnvironment
from networkDevice.INetworkDevice import INetworkDevice
from loraPHY.loraPacket import LoraPacket
from loraPHY.modem import LoraModem
from Property import Property

class LoraDevice(IHaveProperties, INetworkDevice):
    def __init__(self, radio_env: RadioEnvironment):
        self.name = ""
        self.position = Position(0, 0)
        self.modems: list[LoraModem] = []
        self.timers: dict[str, DeviceTimer] = {}
        self.routing_strategy = None
        self.radio_env = radio_env
        self.event_queue = radio_env.event_queue

    def add_modem(self, modem: LoraModem):
        if modem not in self.modems:
            self.modems.append(modem)
        else:
            raise ValueError("modem already added")

    def add_timer(self, name, timer: DeviceTimer):
        if self.timers.get(name) is None:
            self.timers[name] = timer
        else:
            raise ValueError("modem already added")

    def get_modems(self):
        return self.modems

    def get_timers(self):
        return self.timers

    def get_event_queue(self):
        return self.event_queue

    def get_radio_environment(self):
        return self.radio_env

    def packet_received(self, packet: LoraPacket):
        pass

    def get_position(self):
        return self.position

    def send_packet(self, data, modem):
        self.modems[modem].send(data, len(data))

    def get_properties(self):
        return {
            "Имя": Property(self,'name'),
            "Позиция": Property(self,'position'),
            "Модемы": Property(self,'modems'),
            "Таймеры": Property(self,'timers'),
            "Алгоритм маршрутизации": Property(self,'routing_strategy')
            }
    def get_minimized(self):
        return ""
