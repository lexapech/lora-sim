from radiosim2.loraPHY.modem import LoraModem
from radiosim2.networkDevice.deviceTimer import DeviceTimer


class LoraDevice:
    def __init__(self):
        self.name = ""
        self.position = (0, 0)
        self.modems: list[LoraModem] = []
        self.timers: dict[str, DeviceTimer] = {}
        self.routing_strategy = None

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

    def packet_received(self):
        pass

    def send_packet(self, data, modem):
        self.modems[modem].send(data, len(data))
