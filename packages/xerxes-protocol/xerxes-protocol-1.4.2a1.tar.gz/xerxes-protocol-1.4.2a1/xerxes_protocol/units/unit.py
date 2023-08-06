#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__all__ = [
    "Unit"  
]

__author__ = "theMladyPan"
__version__ = "1.4.0"
__license__ = "MIT"
__email__ = "stanislav@rubint.sk"
__status__ = "Production"
__package__ = "xerxes_protocol"
__date__ = "2023-02-22"


class Unit:
    """Base class for all units used in the Xerxes protocol.

    The units are used to represent the values of the messages being sent or received.

    Args:
        value (int|float): The value of the unit.
    """
    _value = 0

    def __init__(self, value: int | float = 0):
        self._value = value

    def preferred(self):
        """Returns the preferred unit for the value."""
        return self._value
    
    @property
    def value(self):
        return self._value
    
    def __repr__(self):
        return f"Unit({self._value})"

    def __radd__(self, other):
        return self._value + other

    def __add__(self, other):
        return self._value + other

    def __sub__(self, other):
        return self._value - other
    
    def __rsub__(self, other):
        return other - self._value


class Index(Unit): 
    ...
