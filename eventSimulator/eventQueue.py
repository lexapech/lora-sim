import queue
import heapq
import copy
from .event import DiscreteEvent
from threading import Thread,Condition
from .IEventSubscriber import IEventSubscriber
from .IEventQueue import IEventQueue
import time

class EventQueue(IEventQueue):
    def __init__(self):
        self.mainQueue: queue.PriorityQueue[DiscreteEvent] = queue.PriorityQueue()
        self._queue: list[DiscreteEvent]=[]
        self.time = 0
        self.started = False
        self.queue_empty = Condition()       
        self.locked =False
        self.timeMult = 10.0
        self.subscribers: dict[str, list[IEventSubscriber]] = {}

    def clear(self):
        if self.locked:
            self.stop()
        while self.locked:
            time.sleep(0.001)
        self.time = 0
        self.mainQueue.queue.clear()

        self.subscribers = {}


    def start(self):
        if not self.started:
            self.started = True
            self.workerThread = Thread(target=self.worker, daemon=False)
            self.workerThread.start()

    def stop(self):
        self.started = False        
        self.queue_empty.acquire()  
        self.queue_empty.notify()
        self.queue_empty.release()  


    def schedule_event_after(self, event: DiscreteEvent, interval: float):
        e = copy.copy(event)
        e.triggerTime = self.time + interval
        self.schedule_event(e)
        return e

    def schedule_event(self, event: DiscreteEvent):
        event.creationTime = self.time
        if event.triggerTime < event.creationTime:
            raise Exception("Cannot schedule past event")
        #self.mainQueue.put(event)
        if len(self._queue) == 0:          
            heapq.heappush(self._queue,event)
            self.queue_empty.acquire()  
            self.queue_empty.notify()
            self.queue_empty.release()  
        else:
            heapq.heappush(self._queue,event)

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
        self.locked=True   

        self.queue_empty.acquire()    
        while self.started:
            if len(self._queue) == 0:
                self.queue_empty.wait()
            if len(self._queue) == 0:
                continue
            event = heapq.heappop(self._queue)

            #print(self.subscribers)
            #try:
                #event = self.mainQueue.get(block=False)
            #except:
                #continue

            if self.timeMult != 0 and (event.triggerTime - self.time)>0:
                time.sleep((event.triggerTime - self.time)/self.timeMult)    
            self.time = event.triggerTime
            notify_list = set()
            for tag in event.tags:
                if tag not in self.subscribers:
                    continue
                for subscriber in self.subscribers[tag]:
                    notify_list.add(subscriber)
            for subscriber in notify_list:
                subscriber.notify(self, event) 
        self.queue_empty.release()   
        self.locked=False
