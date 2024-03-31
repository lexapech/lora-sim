from .event import DiscreteEvent
from .IEventQueue import IEventQueue


class IEventSubscriber:
    def notify(self, env: IEventQueue, event: DiscreteEvent):
        raise NotImplementedError
