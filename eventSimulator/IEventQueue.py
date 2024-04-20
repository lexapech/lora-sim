from .event import DiscreteEvent


class IEventQueue:
    def schedule_event_after(self, event: DiscreteEvent, interval: float):
        raise NotImplementedError

    def schedule_event(self, event: DiscreteEvent):
        raise NotImplementedError

    def subscribe(self, listener, tag):
        raise NotImplementedError

    def unsubscribe(self, listener, tag):
        raise NotImplementedError

    def get_time(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError
