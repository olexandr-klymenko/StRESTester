__all__ = ['ActionsRegistry', 'register_action_decorator']


class ActionsRegistry:
    _registry = {}

    @classmethod
    def register_action(cls, coro, action_name):
        cls._registry[action_name] = coro

    @classmethod
    def get_action(cls, action_name):
        return cls._registry[action_name]
    
    @classmethod
    def get_actions(cls):
        return list(cls._registry)


def register_action_decorator(action_name):
    def helper(coro):
        ActionsRegistry.register_action(coro=coro, action_name=action_name)
        
        async def wrapper(*args, **kwargs):
            result = await coro(*args, **kwargs)
            return result
        return wrapper
    return helper
