import asyncio
import json
from typing import Dict, AnyStr
from urllib.parse import urljoin

from constants import *
from interfaces import BaseStressTestPlayer
from utils import get_swagger, parse_scenario_template, timeit_decorator

__all__ = ['StressTestGameK01Player']


class StressTestGameK01Player(BaseStressTestPlayer):
    def __init__(self, loop: asyncio.AbstractEventLoop, config: Dict, scenario_path: AnyStr):
        self.loop = loop
        self._config = config
        self._scenario_path = scenario_path
        self._auth_swagger = None
        self._api_users_swagger = None
        self._api_admin_swagger = None

    @timeit_decorator
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
    def _set_swaggers(self):
        self._auth_swagger = get_swagger(self._config[AUTH])
        self._api_users_swagger = get_swagger(urljoin(self._config[API], '/users/'))
        self._api_admin_swagger = get_swagger(urljoin(self._config[API], '/admin/'))

    async def do_play(self, **kwargs):
        with open(self._scenario_path) as scenario_file:
            await parse_scenario_template(json.load(scenario_file), globals(), kwargs)
