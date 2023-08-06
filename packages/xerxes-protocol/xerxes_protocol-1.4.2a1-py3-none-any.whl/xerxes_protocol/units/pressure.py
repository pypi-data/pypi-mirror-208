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
    "Pressure",
    "Pascal",
    "Nivelation",
    "_g"
]


class Pressure(Unit):
    """Base class for all pressure units used in the Xerxes protocol.

    Args:
        Pa (int|float): The value of the pressure in pascal.

    Attributes:
        Pa (int|float): The value of the pressure in pascal.
        mmH2O (int|float): The value of the pressure in millimeters of water.
        bar (int|float): The value of the pressure in bar.
    
    Methods:
        from_micro_bar(ubar): Creates a new pressure object from a value in microbar.
    """
    @property
    def mmH2O(self):
        return self._value * 0.10197162129779283

    @property
    def bar(self):
        return self._value * 0.00001

    @property
    def Pascal(self):
        return self.value
    
    @staticmethod
    def from_micro_bar(ubar):
        return Pressure(ubar/10)

    def __repr__(self):
        return f"Pressure({self.value})"

    def preferred(self):
        return self.Pascal


def Pascal(Pa) -> Pressure:
    """Creates a new pressure object from a value in pascal.

    Args:
        Pa (int|float): The value of the pressure in pascal.
    """
    return Pressure(Pa)


_g = 9.80665


class Nivelation(Pressure):
    """Base class for all nivelation units used in the Xerxes protocol.

    Args:
        Pa (int|float): The value of the pressure in pascal.

    Methods:
        mm_ethyleneglycol(): Returns the value of the pressure in millimeters of ethylene glycol.
        mm_water(): Returns the value of the pressure in millimeters of water.
        mm_siloxane(): Returns the value of the pressure in millimeters of siloxane.
        mm_propyleneglycol(): Returns the value of the pressure in millimeters of propylene glycol.
        preferred(): Returns the preferred unit for the value which is millimeters of propylene glycol.
    """
    def mm_ethyleneglycol(self):
        return self.value / (_g * 1.1132)

    def mm_water(self):
        return self.value / (_g * 1)

    def mm_siloxane(self):
        return self.value / (_g * 0.965)
    
    def mm_propyleneglycol(self):
        return self.value / (_g * 1.04)

    def preferred(self):
        return self.mm_propyleneglycol()
