import asyncio
import json
import timeit
from logging import getLogger
from typing import Dict, Union
from urllib.parse import urljoin
from xml.etree import ElementTree as ET

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientOSError, ClientResponseError
from concurrent.futures._base import TimeoutError

from constants import RETURN, MAX_RETRY, RETRY_DELAY
from counter import StatsCounter
from actions_registry import ActionsRegistry, register_action_decorator
from swagger_info import Swagger

__all__ = ['async_rest_call', 'parse_scenario_template', 'async_sleep', 'parse_scenario_template',
           'timeit_decorator']

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


@register_action_decorator('rest')
async def async_rest_call(name, **kwargs) -> Union[str, bytes]:
    if kwargs.get('raw'):
        kwargs['data'] = json.dumps(kwargs['data'])
    attempts_left = MAX_RETRY
    while attempts_left:
        async with ClientSession() as session:
            _full_url = urljoin(kwargs['url'], kwargs['path'])
            try:
                resp_data = await async_http_request(name, session, _full_url, **kwargs)
            except (ClientConnectorError, ClientOSError, ClientResponseError, TimeoutError) as err:
                logger.warning(str(err))
                StatsCounter.append_error_metric(action_name=name)
                attempts_left -= 1
                await asyncio.sleep(RETRY_DELAY)
                continue
            else:
                return resp_data
    raise Exception("Max number of retries exceeded")


@async_timeit_decorator
async def async_http_request(name, session: ClientSession, _full_url: str, **kwargs) -> str:
    async with session.request(method=kwargs['method'],
                               url=_full_url,
                               data=kwargs.get('data'),
                               headers=kwargs.get('headers'),
                               params=kwargs.get('params')) as resp:
        resp_data = await resp.text()
        description = Swagger.get_description(resp.status, **kwargs)
        logger.info("'%s' %s %s, status: %s, description: %s\n\tpayload: %s\n\tparams: %s\n\tresponse data: %s" %
                    (name,
                     _full_url,
                     kwargs['method'].upper(),
                     resp.status,
                     description,
                     kwargs.get('data'),
                     kwargs.get('params'),
                     resp_data))
        return resp_data


async def parse_scenario_template(template_root: ET.Element, scenario_kwargs):

    for child in template_root:
        parsed_args = []
        parsed_kwargs = {}
        action_name = child.tag
        coro = ActionsRegistry.get_action(action_name)
        if action_name == 'rest':
            parsed_args.append(child.attrib['name'])

        return_variable = child.attrib.get(RETURN)

        for node in child:
            try:
                parsed_kwargs[node.tag] = eval(node.text, globals(), scenario_kwargs)
            except (NameError, SyntaxError):
                parsed_kwargs[node.tag] = node.text

        if return_variable:
            scenario_kwargs[return_variable] = await coro(*parsed_args, **parsed_kwargs)
        else:
            await coro(*parsed_args, **parsed_kwargs)


@register_action_decorator('sleep')
async def async_sleep(sec):
    await asyncio.sleep(sec)


@register_action_decorator('get')
async def get_value(info: Union[str, Dict], key: str):
    assert info != "", 'Incorrect dictionary'
    try:
        if isinstance(info, dict):
            info = json.dumps(info)
        return json.loads(info)[key]
    except TypeError:
        logger.error("Unexpected value of 'info'. Expected: dict(), got: %s" % info)
        raise
