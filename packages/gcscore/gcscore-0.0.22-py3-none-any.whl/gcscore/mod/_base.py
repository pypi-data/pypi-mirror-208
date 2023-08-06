"""
Base classes and component to build a gcs module.
"""
from __future__ import annotations

import re
from typing import TypeVar, Type

T = TypeVar('T')

__all__ = ['BaseNode', 'add_child', 'HasName', 'HasDescription', 'HasChildren', 'AcceptAnonymousChild', 'AcceptMerge']


class BaseNode:
    """
    All nodes should inherit from this class. On initialization, this class tries to call __gcs_init__ for each
    super class.
    """

    def __init__(self, **kwargs):
        for cls in self.__class__.__mro__:
            if hasattr(cls, '__gcs__init__'):
                cls.__gcs__init__(self, **kwargs)


PATTERN_NAME = re.compile(r'^[a-zA-Z0-9_\-.]+$')


class HasName:
    """
    Provide the node with a name. This is also the base trait to use for all the nodes.
    """
    gcscore_name: str

    def __gcs__init__(self, **kwargs):
        if 'name' not in kwargs:
            raise AttributeError('Missing required argument "name"')
        self.gcscore_name = kwargs['name']


class HasChildren:
    """
    Allow the node to have children. If used, create a __init__ method calling this one HasChildren.__init__(self)
    """
    gcscore_children: list

    def __gcs__init__(self, **_):
        self.gcscore_children = []


class HasDescription:
    gcscore_description: str = ''

    def description(self: T, text: str) -> T:
        """
        Provide the node with a description.
        :param text: text of the description.
        :return: the node
        """
        self.gcscore_description = text
        return self


class AcceptMerge:
    def merge(self: HasChildren, other: HasChildren) -> HasChildren:
        """
        Merges the other's children in its own (the order is kept).
        :param other: other node with children
        :return: self
        """
        self.gcscore_children.extend(other.gcscore_children)
        return self


class AcceptAnonymousChild:
    def child(self: HasChildren, other: HasName) -> HasChildren:
        """
        Adds the other as its own child.
        :param other: any kind of node
        :return: self
        """
        self.gcscore_children.append(other)
        return self


def add_child(parent: HasChildren, klass: Type[T], **kwargs) -> T:
    """
    Create and add a child to the given parent node.
    :param parent: the parent node
    :param klass: the class of the child node
    :return: the child node
    """
    child = klass(**kwargs)
    parent.gcscore_children.append(child)
    return child
