import asyncio
import json
from collections import defaultdict
from logging import getLogger
from typing import Dict
from urllib.parse import urljoin
from http.client import responses

from aiohttp.client import ClientSession
from aiohttp.hdrs import METH_GET

from constants import BLUEPRINTS_INFO

__all__ = ['HTTPCodesDescription']

logger = getLogger('asyncio')

SWAGGER_JSON = 'swagger.json'
PATHS = 'paths'
UNKNOWN = '!!! UNKNOWN !!!'


class HTTPCodesDescription:
    """
    Class for figuring out status codes description from swagger json files
    """
    _info = defaultdict(dict)
    _use_swagger = False

    @classmethod
    def init(cls, config: Dict, use_swagger):
        loop = asyncio.get_event_loop()
        if not cls._info and use_swagger:
            loop.run_until_complete(cls._do_init(config))
            logger.info("Swagger info has been generated")

    @classmethod
    async def _do_init(cls, config):
        for swagger_root, swagger_paths in config[BLUEPRINTS_INFO].items():
            for _path in swagger_paths:
                url = urljoin(urljoin(config[swagger_root], _path), SWAGGER_JSON)
                logger.info("Adding swagger from '%s'" % url)
                cls._info[config[swagger_root]][_path] = await _async_get_swagger(url)

    # TODO figure out swagger path from swagger_info
    # TODO Use 3rd party swagger parser
    @classmethod
    def get_description(cls, status, **kwargs) -> str:
        if cls._use_swagger:
            url = kwargs['url']
            path = kwargs['path']
            swagger_path = kwargs['swagger_path']
            method = kwargs['method']
            for blueprint, swagger in cls._info[url].items():
                if path.startswith(blueprint):
                    try:
                        return swagger[PATHS][swagger_path][method.lower()]['responses'][str(status)]['description']
                    except KeyError:
                        logger.warning("Probably unexpected status code %s" % status)
                        return UNKNOWN
            raise Exception("Path '%s' is not part of any blueprint %s of the url '%s'" %
                            (path, cls._info[url], url))
        return responses[status]


async def _async_get_swagger(url) -> Dict:
    async with ClientSession() as session:
        async with session.request(url=url, method=METH_GET) as resp:
            return json.loads(await resp.text())
