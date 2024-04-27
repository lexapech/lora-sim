from loraPHY.modem import IModem
from networkDevice.deviceTimer import DeviceTimer
from interfaces.IHaveProperties import IHaveProperties
from util.position import Position
from radioEnvironment.radioEnvironment import RadioEnvironment
from networkDevice.INetworkDevice import INetworkDevice
from loraPHY.loraPacket import LoraPacket
from loraPHY.modem import LoraModem
from util.Property import Property
from interfaces.ISerializable import ISerializable,SerializableDict
from interfaces.ISimulation import ISimulation
from util.path import Path
import os
from interfaces.IRoutingStrategy import IRoutingStrategy
import inspect
import importlib
class LoraDevice(IHaveProperties, INetworkDevice, ISerializable):
    def __init__(self, radio_env: RadioEnvironment = None,logger=None):
        self.name = ""
        self.logger = logger
        self.custom_props=SerializableDict()
        self.position = Position(0, 0)
        self.modems: list[LoraModem] = []
        self.timers: list[DeviceTimer] = []
        self.routing_strategy = Path("")
        self.radio_env = radio_env
        self.router_class: [IRoutingStrategy,None]=None
        self.event_queue = radio_env.event_queue

    @staticmethod
    def init(simulation:ISimulation):
        dev = LoraDevice(simulation.get_radio_env(),simulation.get_logger())
        return dev

    def late_init(self):
        self.set_routing(self.routing_strategy)

    def from_json(self,json,attr_types=None):
        self.modems=[]
        self.timers=[]
        #self.custom_props = json[]
        if 'custom_props' in json:
            self.custom_props = SerializableDict(json.pop('custom_props'))
             

        #print(self.custom_props)
        return super().from_json(json,{
            'position':Position,
            'modems': LoraModem,
            'timers': DeviceTimer,
            'routing_strategy': Path,
            'name': str
            })

    def add_property(self,name,property:Property):
        self.custom_props[name] = property

    def to_json(self,attrs=[]):
        return super().to_json(['name','position','modems','timers','routing_strategy','custom_props'])

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
        self.set_routing(self.routing_strategy)
        if self.router_class is not None:
            try:
                self.router_class.start()
            except Exception as ex:
                self.logger.log(repr(ex),self)


    def get_logger(self):
        return self.logger

    def set_routing(self,path):
        self.routing_strategy = path
        if os.path.isfile(self.routing_strategy.path):
            #f = open(self.routing_strategy.path,"r")
            #globals={}
            #locals={}
            try:
                spec=importlib.util.spec_from_file_location("router",self.routing_strategy.path)
 
                # creates a new module based on spec
                foo = importlib.util.module_from_spec(spec)
                
                # executes the module in its own namespace
                # when a module is imported or reloaded.
                spec.loader.exec_module(foo)
               # print()

                #exec(f.read(),None ,locals)
                #f.close()
                strat:[IRoutingStrategy,None] =None
                #self.router_context = locals
                for _, e in inspect.getmembers(foo):
                    if inspect.isclass(e) \
                        and issubclass(e,IRoutingStrategy)\
                        and e != IRoutingStrategy:
                        strat = e
                if strat is None:
                    print("Cannot find routing strat")
                    return
                self.router_class = strat(self)
                #self.router_class.start()
            except Exception as ex:
                self.logger.log(repr(ex),self)
                #print(ex)
            #print(strat)

    def get_property(self,prop, default):
        props = self.get_properties()
        if prop in props:
            if isinstance(props[prop],Property):              
                return props[prop].get()
            else:
                return type(default)(props[prop])
        else:
            return default

    def __str__(self):
        return f"Device \"{self.name}\""

    def get_properties(self):
        return {
            "Имя": Property(self,'name'),
            "Позиция": Property(self,'position'),
            "Модемы": Property(self,'modems',add_func=self.create_modem),
            "Таймеры": Property(self,'timers',add_func=self.create_timer),
            "Алгоритм маршрутизации": Property(self,'routing_strategy',Path,setter = self.set_routing)
            } | self.custom_props
    def get_minimized(self):
        return ""
