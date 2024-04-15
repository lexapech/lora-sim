class Property:
    def __init__(self,o,attr,_type=None):
        self.obj = o
        self.attr = attr
        self.type = _type
        self.value=getattr(self.obj,self.attr)


    def get(self,load=False):
        if load:
            self.value = getattr(self.obj,self.attr)
            return getattr(self.obj,self.attr)
        return self.value

    def set(self,value,commit=False):
        if self.type is not None and not isinstance(value,self.type):
            value = self.type(value)
        self.value = value
        if commit:      
            setattr(self.obj,self.attr,self.value)

    def commit(self):
        setattr(self.obj,self.attr,self.value)

    def __str__(self):
        return f'Property({self.obj}, {self.attr}, {self.value}, {getattr(self.obj,self.attr)})'