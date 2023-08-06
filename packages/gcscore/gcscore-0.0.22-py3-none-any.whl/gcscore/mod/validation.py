import re
from dataclasses import dataclass, field
from typing import Any

__all__ = ['VisitorStateValidation', 'validation_error', 'validate_string', 'validation_error_value']


@dataclass
class VisitorStateValidation:
    """
    A base for a validation visitor.
    """
    traceback: list[str] = field(default_factory=list)
    only_log_errors: bool = False
    others: dict[str, Any] = field(default_factory=dict)
    errors: list[Exception] = field(default_factory=list)

    def concat(self, *trace: str):
        """
        Creates a new visitor with a new backtrace.
        :param trace: the trace, a list of string
        :return: the new visitor
        """
        return VisitorStateValidation(
            traceback=self.traceback + list(trace),
            only_log_errors=self.only_log_errors,
            others=self.others,
            errors=self.errors
        )

    def formatted_traceback(self) -> str:
        """
        Concatenate the visitor's traceback into a string
        """
        return '.'.join(self.traceback)

    def has_errors(self) -> bool:
        """
        Check if the state contains errors.
        :return: whether the state contains errors or not
        """
        return len(self.errors) > 0


def validation_error(state: VisitorStateValidation, message: str):
    """
    Through a generic validation error. If state.only_log_errors is True, then it will simply print the message.
    :param state: the current visitor state
    :param message: an explicit message about the error and the way to fix it
    :raise ValueError: if state.only_log_errors is False
    """
    if state.only_log_errors:
        print(message)
        state.errors.append(ValueError(message))
    else:
        raise ValueError(message)


VALUE_ERROR_MESSAGE = """
Invalid value for \033[93m{traceback}.\033[1m{attr}\033[0m
    \033[96m{message}\033[0m
    Given value: \033[91m{actual}\033[0m"""


def validation_error_value(state: VisitorStateValidation, attr: str, value: Any, valid_value_message: str):
    """
    Throws a validation error for a value.
    :param state: the current visitor state
    :param attr: the attribute that cannot be validated
    :param value: the given value of the attribute
    :param valid_value_message: an explicit message about the error and the way to fix it
    """
    message = VALUE_ERROR_MESSAGE.format(
        traceback=state.formatted_traceback(),
        attr=attr,
        message=valid_value_message,
        actual=value
    )
    validation_error(state, message)


PATTERN_NAME = re.compile(r'^[a-zA-Z0-9_\-]+$')


def validate_string(state: VisitorStateValidation, attr: str, value: str, pattern: re.Pattern):
    """
    Check if the given string matches the given pattern. Throws a validation error if not.
    :param state: the current visitor state
    :param attr: the attribute to validate
    :param value: the value to validate
    :param pattern: the pattern the value must match
    """
    if PATTERN_NAME.match(value) is None:
        validation_error_value(state, attr, value, f'Must match /{pattern.pattern}/')
