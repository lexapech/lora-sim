from eventSimulator.IEventQueue import IEventQueue
from eventSimulator.event import DiscreteEvent
from eventSimulator.IEventSubscriber import IEventSubscriber
from typing import Callable
import copy


class DeviceTimer(IEventSubscriber):
    def __init__(self, event_queue: IEventQueue, period, overflow_handler=None, compare_handler=None):
        self.overflow_handler = overflow_handler
        self.compare_handler = compare_handler
        self.event_queue = event_queue
        self.period = period
        self.compare = 0
        self.started = False
        self.next_overflow: DiscreteEvent or None = None
        self.next_compare: DiscreteEvent or None = None

        self.event_queue.subscribe(self, self)
        self.oneshot_handler = None

    def set_overflow_callback(self, cb: Callable):
        self.overflow_handler = cb

    def set_compare_callback(self, cb: Callable):
        self.compare_handler = cb

    def start(self):
        self.started = True
        e = DiscreteEvent()
        e.tags = [self]
        e.data = ("OVERFLOW", e)
        e.sender = self
        self.next_overflow = self.event_queue.schedule_event_after(e, self.period)
        e.data = ("COMPARE", e)
        self.next_compare = self.event_queue.schedule_event_after(e, self.compare)

    def stop(self):
        self.next_compare = None
        self.next_overflow = None
        self.started = False

    def start_oneshot(self, delay, handler: Callable, args=None):
        e = DiscreteEvent()
        e.tags = [self]
        e.data = ("ONESHOT", args)
        e.sender = self
        self.oneshot_handler = handler
        self.event_queue.schedule_event_after(e, delay)

    def set_compare(self, s_from_reload):
        self.compare = s_from_reload
        if isinstance(self.next_overflow, DiscreteEvent):
            e = DiscreteEvent()
            e.tags = [self]
            e.sender = self
            e.data = ("COMPARE", e)
            e.triggerTime = self.next_overflow.creationTime + self.compare
            self.event_queue.schedule_event(e)
            self.next_compare = e

    def set_cnt(self, s_from_reload):
        if isinstance(self.next_overflow, DiscreteEvent):
            e = DiscreteEvent()
            e.tags = [self]
            e.sender = self
            e.data = ("OVERFLOW", e)
            self.next_overflow = self.event_queue.schedule_event_after(e, self.period - s_from_reload)
            e.data = ("COMPARE", e)
            e.triggerTime = self.next_overflow.creationTime + self.compare
            self.event_queue.schedule_event(e)
            self.next_compare = e

    def notify(self, env: IEventQueue, event: DiscreteEvent):
        if isinstance(event.data, tuple):
            if event.data[0] == "ONESHOT":
                if self.oneshot_handler is not None:
                    if event.data[1] is not None:
                        self.oneshot_handler(*event.data[1])
                    else:
                        self.oneshot_handler()
            elif event.data[0] == "OVERFLOW":
                if event == self.next_overflow:
                    if self.overflow_handler is not None:
                        self.overflow_handler()
                    if self.started:
                        e = DiscreteEvent()
                        e.tags = [self]
                        e.data = ("OVERFLOW", e)
                        e.sender = self
                        self.next_overflow = self.event_queue.schedule_event_after(e, self.period)
                        e.data = ("COMPARE", e)
                        self.next_compare = self.event_queue.schedule_event_after(e, self.compare)
            elif event.data[0] == "COMPARE":
                if event == self.next_compare:
                    if self.compare_handler is not None:
                        self.compare_handler()
            else:
                raise ValueError("Unknown event")
        else:
            raise ValueError("Unknown event")
