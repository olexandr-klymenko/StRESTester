from logging import getLogger
from urllib.parse import urljoin
import json
from typing import Dict
import asyncio
from collections import defaultdict

from aiohttp.client import ClientSession
from aiohttp.hdrs import METH_GET

from constants import BLUEPRINTS_INFO, SWAGGER_JSON


__all__ = ['Swagger']


logger = getLogger('asyncio')


class Swagger:
    info = defaultdict(dict)

    @classmethod
    def parse(cls, loop: asyncio.AbstractEventLoop, config: Dict):
        if not cls.info:
            loop.run_until_complete(cls._do_parse(config))
            logger.info("Swagger info has been generated")

    @classmethod
    async def _do_parse(cls, config):
        for swagger_root, swagger_paths in config[BLUEPRINTS_INFO].items():
            for _path in swagger_paths:
                url = urljoin(urljoin(config[swagger_root], _path), SWAGGER_JSON)
                cls.info[config[swagger_root]][_path] = await _async_get_swagger(url)


async def _async_get_swagger(url) -> Dict:
    async with ClientSession() as session:
        async with session.request(url=url, method=METH_GET) as resp:
            return json.loads(await resp.text())
