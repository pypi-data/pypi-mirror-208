#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from xerxes_protocol.ids import MsgId
from xerxes_protocol.hierarchy.leaves.leaf import Leaf, LeafData
from xerxes_protocol.units.unit import Unit
from xerxes_protocol.units.temp import Celsius
import struct


@dataclass
class SLeafData(LeafData):
    strain: Unit
    temperature_external_1: Celsius
    temperature_external_2: Celsius


class SLeaf(Leaf):
    def fetch(self) -> SLeafData:
        reply = self.exchange(bytes(MsgId.FETCH_MEASUREMENT))

        values = struct.unpack("fff", reply.payload)  # unpack 3 floats: strain, temp_e1, temp_e2

        # convert to sensible units
        return SLeafData(
            strain=Unit(values[0]),
            temperature_external_1=Celsius(values[1]),
            temperature_external_2=Celsius(values[2])
        )
        
            
    def __repr__(self):
        return f"SLeaf(addr={self.address}, root={self.root})"
    
        
    
        
    