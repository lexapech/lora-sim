from networkDevice.INetworkDevice import INetworkDevice

class IRoutingStrategy:
    def __init__(self,device: INetworkDevice):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError