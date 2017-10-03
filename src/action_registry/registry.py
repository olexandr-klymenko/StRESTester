from collections import namedtuple
from logging import getLogger
from typing import Tuple, Awaitable

__all__ = ['ActionsRegistry', 'register_action_decorator']

logger = getLogger('asyncio')


class ActionsRegistry:
    """
    Registry contains all available stress test scenario actions
    """
    Action = namedtuple('Action', ['coro', 'args'])
    _registry = {}

    @classmethod
    def register_action(cls, coro: Awaitable, action_name: str, mandatory_args: Tuple):
        cls._registry[action_name] = cls.Action(coro=coro, args=mandatory_args)

    @classmethod
    def get_action(cls, action_name) -> Action:
        if action_name not in cls._registry:
            raise KeyError("Action '%s' is not registered. Valid actions: %s" % (action_name, cls.get_actions()))
        return cls._registry[action_name]

    @classmethod
    def get_actions(cls):
        return list(cls._registry)


def register_action_decorator(action_name: str, mandatory_args=None):
    """
    Decorator with argument "action_name" which registers functions as an stress test scenario action.
    :param action_name:
    :param mandatory_args:
    :return:
    """
    def helper(coro):
        ActionsRegistry.register_action(coro=coro, action_name=action_name, mandatory_args=mandatory_args)
        
        async def wrapper(*args, **kwargs):
            result = await coro(*args, **kwargs)
            return result
        return wrapper
    return helper
