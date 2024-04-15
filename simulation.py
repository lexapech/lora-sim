from networkDevice.networkDevice import LoraDevice

from PySide6.QtCore import QObject, Signal

class Simulation(QObject):
    deviceListChanged = Signal(list)

    def __init__(self, env):
        super(Simulation, self).__init__()
        self.devices: list[LoraDevice] = []
        self.env = env

    def add_device(self,device: LoraDevice):
        if device not in self.devices:
            self.devices.append(device)
            self.deviceListChanged.emit(self.devices)
        else:
            raise ValueError("device already added")

    def update_device_list(self):
        self.deviceListChanged.emit(self.devices)

    def create_empty_device(self):

        device = LoraDevice(self.env)
        device.name ="New Lora Device"
        self.devices.append(device)
        self.deviceListChanged.emit(self.devices)

    def delete_device(self,device: LoraDevice):
        if device in self.devices:
            self.devices.remove(device)
            self.deviceListChanged.emit(self.devices)
        else:
            raise ValueError("device not found")
       