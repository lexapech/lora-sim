from networkDevice.deviceTimer import DeviceTimer
from util.Property import Property

class INetworkDevice():
    def add_modem(self):
        raise NotImplementedError

    def send_packet(self, data, modem):
        raise NotImplementedError

    def add_timer(self, timer: DeviceTimer):
        raise NotImplementedError
    
    def packet_received(self, packet):
        raise NotImplementedError

    def get_event_queue(self):
        raise NotImplementedError

    def get_radio_environment(self):
        raise NotImplementedError

    def get_position(self):
        raise NotImplementedError

    def get_modems(self):
        raise NotImplementedError
    
    def get_timers(self):
        raise NotImplementedError

    def get_logger(self):
        raise NotImplementedError

    def add_property(self,property:Property):
        raise NotImplementedError

