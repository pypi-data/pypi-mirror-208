from __future__ import annotations

from typing import Callable, Any, TypeVar

__all__ = ['Visitor']

T = TypeVar('T')
VisitorState = Any
NodeClass = T


class Visitor:
    """
    Base class of the visitor. Call self.visit(object) to visit the object automatically using
    the object __visitor_method__ attribute to find the method.
    """

    def __init__(self):
        self.methods = {}

    def register(self,
                 name: str,
                 method: Callable[[Visitor, NodeClass, VisitorState], None],
                 allow_overwrite: bool = False
                 ):
        """
        Register the visitor method.
        :param allow_overwrite: allow to overwrite of an already registered function
        :param name: method's name
        :param method: the method
        :raise KeyError: if a method is already registered under the given name
        """
        if name in self.methods and not allow_overwrite:
            raise KeyError(f'A method is already registered for "{name}"')
        self.methods[name] = method

    def unregister(self, name: str):
        """
        Unregister the method if it exists.
        :param name: method's name
        """
        if name in self.methods:
            del self.methods[name]

    def clear(self):
        """
        Unregister all the methods.
        """
        self.methods.clear()

    def visit(self, obj: object, context: Any, ignore_errors: bool = False):
        """
        Detect and call the visit method for the given object. The method is defined in the visited object with the
        class attribute __visitor_method__ set to the name of a visitor's method.
        :param context: the visitor context
        :param obj: the object to visit
        :param ignore_errors: if true, missing visitor methods will be ignored, else, an error will be raised.
        :raise ValueError: if ignore_error is False and __visitor_method__ is missing or concrete visit
        method is missing
        """
        visitor_method = getattr(obj, '__visitor_method__', None)
        if visitor_method is None:
            if ignore_errors:
                return
            raise ValueError(f'Missing __visitor_method__ in {obj.__class__.__name__}')

        if visitor_method not in self.methods:
            raise ValueError(f'Missing concrete visitor method "{visitor_method}" in {self.__class__.__name__}')

        self.methods[visitor_method](self, obj, context)
