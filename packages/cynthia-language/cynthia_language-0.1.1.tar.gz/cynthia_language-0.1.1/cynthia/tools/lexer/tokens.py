"""General token definition."""

from enum import Enum
from typing import Any


class Token(object):
    """Class for representing any input as token."""

    def __init__(self, type: Enum, value: Any):
        """Initialize token."""
        self.type = type
        self.value = value

    def __str__(self):
        """String representation of the class instance."""
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        """Show string representation."""
        return self.__str__()
