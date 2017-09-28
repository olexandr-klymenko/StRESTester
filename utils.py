import asyncio
import json
import timeit
from logging import getLogger
from typing import Dict
from xml.etree import ElementTree as ET

from jinja2 import Template

from actions_registry import ActionsRegistry
from constants import RETURN, REQUEST_ARGS, SERIALIZABLE_ARGS
from counter import StatsCounter

__all__ = ['parse_scenario_template', 'parse_scenario_template', 'async_timeit_decorator', 'timeit_decorator',
           'get_prepare_request_kwargs', 'get_users']

logger = getLogger('asyncio')


def async_timeit_decorator(coro) -> asyncio.coroutine:
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


async def parse_scenario_template(template_root: ET.Element, scenario_kwargs):
    template_length = len(template_root)
    for idx, child in enumerate(template_root):
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


def get_prepare_request_kwargs(kwarg_info: Dict):
    _kwargs = {key: value for key, value in kwarg_info.items() if key in REQUEST_ARGS}
    serializable = {key: json.loads(value) for key, value in _kwargs.items() if key in SERIALIZABLE_ARGS}
    _kwargs.update(serializable)
    return _kwargs


def get_users(username, users_number, multiplier):
    return ["%s_%s" % (username, idx) for idx in range((multiplier - 1) * users_number, users_number * multiplier)]
