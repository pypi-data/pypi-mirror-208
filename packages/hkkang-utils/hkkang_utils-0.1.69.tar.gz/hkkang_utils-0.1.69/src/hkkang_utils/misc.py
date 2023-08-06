from typing import Dict, List, Any, Callable, Iterable


def infinite_iterator(iterator: Iterable) -> Any:
    """Infinite iterator

    :param iterator: iterator
    :type iterator: iterator
    :yield: item from iterator
    :rtype: Any
    """
    while True:
        for item in iterator:
            yield item


def property_with_cache(func: Callable) -> Callable:
    """Property decorator to cache the result of a property. The result is cached in the attribute of name "_{func.__name__}".

    :param func: function to decorate
    :type func: function
    :return: decorated function
    :rtype: function
    """
    @property
    def decorated_func(*args, **kwargs):
        raise RuntimeError("Deprecated. use functools.cached_property instead.")
    return decorated_func

def to_dict(input_object, exclude_prefixes: List[str]=["_", "__"]) -> Dict[str, Any]:
    """Transform object to dictionary. Note that all the attributes that starts with "__" or callable are excluded.

    :return: Dictionary that contains all the attributes of the object
    :rtype: Dict
    """
    return {
        key: getattr(input_object, key)
        for key in dir(input_object)
        if all([not key.startswith(prefix) for prefix in exclude_prefixes]) and not callable(getattr(input_object, key))
    }
