
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

    def __init__(self):
        super(Logger, self).__init__()
        pass

    def log(self,message,sender=None, level=DebugLevel.INFO):
        self.message.emit(str(message))