import json
from typing import Dict, List, ByteString
from urllib.parse import urljoin
from urllib.request import urlopen
import asyncio

import aiohttp

from constants import SWAGGER_JSON, PATHS

__all__ = ['get_swagger', 'async_rest_call', 'parse_scenario_template']


def get_swagger(url, swagger_json=SWAGGER_JSON) -> Dict:
    with urlopen(urljoin(url, swagger_json)) as response:
        swagger = json.loads(response.read())
        return swagger


async def async_rest_call(method, url, path, swagger, swagger_path,
                          data=None, params=None, headers=None, raw=False) -> ByteString:
    if raw:
        data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        _full_url = urljoin(url, path)
        async with getattr(session, method)(_full_url, data=data, headers=headers, params=params) as resp:
            resp_data = await resp.text()
            print("url: %s, method: %s, status: %s, description: %s, payload: %s, response data: %s" %
                  (_full_url,
                   method,
                   resp.status,
                   _get_swagger_description(swagger, swagger_path, method, resp.status),
                   data,
                   resp_data))
            return resp_data


def _get_swagger_description(swagger, path, method, status) -> ByteString:
    try:
        return swagger[PATHS][path][method]['responses'][str(status)]['description']
    except KeyError:
        return b'Unknown'


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


async def sleep_(sec):
    await asyncio.sleep(sec)


async def get_value(info, key):
    if isinstance(info, dict):
        info = json.dumps(info)
    return json.loads(info)[key]

