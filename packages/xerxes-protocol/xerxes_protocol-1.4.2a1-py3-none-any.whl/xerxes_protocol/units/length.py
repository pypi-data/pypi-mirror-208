#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .unit import Unit


__author__ = "theMladyPan"
__version__ = "1.4.0"
__license__ = "MIT"
__email__ = "stanislav@rubint.sk"
__status__ = "Production"
__package__ = "xerxes_protocol"
__date__ = "2023-02-22"

__all__ = [
    "Length"
]


class Length(Unit):
    """Base class for all length units used in the Xerxes protocol.

    Args:
        m (int|float): The value of the length in meters.

    Attributes:
        m (int|float): The value of the length in meters.
        mm (int|float): The value of the length in millimeters.
    """
    
    @property
    def m(self):
        return self.value

    @property
    def mm(self):
        return self.value * 1000.0

    def __repr__(self):
        return f"Length({self.value})"

    def preferred(self):
        return self.m
