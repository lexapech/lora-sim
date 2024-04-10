from IHaveProperties import IHaveProperties

class Position(IHaveProperties):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
    def __str__(self):
        return f"({self.x}, {self.y})"

    def get_properties(self):
        return {
            "x": self.x,
            "y": self.y
            }
    def get_minimized(self):
        print("here")
        return str(self)