
from PySide6.QtCore import QObject, Signal

from enum import Enum
import datetime

class DebugLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 4
    ERROR = 8
    

class Logger(QObject):
    message = Signal(str)

    def __init__(self,queue):
        super(Logger, self).__init__()
        self.queue = queue

    def log(self,message,sender=None, level=DebugLevel.INFO):
        if sender is not None:
            self.message.emit(f"<p>[{self.queue.time*1000:.2f} ms][{str(sender)}] {str(message)}</p>")
        else:
            self.message.emit(f"[{self.queue.time*1000:.2f} ms] {str(message)}")