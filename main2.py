
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

from PySide6.QtCore import QThread, Slot
from logger import Logger,DebugLevel

class WorkerThread(QThread):

    def __init__(self):
        super(WorkerThread, self).__init__()
        self.logger = Logger()
        self.simulation = Simulation()

    @Slot()  # QtCore.Slot
    def run(self):

        self.logger.log("Worker thread started")
        
        queue = EventQueue()

        env = RadioEnvironment(queue)

        modem1 = LoraModem(queue, env)

        modem2 = LoraModem(queue, env)

        modem3 = LoraModem(queue, env)

        modem1.modem_settings.spread_factor = LoraSpreadFactor.SF_5
        modem1.modem_settings.power = 0
        modem1.modem_settings.bandwidth = LoraBandwidth.BW_125
        modem1.modem_settings.coding_rate = LoraCodingRate.CR_4_5
        modem1.modem_settings.frequency = 868000000
        modem1.modem_settings.preamble = 12
        modem1.position = (100, 0)


        modem2.modem_settings.spread_factor = LoraSpreadFactor.SF_5
        modem2.modem_settings.power = 22
        modem2.modem_settings.bandwidth = LoraBandwidth.BW_125
        modem2.modem_settings.coding_rate = LoraCodingRate.CR_4_5
        modem2.modem_settings.frequency = 868000000
        modem2.modem_settings.preamble = 12


        device1=LoraDevice()
        device1.name = 'device 1'
        device1.add_modem(modem1)
        

        device2=LoraDevice()
        device2.name = 'device 2'
        device2.add_modem(modem2)
        device2.add_modem(modem3)

        self.simulation.add_device(device1)
        self.simulation.add_device(device2)


        def modem1_cb():
            self.logger.log(f'[{queue.time*1000} ms][M1] callback')


        def modem2_cb(packet: LoraPacket):
            self.logger.log(f'[{queue.time*1000} ms][M2] callback {packet.data}')


        modem1.set_tx_done_callback(modem1_cb)
        modem2.set_rx_done_callback(modem2_cb)

        modem1.send(bytes("123", 'utf-8'))

        timer1 = DeviceTimer(queue, 2.0)


        def timer_cb1():
            self.logger.log(f'[{queue.time*1000} ms][T_OVF] callback')
            timer1.stop()


        def timer_cb4():
            self.logger.log(f'[{queue.time*1000} ms][T_1] callback ')


        def timer_cb2():
            self.logger.log(f'[{queue.time*1000} ms][T_CMP] callback ')
            timer1.start_oneshot(3, timer_cb4)


        timer1.set_overflow_callback(timer_cb1)
        timer1.set_compare_callback(timer_cb2)
        timer1.set_compare(1.0)

        timer1.start()
        i=0
        while True:
            self.logger.log(i)
            i+=1
            self.sleep(1)
