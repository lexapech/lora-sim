import json
from enum import Enum
class ISerializable:
    def to_json(self,attrs=[]):  
        result={}
        for key in  attrs:
            val = self.__dict__[key]
            if isinstance(val, ISerializable):
                result[key] = val.to_json()
            elif isinstance(val, list):
                result[key] =[]
                for x in val:
                    if isinstance(x, ISerializable):
                        result[key].append(x.to_json())
                    else:
                        result[key].append(str(x))
                
            else:
                result[key] = str(val)
        return result

    def from_json(self,json,attr_types=None):
        if attr_types is None:
            raise AttributeError
        for k,v in json.items():
            if isinstance(v,list):
                l = []
                setattr(self,k,l)
                t = attr_types[k]
                for i in v:
                    if issubclass(t,ISerializable):
                        a = t.init(self)
                        a.from_json(i)
                        a.late_init()
                    elif issubclass(t,Enum):
                        a = next(x for x in list(t) if x.name == i) 
                    else:
                        a = t(i)
                    if a not in l:
                        l.append(a)
            else:
                t = attr_types[k]
                if issubclass(t,ISerializable):
                    a = t.init(self)                   
                    a.from_json(v)
                    a.late_init()
                elif issubclass(t,Enum):
                    a = next(x for x in list(t) if x.name == v)                  
                else:
                    a = t(v)
                setattr(self, k, a)
    
    def late_init(self):
        pass

    @staticmethod
    def init(arg):
        raise NotImplementedError


class SerializableDict(dict,ISerializable):
    def to_json(self,attrs=[]):
        result={}
        for key in  self.keys():
            val = self[key]
            if isinstance(val, ISerializable):
                result[key] = val.to_json()
            elif isinstance(val, list):
                result[key] =[]
                for x in val:
                    if isinstance(x, ISerializable):
                        result[key].append(x.to_json())
                    else:
                        result[key].append(str(x))
                
            else:
                result[key] = str(val)
        return result
