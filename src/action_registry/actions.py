import asyncio
import json
import sys
from concurrent.futures._base import TimeoutError
from logging import getLogger
from typing import Dict, Union
import traceback
from pprint import pprint

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientOSError,\
    ClientResponseError

from action_registry.registry import register_action_decorator
from codes_description import HTTPCodesDescription
from constants import MAX_RETRY, RETRY_DELAY, DEFAULT_REST_REQUEST_TIMEOUT,\
    IGNORE_ERRORS
from counter import StatsCounter
from utils import async_timeit_decorator, serialize

logger = getLogger('asyncio')

__all__ = ['async_rest_call', 'get_value', 'async_sleep']


@register_action_decorator(action_name='rest',
                           mandatory_args=('url', 'method'))
async def async_rest_call(name, **kwargs) -> Union[str, bytes]:
    """
    The main action which performs HTTP REST requests to target resource
    :param name:
    :param kwargs:
    :return:
    """
    if kwargs.get('raw'):
        kwargs['data'] = json.dumps(kwargs['data'])
    attempts_left = MAX_RETRY
    while attempts_left:
        async with ClientSession() as session:
            try:
                resp_data = await async_http_request(name, session, **kwargs)
            except (ClientConnectorError,
                    ClientOSError,
                    ClientResponseError,
                    TimeoutError
                    ) as err:
                logger.warning(str(err))
                traceback.print_exc(file=sys.stdout)
                StatsCounter.append_error_metric(action_name=name)
                if kwargs[IGNORE_ERRORS]:
                    return

                attempts_left -= 1
                await asyncio.sleep(RETRY_DELAY)
                continue
            else:
                return resp_data

    pprint("name: %s\nkwargs: %s" % (name, kwargs), indent=4)
    raise Exception("Max number of retries exceeded")


@async_timeit_decorator
async def async_http_request(name, session: ClientSession, **kwargs) -> str:
    """
    Invokes aiohttp client session request
    :param name:
    :param session:
    :param kwargs:
    :return:
    """
    _kwargs = serialize(kwargs)
    async with session.request(
            timeout=DEFAULT_REST_REQUEST_TIMEOUT,
            **_kwargs) as resp:
        resp_data = await resp.text()
        description = HTTPCodesDescription.get_description(resp.status,
                                                           **kwargs)
        logger.debug("'%s' '%s' %s %s, status: %s, description: %s"
                     "\n\tpayload: %s\n\trequest headers: %s\n\tparams: %s"
                     "\n\tresponse data: %s\n\tresponse headers: %s" %
                     (kwargs['username'],
                      name,
                      kwargs['url'],
                      kwargs['method'].upper(),
                      resp.status,
                      description,
                      kwargs.get('data'),
                      kwargs.get('headers'),
                      kwargs.get('params'),
                      resp_data,
                      dict(resp.headers)))
        #  TODO: replace dirty hack
        if resp.status not in list(range(200, 209)):
            raise ClientResponseError(request_info=kwargs,
                                      history='',
                                      code=resp.status)
        return resp_data


@register_action_decorator(action_name='sleep')
async def async_sleep(sec):
    await asyncio.sleep(sec)


@register_action_decorator(action_name='get')
async def get_value(info: Union[str, Dict], key: str, **kwargs):
    """
    Auxiliary action for processing responses like dictionary
    :param info:
    :param key:
    :param kwargs:
    :return:
    """
    info = str(info).replace("'", "\"")
    try:
        return json.loads(info)[key]
    except (TypeError, json.decoder.JSONDecodeError):
        sys.stdout.write(kwargs['xml'].decode())
        raise ValueError('Unexpected HTTP response'
                         ' or incorrect dictionary name in scenario')
