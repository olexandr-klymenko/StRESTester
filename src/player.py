import asyncio
import re
from multiprocessing import Queue
from typing import Dict, Iterable
from xml.etree import ElementTree as ET

from jinja2 import Template

from action_registry.registry import ActionsRegistry
from constants import *
from interfaces import BaseActionsRegistry

__all__ = ['StressTestPlayer']

USER_ID_RE = re.compile("\d+")


class StressTestPlayer:
    def __init__(self,
                 config: Dict,
                 scenario: Iterable[ET.Element],
                 test_user: str,
                 progress_queue: Queue,
                 act_registry: BaseActionsRegistry = ActionsRegistry):

        self._config = config
        self._scenario = scenario
        self._test_user = test_user
        self._progress_queue = progress_queue
        self._action_registry = act_registry

    def run_player(self):
        """
        Creates loop within given process worker,
         iterates over ITERATION NUMBER,
         user names and runs action coroutines

        :return:
        """
        loop = asyncio.get_event_loop()
        for iteration in range(self._config[ITERATIONS_NUMBER]):
            scenario_kwargs = {
                'uid': self._get_user_id(self._test_user),
                'username': self._test_user,
                'password': TEST_USER_PASSWORD
            }
            scenario_kwargs.update(self._config[URLS])
            scenario_kwargs.update(self._config)
            loop.run_until_complete(
                self._parse_scenario_template(scenario_kwargs))

    @staticmethod
    def _get_user_id(username):
        return re.search(USER_ID_RE, username).group(0)

    async def _parse_scenario_template(self, scenario_kwargs: Dict):
        """
        Parser which converts parsed scenario actions into asyncio coroutines
         and awaits them.
        After awaiting coro puts message (0) to progress queue

        :param scenario_kwargs:
        :return:
        """
        for idx, child in enumerate(self._scenario):
            parsed_args = []
            parsed_kwargs = {'xml': ET.tostring(child)}
            action_name = child.tag
            coro = self._action_registry.get_action(action_name).coro
            if action_name == 'rest':
                parsed_args.append(child.attrib[NAME])
                parsed_kwargs.update(
                    {IGNORE_ERRORS: child.attrib.get(IGNORE_ERRORS, False)})

            return_variable = child.attrib.get(RETURN)

            for node in child:
                try:
                    parsed_kwargs[node.tag] = \
                        Template(node.text).render(**scenario_kwargs)

                except (NameError, SyntaxError):
                    parsed_kwargs[node.tag] = node.text

            parsed_kwargs['username'] = scenario_kwargs['username']

            if return_variable:
                scenario_kwargs[return_variable] = await coro(*parsed_args,
                                                              **parsed_kwargs)
            else:
                await coro(*parsed_args, **parsed_kwargs)
            self._progress_queue.put(0)

# TODO add XML validation according to swagger_info
