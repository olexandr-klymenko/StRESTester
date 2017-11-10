import json
import timeit
from logging import getLogger
from multiprocessing import Queue
from typing import Dict, Coroutine

from constants import REQUEST_ARGS, SERIALIZABLE_ARGS, NAME
from counter import StatsCounter

__all__ = ['async_timeit_decorator', 'timeit_decorator', 'serialize',
           'progress_handler', 'skipped_actions']

logger = getLogger('asyncio')


def async_timeit_decorator(coro: Coroutine) -> Coroutine:
    async def wrapper(*args, **kwargs):
        start = timeit.default_timer()
        result = await coro(*args, **kwargs)
        action_name = args[0]
        time_metric = timeit.default_timer() - start
        logger.debug("Action '%s' execution time: %s"
                     % (action_name, time_metric))
        StatsCounter.append_time_metric((action_name, time_metric))
        return result

    return wrapper


def timeit_decorator(func):
    def wrapper(*args, **kwargs):
        start = timeit.default_timer()
        result = func(*args, **kwargs)
        func_name = kwargs.get(NAME, func.__name__)
        time_metric = timeit.default_timer() - start
        print("Function '%s' execution time: %s" % (func_name, time_metric))
        print("HTTP request rate: %2.2f requests/sec" %
              (kwargs.get('rest_actions', 0) / time_metric))
        return result

    return wrapper


def serialize(kwarg_info: Dict) -> Dict:
    """
    Accept key word arguments and serialize them for HTTP requests
    :param kwarg_info:
    :return:
    """
    _kwargs = {k: v for k, v in kwarg_info.items() if k in REQUEST_ARGS}
    serializable = {k: json.loads(v)
                    for k, v in _kwargs.items() if k in SERIALIZABLE_ARGS}
    _kwargs.update(serializable)
    return _kwargs


def progress_handler(queue: Queue, total_actions: int):
    """
    Gets message from progress queue
     and outputs progress percentage in the loop
    :param queue:
    :param total_actions:
    :return:
    """
    actions_left = total_actions
    while actions_left:
        queue.get()
        actions_left -= 1
        percentage = ' %2.2f%% ' %\
                     ((total_actions - actions_left) * 100 / total_actions)
        print('{:-^80}'.format(percentage))


skipped_actions = set()
