import queue
import copy
from .event import DiscreteEvent
from threading import Thread
from .IEventSubscriber import IEventSubscriber
from .IEventQueue import IEventQueue


class EventQueue(IEventQueue):
    def __init__(self):
        self.mainQueue: queue.PriorityQueue[DiscreteEvent] = queue.PriorityQueue()
        self.workerThread = Thread(target=self.worker, daemon=True)
        self.time = 0
        self.workerThread.start()
        self.subscribers: dict[str, list[IEventSubscriber]] = {}

    def schedule_event_after(self, event: DiscreteEvent, interval: float):
        e = copy.copy(event)
        e.triggerTime = self.time + interval
        self.schedule_event(e)
        return e

    def schedule_event(self, event: DiscreteEvent):
        event.creationTime = self.time
        if event.triggerTime < event.creationTime:
            raise Exception("Cannot schedule past event")
        self.mainQueue.put(event)

    def subscribe(self, listener, tag):
        tagsubs = self.subscribers.get(tag)
        if tagsubs is None:
            tagsubs = [listener]
            self.subscribers[tag] = tagsubs
        else:
            self.subscribers[tag].append(listener)

    def unsubscribe(self, listener, tag):
        tagsubs = self.subscribers.get(tag)
        if tagsubs is not None and listener in tagsubs:
            tagsubs.remove(listener)

    def get_time(self):
        return self.time

    def worker(self):
        while True:
            event = self.mainQueue.get()
            self.time = event.triggerTime
            notify_list = set()

            for tag in event.tags:
                for subscriber in self.subscribers[tag]:
                    notify_list.add(subscriber)
            for subscriber in notify_list:
                subscriber.notify(self, event)
