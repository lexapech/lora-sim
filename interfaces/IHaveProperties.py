

class IHaveProperties:
    def get_properties(self):
        raise NotImplementedError

    def get_minimized(self):
        raise NotImplementedError

    def get_property(self,prop, default):
        raise NotImplementedError
