#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Union
import math


MAGIC_UNLOCK = 0x55AA55AA


__all__ = [
    "Id",
    "MsgIdMixin",
    "MsgId",
    "DevIdMixin",
    "DevId"
]

__author__ = "theMladyPan"
__version__ = "1.4.0"
__license__ = "MIT"
__email__ = "stanislav@rubint.sk"
__status__ = "Production"
__package__ = "xerxes_protocol"
__date__ = "2023-02-22"


class Id: 
    ...


class Id:    
    """Base class for all id's used in the Xerxes protocol.

    The id's are used to identify the type of message being sent or the device that is sending or receiving the message.

    Args:
        id (Union[int, bytes]): The id as an integer or as bytes.
    """

    def __init__(self, id: Union[int, bytes]) -> None:
        if isinstance(id, int):
            assert (id >= 0)
        elif isinstance(id, bytes):
            id = int(id.hex(), 16)
        else:
            raise TypeError(f"Unsupported argument, expected int|bytes, got {type(id)} instead")

        self._id: int = id


    def to_bytes(self):
        """Converts the id to bytes."""
        return bytes(self)


    def __bytes__(self) -> bytes:
        id: int = self._id
        byte_length = math.ceil(id.bit_length() / 8)
        
        return id.to_bytes(byte_length, "little")
        

    def __repr__(self):
        return f"Id({bytes(self)})"
    
    
    def __int__(self):
        return int(self._id)
    

    def __str__(self):
        return f"Id({bytes(self).hex()})"


    def __eq__(self, __o: Id) -> bool:
        assert isinstance(__o, Id), f"Invalid object type received, expected {type(Id(0))}, got {type(__o)} instead."
        return self._id == __o._id


    def __hash__(self):
        return int(self._id)
        

class MsgIdMixin(Id):
    """Base class for all message id's used in the Xerxes protocol.

    The message id's are used to identify the type of message being sent.

    Args:
        id (Union[int, bytes]): The id as an integer or as bytes.
    """

    def __init__(self, id: Union[int, bytes]):
        if isinstance(id, bytes):
            assert len(id) == 2
        elif isinstance(id, int):
            assert id >= 0 and id <= 0xFFFF
        else:
            raise TypeError(f"Unsupported argument, expected int|bytes, got {type(id)} instead")
        super().__init__(id)
        
    
    def __bytes__(self):
        return self._id.to_bytes(2, "little")


    def __len__(self):
        return 2


class DevIdMixin(Id):
    """Base class for all device id's used in the Xerxes protocol.

    The device id's are used to identify the device that is sending or receiving the message.

    Args:
        id (Union[int, bytes]): The id as an integer or as bytes.
    """
    
    def __init__(self, id: Union[int, bytes]):
        if isinstance(id, bytes):
            assert len(id) == 1
        elif isinstance(id, int):
            assert id >= 0 and id <= 0xFF
        else:
            raise TypeError(f"Unsupported argument, expected int|bytes, got {type(id)} instead")
        super().__init__(id)
    

    def __len__(self):
        return 1


class MsgId(MsgIdMixin):   
    """Message id's enum used in the Xerxes protocol.
    
    Attributes:
        PING (MsgIdMixin): 
            Ping packet
        PING_REPLY (MsgIdMixin): 
            Reply to ping packet
        ACK_OK (MsgIdMixin): 
            Acknowledge OK packet
        ACK_NOK (MsgIdMixin): 
            Acknowledge NOK packet
        SLEEP (MsgIdMixin): 
            Broadcast sleep to put all devices into low power state
        RESET_SOFT (MsgIdMixin): 
            Soft reset device
        RESET_HARD (MsgIdMixin): 
            Hard reset device a.k.a factory reset
        FETCH_MEASUREMENT (MsgIdMixin): 
            Request to send measurements
        SYNC (MsgIdMixin): 
            Synchronisation message
        WRITE (MsgIdMixin): 
            Set register to a value
        READ_REQ (MsgIdMixin): 
            Read up to <LEN> bytes from device register, starting at <REG_ID>
        READ_REPLY (MsgIdMixin): 
            Reply to read request
        PRESSURE (MsgIdMixin): 
            Pressure value
        STRAIN (MsgIdMixin): 
            Strain value
        PULSES (MsgIdMixin): 
            Number of pulses (counters)
        DISTANCE_22MM (MsgIdMixin): 
            Distance value for 22mm sensor
        DISTANCE_225MM (MsgIdMixin): 
            Distance value for 225mm sensor
        ANGLE_DEG_XY (MsgIdMixin): 
            Angle value for X and Y axis in degrees
    """
    
    # Ping packet
    PING                          = MsgIdMixin(0x0000)
    
    # Reply to ping packet
    PING_REPLY                    = MsgIdMixin(0x0001)  # 1
    
    # Acknowledge OK packet
    ACK_OK                        = MsgIdMixin(0x0002)  # 2
    
    # Acknowledge NOK packet
    ACK_NOK                       = MsgIdMixin(0x0003)  # 3

    # Broadcast sleep to put all devices into low power state 
    # The message prototype  is [MSGID_SLEEP_ALL] <uint32_t>[DURATION_US]
    SLEEP                         = MsgIdMixin(0x0004)  # 4
    
    # Soft reset device
    RESET_SOFT                    = MsgIdMixin(0x00FF)  # 255
    
    # Hard reset device a.k.a factory reset
    RESET_HARD                    = MsgIdMixin(0x00FE)  # 254
    
    # Request to send measurements
    FETCH_MEASUREMENT             = MsgIdMixin(0x0100)  # 256
    
    # Synchronisation message
    SYNC                          = MsgIdMixin(0x0101)  # 257
    
    # Set register to a value 
    # The message prototype is <MSGID_SET> <REG_ID> <LEN> <BYTE_1> ... <BYTE_N>
    WRITE                         = MsgIdMixin(0x0200)  # 512
    
    # Read  up to <LEN> bytes from device register, starting at <REG_ID>
    # The request prototype is <MSGID_READ> <REG_ID> <LEN>           
    READ_REQ                      = MsgIdMixin(0x0201)  # 513
    READ_REPLY                    = MsgIdMixin(0x0202)  # 514
    
    # Pressure value w/o temperature*/ 
    PRESSURE                      = MsgIdMixin(0x0400)  # 1024
    
    STRAIN_24BIT                  = MsgIdMixin(0x1100)  # 4352

    # Cutter 1000P/R, 63mm wheel */
    PULSES                        = MsgIdMixin(0x2A01)  # 10753

    
    # 2 distance values, 0-22000um, no temp
    DISTANCE_22MM                 = MsgIdMixin(0x4000)  # 16384
    # 2 distance values, 0-225000um, no temp
    DISTANCE_225MM                = MsgIdMixin(0x4100)  # 16640
    

    # 2 angle values, X, Y (-90°, 90°)
    ANGLE_DEG_XY                  = MsgIdMixin(0x3000)  # 12288


    def __repr__(self):
        return f"MsgId({int(self)})"


    def __str__(self):
        return self.__repr__()


