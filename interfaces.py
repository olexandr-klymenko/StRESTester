from abc import ABCMeta, abstractmethod
from typing import Dict

__all__ = ['BaseStressTestConfig', 'BaseStressTestPlayer', 'MetaSingleton']


class BaseStressTestConfig(dict, metaclass=ABCMeta):
    def __init__(self, config):
        self._config = self._read_config(config)
        self._validate_config()
        super().__init__(self._config)

    def __getitem__(self, item):
        return self._config[item]

    def __repr__(self):
        return "%s: (%s)" % (self.__class__, str(self._config))

    @staticmethod
    @abstractmethod
    def _read_config(config) -> Dict:
        pass

    @abstractmethod
    def _validate_config(self):
        pass


class BaseStressTestPlayer(metaclass=ABCMeta):
    @abstractmethod
    def run_player(self):
        pass


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
