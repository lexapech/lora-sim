from IHaveProperties import IHaveProperties
from Property import Property
class Position(IHaveProperties):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
    def __str__(self):
        return f"({self.x}, {self.y})"

    def get_properties(self):
        return {
            "x": Property(self,'x',float),
            "y": Property(self,'y',float)
            }
    def get_minimized(self):
        return str(self)