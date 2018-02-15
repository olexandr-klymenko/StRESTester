import json
from logging import getLogger

import validators

from constants import *
from interfaces import BaseStressTestConfig

__all__ = ['StressTestConfig']

logger = getLogger(__name__)


DEPRECATED_FIELDS = ['users_number']


class StressTestConfig(BaseStressTestConfig):

    @staticmethod
    def _read_config(config):
        with open(config, 'r') as config_file:
            return json.load(config_file)

    def _validate_config(self):
        if set(DEPRECATED_FIELDS).issubset(set(self._config)):
            logger.warning(
                f"There are at least one deprecated filed in the config:"
                f" {set(self._config) & set(DEPRECATED_FIELDS)}"
            )

        if not set(MANDATORY_CONFIG_FIELDS).issubset(set(self._config)):
            raise Exception("Config file is not complete")

        for url_name, url in self._config[URLS].items():
            if not validators.url(url):
                raise Exception("Invalid url: %s %s" % (url_name, url))
