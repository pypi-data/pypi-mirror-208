import inspect


def get_fathers_class_for_method(method):
    cls = getattr(
        inspect.getmodule(method),
        method.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0],
        None
    )
    if isinstance(cls, type):
        return cls


def is_iterable(obj):
    return hasattr(obj, '__iter__') \
        and hasattr(obj, '__next__') \
        and callable(obj.__iter__)
