#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xerxes_protocol.units.unit import Unit


__author__ = "theMladyPan"
__version__ = "1.4.0"
__license__ = "MIT"
__email__ = "stanislav@rubint.sk"
__status__ = "Production"
__package__ = "xerxes_protocol"
__date__ = "2023-02-22"

__all__ = [
    "Temperature",
    "Celsius",
    "Kelvin"
]


class Temperature(Unit):
    """Base class for all temperature units used in the Xerxes protocol.
    
    The temperature units are used to represent the values of the messages being sent or received.

    Args:
        kelvin (int|float): The value of the temperature in kelvin.

    Attributes:
        kelvin (int|float): The value of the temperature in kelvin.
        celsius (int|float): The value of the temperature in celsius.
        fahrenheit (int|float): The value of the temperature in fahrenheit.
    
    Methods:
        from_milli_kelvin(mK): Creates a new temperature object from a value in millikelvin.
    """
    def __init__(self, kelvin: int | float = 0):
        super().__init__(kelvin)

    @property
    def kelvin(self):
        return self.value


    @property
    def celsius(self):
        return self.value - 273.15


    @property
    def fahrenheit(self):
        return (self.celsius * 9 / 5) + 32

    
    @staticmethod
    def from_milli_kelvin(mK):
        return Temperature(mK/1000)


    def __repr__(self):
        return f"Temperature({self._value})"
    
    
    def preferred(self):
        return self.celsius


class Celsius(Temperature):
    """Class for all temperature units in celsius used in the Xerxes protocol.

    Args:
        celsius (int|float): The value of the temperature in celsius.
    """
    def __init__(self, celsius: int | float = 0):
        super().__init__(celsius + 273.15)
        

class Kelvin(Temperature):
    """Just an alias for the Temperature class."""
    ...
