import functools
import math
import operator
from typing import Any, List, Iterable, Union


def do_flatten_list(list_of_list: List[List[Any]])-> List[Any]:
    """Flatten a list of list to a list

    :param list_of_list: list to flatten
    :type list_of_list: List[List[Any]]
    :return: flatten list
    :rtype: List[Any]
    """
    return functools.reduce(operator.iconcat, list_of_list, [])

def map_many(functions: List, iterable:List[Any]) -> List[Any]:
    return list(functools.reduce(lambda x, y: map(y, x), functions, iterable))

def get(items: List[Any], idx: int, default: Any="") -> Any:
    if idx < 0:
        return default
    try:
        return items[idx]
    except IndexError:
        return default
    
def divide_into_chunks(lst: List[Any], num_chunks: int) -> List[List[Any]]:
    num_of_items_in_chunk = math.ceil(len(lst) / num_chunks)
    return [lst[i:i+num_of_items_in_chunk] for i in range(0, len(lst), num_of_items_in_chunk)]

def chunks(iterator: Union[Iterable[Any], List[Any]], chunk_size: int) -> Iterable[List[Any]]:
    """Yield successive n-sized chunks from iterator."""
    chunk = []
    for x in iterator:
        chunk.append(x)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    if len(chunk) > 0:
        yield chunk