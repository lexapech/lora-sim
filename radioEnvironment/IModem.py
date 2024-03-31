
class IModem:
    def get_position(self) -> tuple[float, float]:
        raise NotImplementedError

    def transmission_start_notify(self, transmission):
        raise NotImplementedError

    def transmission_end_notify(self, transmission):
        raise NotImplementedError
