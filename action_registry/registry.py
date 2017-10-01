from logging import getLogger

__all__ = ['ActionsRegistry', 'register_action_decorator']

logger = getLogger('asyncio')


class ActionsRegistry:
    """
    Registry contains all available stress test scenario actions
    """
    _registry = {}

    @classmethod
    def register_action(cls, coro, action_name):
        cls._registry[action_name] = coro

    @classmethod
    def get_action(cls, action_name):
        if action_name not in cls._registry:
            raise KeyError("Action '%s' is not registered. Valid actions: %s" % (action_name, cls.get_actions()))
        return cls._registry[action_name]

    @classmethod
    def get_actions(cls):
        return list(cls._registry)


def register_action_decorator(action_name):
    """
    Decorator with argument "action_name" which registers functions as an stress test scenario action.
    :param action_name:
    :return:
    """
    def helper(coro):
        ActionsRegistry.register_action(coro=coro, action_name=action_name)
        
        async def wrapper(*args, **kwargs):
            result = await coro(*args, **kwargs)
            return result
        return wrapper
    return helper