class DevId(DevIdMixin):
    """Device id's enum used in the Xerxes protocol.
    
    Attributes:
        NULL (DevIdMixin):
            Null device - should not be used - used for debugging
        PRESSURE_600MBAR (DevIdMixin): 
            Pressure sensor range 0-600mbar, output in Pa, 2 external temperature sensors -50/150°C output: mK
        PRESSURE_60MBAR (DevIdMixin): 
            Pressure sensor range 0-60mbar, output in Pa, 2 external temperature sensors -50/150°C output: mK
        STRAIN_24BIT (DevIdMixin):  
            Strain-gauge sensor range 0-2^24, 2 external temperature sensors -50/150°C output: mK
        IO_8DI_8DO (DevIdMixin): 
            I/O device, 8DI/8DO (8xDigital Input, 8xDigital Output)
        IO_4DI_4DO (DevIdMixin): 
            I/O device, 4DI/4DO (4xDigital Input, 4xDigital Output)
        IO_4AI (DevIdMixin):
            I/O device, 4AI (4xAnalog Input)
        ANGLE_XY_90 (DevIdMixin): 
            Angle sensor, X, Y (-90°, 90°)
        ANGLE_XY_30 (DevIdMixin): 
            Angle sensor, X, Y (-30°, 30°)
        DISTANCE_22MM (DevIdMixin): 
            Distance sensor, 0-22000um
        DISTANCE_225MM (DevIdMixin): 
            Distance sensor, 0-225000um
        DEVICE_ENC_1000PPR (DevIdMixin): 
            Cutter 1000P/R, 63mm wheel
        AIR_POL_CO_NOX_VOC (DevIdMixin): 
            Air pollution sensor, CO, NOx, VOC
        AIR_POL_PM (DevIdMixin): 
            Air pollution sensor, PM
        AIR_POL_CO_NOX_VOC_PM (DevIdMixin): 
            Air pollution sensor, CO, NOx, VOC, PM
        AIR_POL_CO_NOX_VOC_PM_GPS (DevIdMixin): 
            Air pollution sensor, CO, NOx, VOC, PM, with GPS location
    """
    NULL                        = DevIdMixin(0x00)
    # Pressure sensors */
    # pressure sensor range 0-600mbar, output in Pa, 2 external temperature sensors -50/150°C output: mK
    PRESSURE_600MBAR            = DevIdMixin(0x03)
    # pressure sensor range 0-60mbar, output in Pa, 2 external temperature sensors -50/150°C output: mK
    PRESSURE_60MBAR             = DevIdMixin(0x04)
    
    # Strain sensors
    # strain-gauge sensor range 0-2^24, 2 external temperature sensors -50/150°C output: mK
    STRAIN_24BIT                = DevIdMixin(0x11)
    
    # I/O Devices
    # I/O device, 8DI/8DO (8xDigital Input, 8xDigital Output)
    IO_8DI_8DO                  = DevIdMixin(0x20)

    # I/O device, 4DI/4DO (4xDigital Input, 4xDigital Output)
    IO_4DI_4DO                  = DevIdMixin(0x21)

    # I/O device, 4AI (4xAnalog Input)
    IO_4AI                      = DevIdMixin(0x22)
    
    # Inclinometers and accelerometers
    # Inclinometer SCL3300
    ANGLE_XY_90                 = DevIdMixin(0x30)

    ANGLE_XY_30                 = DevIdMixin(0x31)
    
    
    # Distance sensors
    # Distance sensor 0-22mm, resistive, linear
    DIST_22MM                   = DevIdMixin(0x40)
    # Distance sensor 0-225mm, resistive, linear
    DIST_225MM                  = DevIdMixin(0x41)
    
    AIR_POL_CO_NOX_VOC          = DevIdMixin(0x50)
    AIR_POL_PM                  = DevIdMixin(0x51)
    AIR_POL_CO_NOX_VOC_PM       = DevIdMixin(0x52)
    AIR_POL_CO_NOX_VOC_PM_GPS   = DevIdMixin(0x53)
    
    # Encoder reader */
    DEVID_ENC_1000PPR           = DevIdMixin(0x2A)
    


    def __repr__(self):
        return f"DevId(0x{bytes(self).hex()})"
    
    
    def __str__(self):
        return self.__repr__()
