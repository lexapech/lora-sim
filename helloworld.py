from IRoutingStrategy import IRoutingStrategy
from networkDevice.INetworkDevice import INetworkDevice
from networkDevice.deviceTimer import DeviceTimer
print("hello world")


class MyRouter(IRoutingStrategy):
    def __init__(self,device: INetworkDevice):
        self.device = device
        print(device)
        self.timer = DeviceTimer(self.device.get_event_queue(),1,self.print)
        pass

    def print(self):
        print("abc")    

    def start(self):
        print("hellwlellw")
        self.timer.start()
