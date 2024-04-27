from interfaces.IHaveProperties import IHaveProperties
from util.Property import Property
from interfaces.ISerializable import ISerializable

class Position(IHaveProperties, ISerializable):
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
    
    def to_json(self,attrs=[]):
        return super().to_json(['x','y'])

    @staticmethod
    def init(arg):
        return Position()

    def from_json(self,json,attr_types=None):
        return super().from_json(json,{
            'x':float,
            'y': float,          
            })