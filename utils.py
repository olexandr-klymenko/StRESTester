import asyncio
import json
import timeit
from logging import getLogger
from typing import Dict
from copy import deepcopy
from xml.etree import ElementTree as ET

from constants import REQUEST_ARGS, SERIALIZABLE_ARGS, REPEAT, CYCLES
from counter import StatsCounter

__all__ = ['parse_scenario_template', 'async_timeit_decorator', 'timeit_decorator', 'get_prepare_request_kwargs',
           'get_parsed_scenario_root']

logger = getLogger('asyncio')


def async_timeit_decorator(coro: asyncio.coroutine) -> asyncio.coroutine:
    async def wrapper(*args, **kwargs):
        start = timeit.default_timer()
        result = await coro(*args, **kwargs)
        action_name = args[0]
        time_metric = timeit.default_timer() - start
        StatsCounter.append_time_metric((action_name, time_metric))
        return result

    return wrapper


def timeit_decorator(func):
    def wrapper(*args, **kwargs):
        start = timeit.default_timer()
        result = func(*args, **kwargs)
        func_name = kwargs.get('name', func.__name__)
        time_metric = timeit.default_timer() - start
        logger.debug("Function '%s' execution time: %s" % (func_name, time_metric))
        return result

    return wrapper


def get_prepare_request_kwargs(kwarg_info: Dict) -> Dict:
    _kwargs = {key: value for key, value in kwarg_info.items() if key in REQUEST_ARGS}
    serializable = {key: json.loads(value) for key, value in _kwargs.items() if key in SERIALIZABLE_ARGS}
    _kwargs.update(serializable)
    return _kwargs


def get_parsed_scenario_root(scenario_path) -> ET.Element:
    with open(scenario_path) as f:
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
