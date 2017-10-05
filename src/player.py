import asyncio
from multiprocessing import Queue
from typing import Dict, List
from xml.etree import ElementTree as ET

from jinja2 import Template

from action_registry.registry import ActionsRegistry
from interfaces import BaseActionsRegistry
from constants import *
from utils import timeit_decorator

__all__ = ['StressTestPlayer']


class StressTestPlayer:
    def __init__(self,
                 config: Dict,
                 scenario_xml_root: ET.Element,
                 test_users: List,
                 progress_queue: Queue,
                 act_registry: BaseActionsRegistry=ActionsRegistry):

        self._config = config
        self._scenario_xml_root = scenario_xml_root
        self._test_users = test_users
        self._progress_queue = progress_queue
        self._action_registry = act_registry

    @timeit_decorator
    def run_player(self):
        """
        Creates loop within given process worker, iterates over ITERATION NUMBER,
         user names and runs action coroutines
        :return:
        """
        loop = asyncio.get_event_loop()
        for iteration in range(self._config[ITERATIONS_NUMBER]):
            for user_name in self._test_users:
                scenario_kwargs = {
                    'username': user_name,
                    'password': TEST_USER_PASSWORD
                }
                scenario_kwargs.update(self._config[URLS])
                scenario_kwargs.update(self._config)
                loop.run_until_complete(self._parse_scenario_template(scenario_kwargs))

    async def _parse_scenario_template(self, scenario_kwargs: Dict):
        """
        Parser which converts parsed scenario actions into asyncio coroutines
         and awaits them.
        After awaiting coro puts message (0) to progress queue

        :param scenario_kwargs:
        :return:
        """
        for idx, child in enumerate(self._scenario_xml_root):
            parsed_args = []
            parsed_kwargs = {'xml': ET.tostring(child)}
            action_name = child.tag
            coro = self._action_registry.get_action(action_name).coro
            if action_name == 'rest':
                parsed_args.append(child.attrib['name'])

            return_variable = child.attrib.get(RETURN)

            for node in child:
                try:
                    parsed_kwargs[node.tag] =\
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
