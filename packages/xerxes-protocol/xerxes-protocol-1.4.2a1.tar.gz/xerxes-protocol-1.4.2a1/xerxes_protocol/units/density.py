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
    "Fraction",
    "Density"
]


class Fraction(Unit):
    """Unit of fraction, where 0 is none and 1 complete saturation

    Args:
        Unit (float): enter direct fraction of component or use static generators 'from_ppm(ppm)' or 'from_percent(percent)'   
            
    Attributes:
        value (float): fraction of component
        percent (float): fraction of component in percent
        ppm (float): fraction of component in parts per million

    Methods:
        from_ppm(ppm): returns Fraction from parts per million
        from_percent(percent): returns Fraction from percent
    """
    @property
    def ppm(self):
        """Return Fraction in parts per million

        Returns:
            float: parts per million
        """
        return self.value * 1_000_000

    @property
    def percent(self):
        return self.value * 100.0

    def __repr__(self):
        return f"PPM({self.value})"
    
    
    def preferred(self):
        return self.value
    
    @staticmethod
    def from_ppm(_v):
        return Fraction(
            value=_v / 1_000_000
        )

    @staticmethod
    def from_percent(_v):
        return Fraction(
            value=_v / 100
        )


class Density(Unit):
    """Unit of density, where 0 is none and 1 complete saturation

    Args:
        Unit (float): enter direct fraction of component 
        or use static generators 'from_ppm(ppm)' or 'from_percent(percent)'

    Attributes:
        ug_per_m3 (float): density in micrograms per cubic meter
        kg_per_m3 (float): density in kilograms per cubic meter
    
    Methods:
        from_ug_per_m3(ug_per_m3): returns Density from micrograms per cubic meter
    """

    @property
    def ug_per_m3(self):
        return self.value * 1_000_000_000

    @property
    def kg_per_m3(self):
        return self.value

    def __repr__(self):
        return f"Density({self.value})"

    @property
    def preferred(self):
        return self.kg_per_m3

    @staticmethod
    def from_ug_per_m3(_v):
        return Density(value=_v / 1_000_000_000)