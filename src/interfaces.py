from abc import ABCMeta, abstractmethod
from typing import Dict

__all__ = ['BaseStressTestConfig', 'BaseActionsRegistry']


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


class BaseActionsRegistry(metaclass=ABCMeta):

    @abstractmethod
    def register_action(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_action(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_actions(self, *args, **kwargs):
        pass
