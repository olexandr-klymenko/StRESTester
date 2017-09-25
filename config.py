import json
from logging import getLogger

import validators

from constants import *
from interfaces import BaseStressTestConfig

__all__ = ['StressTestConfig']

logger = getLogger(__name__)


class StressTestConfig(BaseStressTestConfig):
    def __init__(self, config):
        super().__init__(config)
        self._validate_config()

    @staticmethod
    def _read_config(config):
        with open(config, 'r') as config_file:
            return json.load(config_file)

    def _validate_config(self):
        assert set(self._config) == set(CONFIG_FIELDS), "Config file is not complete"

        assert validators.url(self._config[API]), "Invalid API URL"

        assert validators.url(self._config[AUTH]), "Invalid auth URL"
