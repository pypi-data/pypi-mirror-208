#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from xerxes_protocol.ids import MsgId
from xerxes_protocol.hierarchy.leaves.leaf import Leaf, LeafData
from xerxes_protocol.units.length import Length
from xerxes_protocol.units.temp import Celsius
from xerxes_protocol.units.unit import Index
import struct


@dataclass
class DLeafData(LeafData):
    distance_1: Length
    distance_2: Length
    raw_1: Index
    raw_2: Index
    temperature_external_1: Celsius
    temperature_external_2: Celsius


class DLeaf(Leaf):
    def fetch(self) -> DLeafData:
        reply = self.exchange(bytes(MsgId.FETCH_MEASUREMENT))

        values = struct.unpack("ffffff", reply.payload)  # unpack 6 floats: distance1, distance2, raw1, raw2, temp_e1, temp_e2

        # convert to sensible units
        return DLeafData(
            distance_1=Length(values[0]),
            distance_2=Length(values[1]),
            raw_1=Index(values[2]),
            raw_2=Index(values[3]),
            temperature_external_1=Celsius(values[4]),
            temperature_external_2=Celsius(values[5])
        )
        
            
    def __repr__(self):
        return f"DLeaf(addr={self.address}, root={self.root})"
    
        
    
        
    