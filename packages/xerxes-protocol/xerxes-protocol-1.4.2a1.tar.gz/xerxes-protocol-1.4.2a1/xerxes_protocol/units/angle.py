#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import pi
from .unit import Unit


__author__ = "theMladyPan"
__version__ = "1.4.0"
__license__ = "MIT"
__email__ = "stanislav@rubint.sk"
__status__ = "Production"
__package__ = "xerxes_protocol"
__date__ = "2023-02-22"

__all__ = [
    "Angle"
]


class Angle(Unit):
    """Unit of angle

    Args:
        angle (int | float): enter direct angle in radians or use static generators 'from_degrees(degrees)'    
    
    Attributes:
        value (float): angle in radians
        degrees (float): angle in degrees
        rad (float): angle in radians
    
    Methods:
        from_degrees(degrees): returns Angle from degrees
    """    
        
    @property
    def degrees(self):
        return 180 * self.value / pi

    @property
    def rad(self):
        return self.value
    
    @staticmethod
    def from_degrees(deg):
        return Angle(pi*deg/180)

    def __repr__(self):
        return f"Angle({self.value})"
    
    def preferred(self):
        return self.degrees