import asyncio
from typing import Dict, AnyStr

from constants import *
from interfaces import BaseStressTestPlayer
import utils
from scenario_parser import get_parsed_scenario_root

__all__ = ['StressTestGameK01Player']


class StressTestGameK01Player(BaseStressTestPlayer):
    def __init__(self, loop: asyncio.AbstractEventLoop, config: Dict, scenario: AnyStr):
        self.loop = loop
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
                self.loop.run_until_complete(coro)

# TODO Use 3rd party swagger parser
# TODO add XML validation according to swagger_info
# TODO figure out swagger path from swagger_info
