import asyncio
import json
import timeit
from logging import getLogger
from typing import Dict, Union
from urllib.parse import urljoin
from urllib.request import urlopen
from xml.etree import ElementTree as ET

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientOSError, ClientResponseError

from constants import SWAGGER_JSON, PATHS, UNKNOWN, RETURN
from counter import StatsCounter
from actions_registry import ActionsRegistry, register_action_decorator

__all__ = ['get_swagger', 'async_rest_call', 'parse_scenario_template', 'async_sleep', 'parse_scenario_template',
           'timeit_decorator']

logger = getLogger('asyncio')


def async_timeit_decorator(coro) -> asyncio.coroutine:
    async def wrapper(*args, **kwargs):
        start = timeit.default_timer()
        # print("%s -->" % start)
        result = await coro(*args, **kwargs)
        # print("--> %s" % timeit.default_timer())
        action_name = args[0]
        time_metric = timeit.default_timer() - start
        StatsCounter.append_time_metric((action_name, time_metric))
        logger.debug("Action '%s' execution time: %s" % (action_name, time_metric))
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


def get_swagger(url, swagger_json=SWAGGER_JSON) -> Dict:
    with urlopen(urljoin(url, swagger_json)) as response:
        swagger = json.loads(response.read())
        return swagger

# TODO add doc strings


@register_action_decorator('rest')
async def async_rest_call(name, **kwargs) -> Union[str, bytes]:
    if kwargs.get('raw'):
        kwargs['data'] = json.dumps(kwargs['data'])
    while True:
        async with ClientSession() as session:
            _full_url = urljoin(kwargs['url'], kwargs['path'])
            try:
                resp_data = await async_http_request(name, session, _full_url, **kwargs)
            except (ClientConnectorError, ClientOSError, ClientResponseError) as err:
                logger.warning(str(err))
                StatsCounter.append_error_metric(action_name=name)
                continue
            else:
                return resp_data


@async_timeit_decorator
async def async_http_request(name, session: ClientSession, _full_url: str, **kwargs) -> str:
    async with session.request(method=kwargs['method'],
                               url=_full_url,
                               data=kwargs.get('data'),
                               headers=kwargs.get('headers'),
                               params=kwargs.get('params')) as resp:
        resp_data = await resp.text()
        description = _get_swagger_description(kwargs['swagger'], kwargs['swagger_path'], kwargs['method'], resp.status)
        logger.info("'%s' %s %s, status: %s, description: %s\n\tpayload: %s\n\tparams: %s\n\tresponse data: %s" %
                    (name,
                     _full_url,
                     kwargs['method'].upper(),
                     resp.status,
                     description,
                     kwargs.get('data'),
                     kwargs.get('params'),
                     resp_data))
        if description == UNKNOWN:
            raise ClientResponseError(resp, ())
        return resp_data


def _get_swagger_description(swagger, path, method, status) -> str:
    try:
        return swagger[PATHS][path][method.lower()]['responses'][str(status)]['description']
    except KeyError:
        return UNKNOWN


async def parse_scenario_template(template_root: ET.Element, *namespaces):
    global_ns, local_ns = namespaces

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
                parsed_kwargs[node.tag] = eval(node.text, global_ns, local_ns)
            except (NameError, SyntaxError):
                parsed_kwargs[node.tag] = node.text

        if return_variable:
            local_ns[return_variable] = await coro(*parsed_args, **parsed_kwargs)
        else:
            await coro(*parsed_args, **parsed_kwargs)


@register_action_decorator('sleep')
async def async_sleep(sec):
    await asyncio.sleep(sec)


@register_action_decorator('get')
async def get_value(info: Union[str, Dict], key: str):
    try:
        if isinstance(info, dict):
            info = json.dumps(info)
        return json.loads(info)[key]
    except TypeError:
        logger.exception("Unexpected value. Expected dict, info: %s\t key: %s" % (info, key))
        raise
