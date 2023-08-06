from src.LoggerService import LoggerService


class LoggerServiceSingleton:

    def __init__(self):
        self._instance = None

    def get_instance(self):
        if self._instance is None:
            self._instance = LoggerService()
        return self._instance


locallgr = LoggerServiceSingleton().get_instance()
