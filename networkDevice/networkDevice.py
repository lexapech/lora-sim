from loraPHY.modem import IModem
from networkDevice.deviceTimer import DeviceTimer
from IHaveProperties import IHaveProperties
from position import Position
from radioEnvironment.radioEnvironment import RadioEnvironment
from networkDevice.INetworkDevice import INetworkDevice
from loraPHY.loraPacket import LoraPacket
from loraPHY.modem import LoraModem
from Property import Property
from ISerializable import ISerializable
from ISimulation import ISimulation
from path import Path
import os
from IRoutingStrategy import IRoutingStrategy
import inspect

class LoraDevice(IHaveProperties, INetworkDevice, ISerializable):
    def __init__(self, radio_env: RadioEnvironment = None):
        self.name = ""
        self.position = Position(0, 0)
        self.modems: list[LoraModem] = []
        self.timers: list[DeviceTimer] = []
        self.routing_strategy = Path("")
        self.radio_env = radio_env
        self.router_class: [IRoutingStrategy,None]=None
        self.event_queue = radio_env.event_queue

    @staticmethod
    def init(simulation:ISimulation):
        return LoraDevice(simulation.get_radio_env())

    def from_json(self,json,attr_types=None):
        self.modems=[]
        self.timers=[]
        return super().from_json(json,{
            'position':Position,
            'modems': LoraModem,
            'timers': DeviceTimer,
            'routing_strategy': Path,
            'name': str
            })

    def to_json(self,attrs=[]):
        return super().to_json(['name','position','modems','timers','routing_strategy'])

    def add_modem(self, modem: LoraModem):
        if modem not in self.modems:
            self.modems.append(modem)
        else:
            raise ValueError("modem already added")

    def add_timer(self, timer: DeviceTimer):
        if timer not in self.timer:
            self.timers.append(timer)
        else:
            raise ValueError("timer already added")

    def get_modems(self):
        return self.modems

    def create_modem(self):
        modem = LoraModem(self)
        #self.add_modem(modem)

    def create_timer(self): 
        timer = DeviceTimer()
        #self.add_timer(timer)
    
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

    def execute_script(self):
        if os.path.isfile(self.routing_strategy.path):
            f = open(self.routing_strategy.path,"r")
            globals={}
            locals={}
            try:
                exec(f.read(),None ,locals)
                f.close()
                strat:[IRoutingStrategy,None] =None
                print(locals)
                for e in locals:
                    if inspect.isclass(locals[e]) \
                        and issubclass(locals[e],IRoutingStrategy)\
                        and locals[e] != IRoutingStrategy:
                        strat = locals[e]
                if strat is None:
                    print("Cannot find routing strat")
                    return
                self.router_class = strat(self)
                self.router_class.start()
            except Exception as ex:
                print(ex)
            #print(strat)


    def get_properties(self):
        return {
            "Имя": Property(self,'name'),
            "Позиция": Property(self,'position'),
            "Модемы": Property(self,'modems',add_func=self.create_modem),
            "Таймеры": Property(self,'timers',add_func=self.create_timer),
            "Алгоритм маршрутизации": Property(self,'routing_strategy',Path)
            }
    def get_minimized(self):
        return ""
