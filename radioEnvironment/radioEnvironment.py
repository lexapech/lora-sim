from .transmission import RadioTransmission
from .IModem import IModem
from .transmissionState import RadioTransmissionState
from eventSimulator.IEventQueue import IEventQueue
from eventSimulator.event import DiscreteEvent
from eventSimulator.IEventSubscriber import IEventSubscriber
from .radioHelpers import calculate_signal_attenuation_db


class RadioEnvironment(IEventSubscriber):
    def __init__(self, event_queue: IEventQueue):
        self.noise_floor_db = 0
        self.event_queue = event_queue
        self.modems: list[IModem] = []
        self.transmissions: list[RadioTransmission] = []
        self.event_queue.subscribe(self, (self, "TRANSMISSION"))

    def register_modem(self, modem: IModem):
        if modem not in self.modems:
            self.modems.append(modem)
        else:
            raise ValueError("Modem already registered")

    def unregister_modem(self, modem: IModem):
        self.modems.remove(modem)

    def start_transmission(self, transmission: RadioTransmission, duration: float):
        self.transmissions.append(transmission)
        transmission.flags.append(RadioTransmissionState.STARTED)

        for modem in self.modems:
            if modem is not transmission.transmitter:
                modem.transmission_start_notify(transmission)
        e = DiscreteEvent()
        e.sender = self
        e.tags = [(self, "TRANSMISSION")]
        e.data = transmission
        self.event_queue.schedule_event_after(e, duration)

    def notify(self, env: IEventQueue, event: DiscreteEvent):
        if isinstance(event.data, RadioTransmission):
            transmission: RadioTransmission = event.data
            transmission.flags.append(RadioTransmissionState.FINISHED)
            initial_power = transmission.power
            for modem in self.modems:
                transmission.power = initial_power -\
                    calculate_signal_attenuation_db(transmission.central_frequency,
                                                    transmission.transmitter.get_position(), modem.get_position())
                modem.transmission_end_notify(transmission)
