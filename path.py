from ISerializable import ISerializable

class Path(ISerializable):
    def __init__(self,path):
        self.path = path

    @staticmethod
    def init(device):
        return Path("")

    def __str__(self):
        if len(self.path)>0:
            return self.path
        else:
            return "Путь не задан"

    def from_json(self,json,attr_types=None):
        self.path = json

    def to_json(self,attrs=[]):
        return self.path