
class ISimulation:
    def get_radio_env(self):
        raise NotImplementedError

    def get_logger(self):
        raise NotImplementedError