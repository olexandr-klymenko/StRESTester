from typing import Dict, AnyStr
import asyncio
from urllib.parse import urljoin
import json

from interfaces import BaseStressTestPlayer
from utils import get_swagger, parse_scenario_template
from constants import *

__all__ = ['StressTestGameK01Player']


class StressTestGameK01Player(BaseStressTestPlayer):
    def __init__(self, loop: asyncio.AbstractEventLoop, config: Dict, scenario_path: AnyStr):
        self.loop = loop
        self._config = config
        self._scenario_path = scenario_path
        self._auth_swagger = None
        self._api_users_swagger = None

    def run_player(self):
        for iteration in range(self._config[ITERATIONS_NUMBER]):
            self.loop.run_until_complete(self.get_tasks())

    def get_tasks(self) -> asyncio.Future:
        self._set_swaggers()
        _tasks = []
        for user_count in range(self._config[USERS_NUMBER]):
            scenario_kwargs = {
                'auth_url': self._config[AUTH],
                'api_url': self._config[API],
                'auth_swagger': self._auth_swagger,
                'api_users_swagger': self._api_users_swagger,
                'username': "%s_%s" % (TEST_USER_NAME, user_count),
                'password': TEST_USER_PASSWORD
            }
            _tasks.append(self.do_play(**scenario_kwargs))
        return asyncio.gather(*_tasks)

    def _set_swaggers(self):
        self._auth_swagger = get_swagger(self._config[AUTH])
        self._api_users_swagger = get_swagger(urljoin(self._config[API], '/users/'))

    async def do_play(self, **kwargs):
        with open(self._scenario_path) as scenario_file:
            await parse_scenario_template(json.load(scenario_file), globals(), kwargs)
