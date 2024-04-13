from networkDevice.networkDevice import LoraDevice

from PySide6.QtCore import QObject, Signal

class Simulation(QObject):
    deviceListChanged = Signal(list)

    def __init__(self):
        super(Simulation, self).__init__()
        self.devices: list[LoraDevice] = []

    def add_device(self,device: LoraDevice):
        if device not in self.devices:
            self.devices.append(device)
            self.deviceListChanged.emit(self.devices)
        else:
            raise ValueError("device already added")

    def create_empty_device(self):

        device = LoraDevice()
        device.name ="New Lora Device"
        print("here")
        self.devices.append(device)
        self.deviceListChanged.emit(self.devices)

    def delete_device(self,device: LoraDevice):
        if device in self.devices:
            self.devices.remove(device)
            self.deviceListChanged.emit(self.devices)
        else:
            raise ValueError("device not found")
       