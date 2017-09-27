import asyncio
from typing import Dict, AnyStr

import utils
from constants import *
from interfaces import BaseStressTestPlayer
from scenario_parser import get_parsed_scenario_root

__all__ = ['StressTestPlayer']


class StressTestPlayer(BaseStressTestPlayer):
    def __init__(self, loop: asyncio.AbstractEventLoop, config: Dict, scenario: AnyStr):
        self._loop = loop
        self._config = config
        self._scenario = scenario

    @utils.timeit_decorator
    def run_player(self):
        scenario_xml_root = get_parsed_scenario_root(self._scenario)
        for iteration in range(self._config[ITERATIONS_NUMBER]):
            for user_count in range(self._config[USERS_NUMBER]):
                scenario_kwargs = {
                    'username': "%s_%s" % (TEST_USER_NAME, user_count),
                    'password': TEST_USER_PASSWORD
                }
                scenario_kwargs.update(self._config)
                coro = utils.parse_scenario_template(scenario_xml_root, scenario_kwargs)
                self._loop.run_until_complete(coro)

# TODO add XML validation according to swagger_info
# TODO add XML validation according to action list