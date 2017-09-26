import asyncio
from typing import Dict, AnyStr
from urllib.parse import urljoin
from xml.etree import ElementTree as ET

from constants import *
from interfaces import BaseStressTestPlayer
import utils

__all__ = ['StressTestGameK01Player']


class StressTestGameK01Player(BaseStressTestPlayer):
    def __init__(self, loop: asyncio.AbstractEventLoop, config: Dict, scenario: AnyStr):
        self.loop = loop
        self._config = config
        self._scenario = scenario
        self._auth_swagger = None
        self._api_users_swagger = None
        self._api_admin_swagger = None

    @utils.timeit_decorator
    def run_player(self):
        self._set_swaggers()
        for iteration in range(self._config[ITERATIONS_NUMBER]):
            for user_count in range(self._config[USERS_NUMBER]):
                scenario_kwargs = {
                    'auth_url': self._config[AUTH],
                    'api_url': self._config[API],
                    'auth_swagger': self._auth_swagger,
                    'api_users_swagger': self._api_users_swagger,
                    'api_admin_swagger': self._api_admin_swagger,
                    'username': "%s_%s" % (TEST_USER_NAME, user_count),
                    'password': TEST_USER_PASSWORD
                }
                self.loop.run_until_complete(self.do_play(**scenario_kwargs))

# TODO Generalize adding swaggers
# TODO Use 3rd party swagger parser

    def _set_swaggers(self):
        self._auth_swagger = utils.get_swagger(self._config[AUTH])
        self._api_users_swagger = utils.get_swagger(urljoin(self._config[API], '/users/'))
        self._api_admin_swagger = utils.get_swagger(urljoin(self._config[API], '/admin/'))

    async def do_play(self, **kwargs):
        with open(self._scenario) as scenario_file:
            xml_root = ET.parse(scenario_file).getroot()
            await utils.parse_scenario_template(xml_root, globals(), kwargs)
