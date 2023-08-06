#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from xerxes_protocol.ids import MsgId
from xerxes_protocol.hierarchy.leaves.leaf import Leaf, LeafData
from xerxes_protocol.units.angle import Angle
from xerxes_protocol.units.temp import Celsius
import struct


@dataclass
class ILeafData(LeafData):
    angle_x: Angle
    angle_y: Angle
    temperature_sensor: Celsius
    temperature_external_1: Celsius
    temperature_external_2: Celsius


class ILeaf(Leaf):
    def fetch(self) -> ILeafData:
        reply = self.exchange(bytes(MsgId.FETCH_MEASUREMENT))

        values = struct.unpack("fffff", reply.payload)  # unpack 5 floats: ang_x, ang_y, temp_sensor, temp_e1, temp_e2

        # convert to sensible units
        return ILeafData(
            angle_x=Angle.from_degrees(values[0]),
            angle_y=Angle.from_degrees(values[1]),
            temperature_sensor=Celsius(values[2]),
            temperature_external_1=Celsius(values[3]),
            temperature_external_2=Celsius(values[4])
        )
        
            
    def __repr__(self):
        return f"ILeaf(addr={self.address}, root={self.root})"
    
        
    