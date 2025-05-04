from collections import OrderedDict
from typing import Dict


def sorted_dict(input_dict: dict[str, int]) -> OrderedDict[str, int]:
    """
    Sorts a dictionary by its integer values in ascending order.

    Args:
        input_dict: Dictionary with string keys and integer values

    Returns:
        OrderedDict: Dictionary sorted by values in ascending order

    Examples:
        >>> sorted_dict({'a': 3, 'b': 1, 'c': 2})
        OrderedDict([('b', 1), ('c', 2), ('a', 3)])
        >>> sorted_dict({})
        OrderedDict()
    """
    if not input_dict:
        return OrderedDict()

    return OrderedDict(sorted(input_dict.items(), key=lambda item: item[1]))
