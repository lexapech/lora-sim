from networkDevice.networkDevice import LoraDevice
from radioEnvironment.radioEnvironment import RadioEnvironment

from PySide6.QtCore import QObject, Signal
from enum import Enum
import json
from ISerializable import ISerializable
from ISimulation import ISimulation
from position import Position
from loraPHY.modem import LoraModem
from loraPHY.enums import LoraBandwidth,LoraSpreadFactor,LoraCodingRate
from loraPHY.loraPacket import LoraPacket
from networkDevice.deviceTimer import DeviceTimer
import os

class SimulationState(Enum):
    STARTED=1,
    PAUSED=2,
    CREATED=3,
    STEP_FORWARD=4,
    STEP_BACKWARD=5,
    STOPPED=6,


class Simulation(QObject,ISerializable,ISimulation):
    deviceListChanged = Signal(list)
    state_changed = Signal(SimulationState)

    def __init__(self, env,logger):
        super(Simulation, self).__init__()
        self.devices: list[LoraDevice] = []
        self.env = env
        self.logger = logger
        self.state = SimulationState.CREATED
        self.clear()
        self.state_at_start=None

    def get_radio_env(self):
        return self.env 

    def from_json(self,json,attr_types=None):
        super().from_json(json,{
            'devices':LoraDevice,
            'env':RadioEnvironment
            })
        #self.temp_init()
        self.deviceListChanged.emit(self.devices)
                    
            
    def to_json(self,attrs=[]):
        return super().to_json(['devices','env'])

    def add_device(self,device: LoraDevice):
        if device not in self.devices:
            self.devices.append(device)
            self.deviceListChanged.emit(self.devices)
        else:
            raise ValueError("device already added")

    def clear(self):
        self.devices=[]
        self.deviceListChanged.emit(self.devices)
        self.set_state(SimulationState.CREATED)


    def start(self):
        if self.state in [SimulationState.CREATED,SimulationState.STOPPED] :
            self.state_at_start = self.to_json()
            self.env.event_queue.start()
            self.temp_init()
            for dev in self.devices:
                dev.execute_script()

            self.set_state(SimulationState.STARTED)
            self.logger.log("Simulation started")
        elif self.state in [SimulationState.PAUSED]:
            self.env.event_queue.start()
            self.set_state(SimulationState.STARTED)
            self.logger.log("Simulation started")
            


    def stop(self):
        if self.state in [SimulationState.STARTED,SimulationState.PAUSED] :
            self.env.event_queue.stop()
            while self.env.event_queue.locked:
                pass
            self.env.event_queue.clear()
            self.env.clear()
            self.from_json(self.state_at_start)
            #self.temp_init()
            self.set_state(SimulationState.STOPPED)
            self.logger.log("Simulation stopped")

    def pause(self):
        if self.state == SimulationState.STARTED:
            self.env.event_queue.stop()
            while self.env.event_queue.locked:
                pass
            self.set_state(SimulationState.PAUSED)

    def set_state(self,state):
        self.state = state
        self.state_changed.emit(self.state)

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


    def temp_init(self):

        modem1 = self.devices[0].get_modems()[0]
        modem2 = self.devices[1].get_modems()[0]

        def modem1_cb():
            self.logger.log(f'[{self.env.event_queue.time*1000} ms][M1] callback')


        def modem2_cb(packet: LoraPacket):
            self.logger.log(f'[{self.env.event_queue.time*1000} ms][M2] callback {packet.data}')


        modem1.set_tx_done_callback(modem1_cb)
        modem2.set_rx_done_callback(modem2_cb)

        modem1.send(bytes("123", 'utf-8'))

        timer1 = DeviceTimer(self.env.event_queue, 2.0)


        def timer_cb1():
            self.logger.log(f'[{self.env.event_queue.time*1000} ms][T_OVF] callback')
            timer1.stop()


        def timer_cb4():
            #self.logger.log(f'[{self.queue.time*1000} ms][T_1] callback ')
            print(f'[{self.env.event_queue.time*1000} ms][T_1] callback ')
            timer1.start_oneshot(1, timer_cb4)

        def timer_cb2():
            self.logger.log(f'[{self.env.event_queue.time*1000} ms][T_CMP] callback ')
            timer1.start_oneshot(3, timer_cb4)


        timer1.set_overflow_callback(timer_cb1)
        timer1.set_compare_callback(timer_cb2)
        timer1.set_compare(1.0)

        timer1.start()
       