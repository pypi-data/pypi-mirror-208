from dataclasses import dataclass, field
from typing import Any

__all__ = ['SearchableList', 'BaseContext']

SEARCH_LIST_OPERATIONS = {
    '==': lambda a, b: a == b,
    '!=': lambda a, b: a != b,
    '>': lambda a, b: a > b,
    '>=': lambda a, b: a >= b,
    '<': lambda a, b: a < b,
    '<=': lambda a, b: a <= b,
    'in': lambda a, b: a in b,
    'not in': lambda a, b: a not in b
}


class SearchableList:
    """
    A list of object with search features.
    """
    def __init__(self, items: list[dict]):
        self._items = items

    @property
    def all(self) -> list[dict]:
        """
        Returns the actual list
        :return: the list of object
        """
        return self._items

    def select(self, attr: str, operation: str, value: Any) -> list[dict]:
        """
        Select the objects with the attribute that validates the condition.
        :param attr: the attribute's name
        :param operation: the operation to perform
        :param value: the condition's value
        :return: a list of dict
        """
        if operation not in SEARCH_LIST_OPERATIONS:
            raise ValueError(f'Operation must be one of {SEARCH_LIST_OPERATIONS}')

        key = SEARCH_LIST_OPERATIONS[operation]
        return [item for item in self._items if attr in item and key(item.get(attr), value)]

    def select_by_name(self, name: str) -> list[dict]:
        """
        Shortcut for select('name', '==', name)
        :param name: the wanted object name's value
        :return: list of dict
        """
        return self.select('name', '==', name)

    def collect(self, attr: str) -> list[Any]:
        """
        Collect all the objects' attributes in one list.
        :param attr: the attribute to get on each object
        :return: a list of Any
        """
        return [item[attr] for item in self._items if attr in item]


@dataclass
class BaseContext:
    variables: dict = field(default_factory=dict)
    targets: SearchableList = field(default_factory=SearchableList)
