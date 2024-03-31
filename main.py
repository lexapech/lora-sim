
from eventSimulator.eventQueue import EventQueue
from eventSimulator.event import DiscreteEvent
from eventSimulator.IEventSubscriber import IEventSubscriber
from radioEnvironment.radioEnvironment import RadioEnvironment
from loraPHY.modem import LoraModem
from loraPHY.enums import LoraBandwidth, LoraSpreadFactor, LoraCodingRate
from loraPHY.loraPacket import LoraPacket
from networkDevice.deviceTimer import DeviceTimer

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




def modem1_cb():
    print(f'[{queue.time*1000} ms][M1] callback')


def modem2_cb(packet: LoraPacket):
    print(f'[{queue.time*1000} ms][M2] callback {packet.data}')


modem1.set_tx_done_callback(modem1_cb)
modem2.set_rx_done_callback(modem2_cb)

modem1.send(bytes("123", 'utf-8'))

timer1 = DeviceTimer(queue, 2.0)


def timer_cb1():
    print(f'[{queue.time*1000} ms][T_OVF] callback')
    timer1.stop()


def timer_cb4():
    print(f'[{queue.time*1000} ms][T_1] callback ')


def timer_cb2():
    print(f'[{queue.time*1000} ms][T_CMP] callback ')
    timer1.start_oneshot(3, timer_cb4)


timer1.set_overflow_callback(timer_cb1)
timer1.set_compare_callback(timer_cb2)
timer1.set_compare(1.0)

timer1.start()




while input() != "q":
    pass
