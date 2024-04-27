
from eventSimulator.eventQueue import EventQueue
from eventSimulator.event import DiscreteEvent
from eventSimulator.IEventSubscriber import IEventSubscriber
from radioEnvironment.radioEnvironment import RadioEnvironment
from loraPHY.modem import LoraModem
from loraPHY.enums import LoraBandwidth, LoraSpreadFactor, LoraCodingRate
from loraPHY.loraPacket import LoraPacket
from networkDevice.deviceTimer import DeviceTimer
from networkDevice.networkDevice import LoraDevice
from simulation import Simulation
from util.position import Position
import threading
from PySide6.QtCore import QThread, Slot
from util.logger import Logger,DebugLevel
from util.Property import Property

class WorkerThread(QThread):

    def __init__(self):
        super(WorkerThread, self).__init__()
        
        self.queue = EventQueue()
        self.logger = Logger(self.queue)
        self.env = RadioEnvironment(self.queue)
        self.simulation = Simulation(self.env,self.logger)
        self.reset()

    def update_property(self,property: Property):
        property.commit()
        self.simulation.update_device_list()

    def reset(self):
        self.logger.log("Simulation resetted")
        self.queue.clear()
        self.env.clear()
        self.simulation.clear()
       


    def stop(self):
        self.queue.stop()
        self.quit()

    def load_simulation(self,json):
        self.reset()
        self.simulation.from_json(json)

    def init():
        device1 = LoraDevice(self.env)
        device2=LoraDevice(self.env)

        device1.name = 'device 1'
        device1.position = Position(100,0)

        
        device2.name = 'device 2'
        device2.position = Position(100,300)

        modem1 = LoraModem(device1)

        modem2 = LoraModem(device2)

        modem3 = LoraModem(device2)

        modem1.modem_settings.spread_factor = LoraSpreadFactor.SF_5
        modem1.modem_settings.power = 0
        modem1.modem_settings.bandwidth = LoraBandwidth.BW_125
        modem1.modem_settings.coding_rate = LoraCodingRate.CR_4_5
        modem1.modem_settings.frequency = 868000000
        modem1.modem_settings.preamble = 12


        modem2.modem_settings.spread_factor = LoraSpreadFactor.SF_5
        modem2.modem_settings.power = 22
        modem2.modem_settings.bandwidth = LoraBandwidth.BW_125
        modem2.modem_settings.coding_rate = LoraCodingRate.CR_4_5
        modem2.modem_settings.frequency = 868000000
        modem2.modem_settings.preamble = 12

        self.simulation.add_device(device1)
        self.simulation.add_device(device2)
    

    @Slot()  # QtCore.Slot
    def run(self):

        self.logger.log("Worker thread started")

        


        

        while True:

            self.sleep(1)
