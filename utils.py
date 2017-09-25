from logging import getLogger
import asyncio
import time
import json
from typing import Dict, List, ByteString
from urllib.parse import urljoin
from urllib.request import urlopen


from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientOSError, ClientResponseError

from constants import SWAGGER_JSON, PATHS, UNKNOWN

__all__ = ['get_swagger', 'async_rest_call', 'parse_scenario_template', 'async_sleep']


logger = getLogger('asyncio')


def timeit(func):
    async def process(func, *args, **params):
        if 'name' in params:
            print(params['name'])
        if asyncio.iscoroutinefunction(func):
            print('this function is a coroutine: {}'.format(func.__name__))
            return await func(*args, **params)
        else:
            print('this is not a coroutine')
            return func(*args, **params)

    async def helper(*args, **params):
        print('{}.time'.format(func.__name__))
        start = time.time()
        result = await process(func, *args, **params)

        # Test normal function route...
        # result = await process(lambda *a, **p: print(*a, **p), *args, **params)

        print('>>>', time.time() - start)
        return result

    return helper


def get_swagger(url, swagger_json=SWAGGER_JSON) -> Dict:
    with urlopen(urljoin(url, swagger_json)) as response:
        swagger = json.loads(response.read())
        return swagger


# TODO create time decorator to measure execution time
# TODO investigate global sleep time as Singleton
# TODO create decorator for collecting errors
# TODO add doc strings


@timeit
async def async_rest_call(name, method, url, path, swagger, swagger_path,
                          data=None, params=None, headers=None, raw=False) -> ByteString:
    if raw:
        data = json.dumps(data)
    sleep_time = 1
    while True:
        async with ClientSession() as session:
            _full_url = urljoin(url, path)
            try:
                async with getattr(session, method)(_full_url, data=data, headers=headers, params=params) as resp:
                    resp_data = await resp.text()
                    description = _get_swagger_description(swagger, swagger_path, method, resp.status)
                    logger.info("'%s' %s %s, status: %s, description: %s\n\tpayload: %s\n\tresponse data: %s" %
                                (name,
                                 _full_url,
                                 method.upper(),
                                 resp.status,
                                 description,
                                 data,
                                 resp_data))
                    if description == UNKNOWN:
                        raise ClientResponseError(resp, ())
            except (ClientConnectorError, ClientOSError, ClientResponseError) as err:
                logger.warning(str(err))
                await asyncio.sleep(sleep_time)
                logger.debug("Increasing sleep time: %s" % sleep_time)
                sleep_time += 1
                continue
            else:
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


async def get_value(info, key):
    try:
        if isinstance(info, dict):
            info = json.dumps(info)
        return json.loads(info)[key]
    except TypeError:
        logger.exception("Unexpected value. Expected dict, info: %s\t key: %s" % (info, key))
        raise
