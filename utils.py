import asyncio
import json
import timeit
from logging import getLogger
from typing import Dict, List, Union
from urllib.parse import urljoin
from urllib.request import urlopen

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientOSError, ClientResponseError

from constants import SWAGGER_JSON, PATHS, UNKNOWN
from counter import StatsCounter

__all__ = ['get_swagger', 'async_rest_call', 'parse_scenario_template', 'async_sleep']

logger = getLogger('asyncio')


def async_timeit_decorator(coro) -> asyncio.coroutine:
    async def wrapper(*args, **kwargs):
        start = timeit.default_timer()
        # print("%s -->" % start)
        result = await coro(*args, **kwargs)
        # print("--> %s" % timeit.default_timer())
        action_name = kwargs.get('name', coro.__name__)
        time_metric = timeit.default_timer() - start
        StatsCounter.append_time_metric((action_name, time_metric))
        logger.debug("Action '%s' execution time: %s" % (action_name, time_metric))
        return result

    return wrapper


def timeit_decorator(func):
    def wrapper(*args, **kwargs):
        start = timeit.default_timer()
        result = func(*args, **kwargs)
        action_name = kwargs.get('name', func.__name__)
        time_metric = timeit.default_timer() - start
        logger.debug("Action '%s' execution time: %s" % (action_name, time_metric))
        return result
    return wrapper


def get_swagger(url, swagger_json=SWAGGER_JSON) -> Dict:
    with urlopen(urljoin(url, swagger_json)) as response:
        swagger = json.loads(response.read())
        return swagger


# TODO fix time decorator
# TODO investigate global sleep time as Singleton
# TODO add doc strings


async def async_rest_call(**kwargs) -> Union[str, bytes]:
    if kwargs.get('raw'):
        kwargs['data'] = json.dumps(kwargs['data'])
    sleep_time = 1
    while True:
        async with ClientSession() as session:
            _full_url = urljoin(kwargs['url'], kwargs['path'])
            try:
                resp_data = await async_http_request(session, _full_url, **kwargs)
            except (ClientConnectorError, ClientOSError, ClientResponseError) as err:
                logger.warning(str(err))
                StatsCounter.append_error_metric(action_name=kwargs['name'])
                await asyncio.sleep(sleep_time)
                logger.debug("Increasing sleep time: %s" % sleep_time)
                sleep_time += 1
                continue
            else:
                return resp_data


@async_timeit_decorator
async def async_http_request(session: ClientSession, _full_url: str, **kwargs) -> str:
    async with session.request(method=kwargs['method'],
                               url=_full_url,
                               data=kwargs.get('data'),
                               headers=kwargs.get('headers'),
                               params=kwargs.get('params')) as resp:
        resp_data = await resp.text()
        description = _get_swagger_description(kwargs['swagger'], kwargs['swagger_path'], kwargs['method'], resp.status)
        logger.info("'%s' %s %s, status: %s, description: %s\n\tpayload: %s\n\tparams: %s\n\tresponse data: %s" %
                    (kwargs['name'],
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
        return swagger[PATHS][path][method]['responses'][str(status)]['description']
    except KeyError:
        return UNKNOWN


async def parse_scenario_template(template: List, *namespaces):
    ret_info = {}
    global_ns, local_ns = namespaces

    for action in template:
        assert len(action) == 1
        for key, args_info in action.items():
            func = eval(key)
            parsed_kwargs = {}
            try:
                kwargs, ret = args_info
                ret_info[func] = ret
            except ValueError:
                kwargs = args_info

            for arg_name, arg_value in kwargs.items():
                try:
                    parsed_kwargs[arg_name] = eval(arg_value, global_ns, local_ns)
                except NameError:
                    parsed_kwargs[arg_name] = arg_value

        if func in ret_info:
            local_ns[ret_info.pop(func)] = await func(**parsed_kwargs)
        else:
            await func(**parsed_kwargs)


async def async_sleep(sec):
    await asyncio.sleep(sec)


async def get_value(info: Union[str, Dict], key: str):
    try:
        if isinstance(info, dict):
            info = json.dumps(info)
        return json.loads(info)[key]
    except TypeError:
        logger.exception("Unexpected value. Expected dict, info: %s\t key: %s" % (info, key))
        raise
