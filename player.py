import asyncio
from copy import deepcopy
from typing import Dict, AnyStr, List
from xml.etree import ElementTree as ET

from jinja2 import Template

from action_registry.registry import ActionsRegistry
from constants import *
from utils import timeit_decorator

__all__ = ['StressTestPlayer']


class StressTestPlayer:
    def __init__(self, config: Dict, scenario_path: AnyStr, test_users: List):
        self._config = config
        self._scenario_path = scenario_path
        self._test_users = test_users
        self._scenario_xml_root = self._get_parsed_scenario_root()

    def _get_parsed_scenario_root(self) -> ET.Element:
        with open(self._scenario_path) as f:
            _root = ET.parse(f).getroot()

        def _parse_root(root: ET.Element, new_root=None) -> ET.Element:
            for child in root:
                if child.tag != REPEAT:
                    if new_root is None:
                        new_root = ET.Element('scenario')
                    new_root.append(child)
                else:
                    for cycle in range(int(child.attrib[CYCLES])):
                        _parse_root(deepcopy(child), new_root)
            return new_root

        return _parse_root(deepcopy(_root))

    @timeit_decorator
    def run_player(self):
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
        template_length = len(self._scenario_xml_root)
        for idx, child in enumerate(self._scenario_xml_root):
            parsed_args = []
            parsed_kwargs = {'xml': ET.tostring(child)}
            action_name = child.tag
            coro = ActionsRegistry.get_action(action_name)
            if action_name == 'rest':
                parsed_args.append(child.attrib['name'])

            return_variable = child.attrib.get(RETURN)

            for node in child:
                try:
                    parsed_kwargs[node.tag] = Template(node.text).render(**scenario_kwargs)
                except (NameError, SyntaxError):
                    parsed_kwargs[node.tag] = node.text

            parsed_kwargs['username'] = scenario_kwargs['username']
            parsed_kwargs['progress'] = "{:10.1f}%".format(idx * 100 / template_length)

            if return_variable:
                scenario_kwargs[return_variable] = await coro(*parsed_args, **parsed_kwargs)
            else:
                await coro(*parsed_args, **parsed_kwargs)

# TODO add XML validation according to swagger_info
# TODO add XML validation according to action list
