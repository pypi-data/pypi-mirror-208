from dataclasses import dataclass

__author__ = "theMladyPan"
__version__ = "1.4.2"
__license__ = "MIT"
__email__ = "stanislav@rubint.sk"
__status__ = "Production"
__package__ = "xerxes_protocol"
__date__ = "2023-05-15"

# non-volatile memory map (persistent)
# memory offset of the offset of the process values
GAIN_PV0_OFFSET = 0
GAIN_PV1_OFFSET = 4
GAIN_PV2_OFFSET = 8
GAIN_PV3_OFFSET = 12

# memory offset of the offset of the process values
OFFSET_PV0_OFFSET = 16
OFFSET_PV1_OFFSET = 20
OFFSET_PV2_OFFSET = 24
OFFSET_PV3_OFFSET = 28

# memory offset of cycle time in microseconds (4 bytes)
OFFSET_DESIRED_CYCLE_TIME = 32

OFFSET_CONFIG_BITS = 40
OFFSET_ADDRESS = 44

# configuration values
CONFIG_VAL0_OFFSET = 48
CONFIG_VAL1_OFFSET = 52
CONFIG_VAL2_OFFSET = 56
CONFIG_VAL3_OFFSET = 60

# Volatile range (not persistent)
PV0_OFFSET = 256
PV1_OFFSET = 260
PV2_OFFSET = 264
PV3_OFFSET = 268

MEAN_PV0_OFFSET = 272
MEAN_PV1_OFFSET = 276
MEAN_PV2_OFFSET = 280
MEAN_PV3_OFFSET = 284

STDDEV_PV0_OFFSET = 288
STDDEV_PV1_OFFSET = 292
STDDEV_PV2_OFFSET = 296
STDDEV_PV3_OFFSET = 300

MIN_PV0_OFFSET = 304
MIN_PV1_OFFSET = 308
MIN_PV2_OFFSET = 312
MIN_PV3_OFFSET = 316

MAX_PV0_OFFSET = 320
MAX_PV1_OFFSET = 324
MAX_PV2_OFFSET = 328
MAX_PV3_OFFSET = 332

DV0_OFFSET = 336
DV1_OFFSET = 340
DV2_OFFSET = 344
DV3_OFFSET = 348

AV0_OFFSET = 352
AV1_OFFSET = 356
AV2_OFFSET = 360
AV3_OFFSET = 364

SV0_OFFSET = 368
SV1_OFFSET = 372
SV2_OFFSET = 376
SV3_OFFSET = 380

MEM_UNLOCKED_OFFSET = 384

# Read only range
STATUS_OFFSET = 512
ERROR_OFFSET = 520
UID_OFFSET = 528

OFFSET_NET_CYCLE_TIME = 544


@dataclass
class ElementType:
    """Represents a memory type in memory.
    
    Attributes:
        _container (bytes | int | float | bool): The container type of the memory type.
        _format (str): The format of the memory type. See struct module for more information.
        _length (int): The length of the memory type in bytes.
    """

    _container: bytes | int | float | bool
    _format: str
    _length: int


class uint64_t(ElementType):
    """Represents a 64 bit unsigned integer in memory."""

    _container = int
    _format = "Q"
    _length = 8


class uint32_t(ElementType):
    """Represents a 32 bit unsigned integer in memory."""

    _container = int
    _format = "I"
    _length = 4


class int32_t(ElementType):
    """Represents a 32 bit signed integer in memory."""

    _container = int
    _format = "i"
    _length = 4


class uint16_t(ElementType):
    """Represents a 16 bit unsigned integer in memory."""

    _container = int
    _format = "H"
    _length = 2


class uint8_t(ElementType):
    """Represents a 8 bit unsigned integer in memory."""

    _container = int
    _format = "B"
    _length = 1


class float_t(ElementType):
    """Represents a 32 bit float in memory."""

    _container = float
    _format = "f"
    _length = 4


class double_t(ElementType):
    """Represents a 64 bit float in memory."""

    _container = float
    _format = "d"
    _length = 8


# frozen dataclass to prevent modification of memory elements after creation
@dataclass(frozen=True)
class MemoryElement:
    """Represents a memory element in the Xerxes memory map.
    
    Attributes:
        mem_addr (int): The memory address of the element.
        mem_type (ElementType): The type of the element.
        write_access (bool): Whether the element can be written to.
    """

    elem_addr: int
    elem_type: ElementType
    write_access: bool = True

    def can_write(self) -> bool:
        """Returns whether the memory element can be written to."""
        return self.write_access


class XerxesMemoryType:
    """Represents a memory access type in the Xerxes memory map."""

    def __str__(self):
        return f"{self.__class__.__name__}(...)"


class MemoryNonVolatile(XerxesMemoryType):
    """Represents the non-volatile memory of the Xerxes memory map.
    
    Attributes:
        gain_pv<n>          (float_t):  The gain of the <n>th process value.
        offset_pv<n>        (float_t):  The offset of the <n>th process value.
        desired_cycle_time  (uint32_t): The desired cycle time in microseconds.
        device_address      (uint8_t):  The device address.
        config              (uint8_t):  The configuration bits.
        config_val<n>       (uint32_t): The <n>th configuration value.
    """
    gain_pv0 = MemoryElement(GAIN_PV0_OFFSET, float_t)
    gain_pv1 = MemoryElement(GAIN_PV1_OFFSET, float_t)
    gain_pv2 = MemoryElement(GAIN_PV2_OFFSET, float_t)
    gain_pv3 = MemoryElement(GAIN_PV3_OFFSET, float_t)

    offset_pv0 = MemoryElement(OFFSET_PV0_OFFSET, float_t)
    offset_pv1 = MemoryElement(OFFSET_PV1_OFFSET, float_t)
    offset_pv2 = MemoryElement(OFFSET_PV2_OFFSET, float_t)
    offset_pv3 = MemoryElement(OFFSET_PV3_OFFSET, float_t)

    desired_cycle_time_us = MemoryElement(OFFSET_DESIRED_CYCLE_TIME, uint32_t)
    device_address = MemoryElement(OFFSET_ADDRESS, uint8_t)
    device_config = MemoryElement(OFFSET_CONFIG_BITS, uint8_t)

    config_val0 = MemoryElement(CONFIG_VAL0_OFFSET, uint32_t)
    config_val1 = MemoryElement(CONFIG_VAL1_OFFSET, uint32_t)
    config_val2 = MemoryElement(CONFIG_VAL2_OFFSET, uint32_t)
    config_val3 = MemoryElement(CONFIG_VAL3_OFFSET, uint32_t)
    

class MemoryVolatile(XerxesMemoryType):
    """Represents the volatile memory of the Xerxes memory map.

    Attributes:
        pv<n>           (float_t):  The <n>th process value.
        mean_pv<n>      (float_t):  The mean of the <n>th process value.
        std_dev_pv<n>   (float_t):  The standard deviation of the <n>th process value.
        min_pv<n>       (float_t):  The minimum of the <n>th process value.
        max_pv<n>       (float_t):  The maximum of the <n>th process value.
        dv<n>           (uint32_t): The <n>th discrete value (0s or 1s), e.g. for digital inputs or outputs.
        av<n>           (float_t):  The <n>th analog value, e.g. for analog inputs or outputs.
        sv<n>           (int32_t):  The <n>th signed value, e.g. for counters.
        mem_unlocked    (uint32_t): Whether the protected memory is unlocked for writing.
    """

    pv0 = MemoryElement(PV0_OFFSET, float_t)
    pv1 = MemoryElement(PV1_OFFSET, float_t)
    pv2 = MemoryElement(PV2_OFFSET, float_t)
    pv3 = MemoryElement(PV3_OFFSET, float_t)

    mean_pv0 = MemoryElement(MEAN_PV0_OFFSET, float_t)
    mean_pv1 = MemoryElement(MEAN_PV1_OFFSET, float_t)
    mean_pv2 = MemoryElement(MEAN_PV2_OFFSET, float_t)
    mean_pv3 = MemoryElement(MEAN_PV3_OFFSET, float_t)

    std_dev_pv0 = MemoryElement(STDDEV_PV0_OFFSET, float_t)
    std_dev_pv1 = MemoryElement(STDDEV_PV1_OFFSET, float_t)
    std_dev_pv2 = MemoryElement(STDDEV_PV2_OFFSET, float_t)
    std_dev_pv3 = MemoryElement(STDDEV_PV3_OFFSET, float_t)

    min_pv0 = MemoryElement(MIN_PV0_OFFSET, float_t)
    min_pv1 = MemoryElement(MIN_PV1_OFFSET, float_t)
    min_pv2 = MemoryElement(MIN_PV2_OFFSET, float_t)
    min_pv3 = MemoryElement(MIN_PV3_OFFSET, float_t)

    max_pv0 = MemoryElement(MAX_PV0_OFFSET, float_t)
    max_pv1 = MemoryElement(MAX_PV1_OFFSET, float_t)
    max_pv2 = MemoryElement(MAX_PV2_OFFSET, float_t)
    max_pv3 = MemoryElement(MAX_PV3_OFFSET, float_t)

    # digital values, for example for digital inputs or outputs
    dv0 = MemoryElement(DV0_OFFSET, uint32_t)  # digital value 1
    dv1 = MemoryElement(DV1_OFFSET, uint32_t)  # digital value 2
    dv2 = MemoryElement(DV2_OFFSET, uint32_t)  # digital value 3
    dv3 = MemoryElement(DV3_OFFSET, uint32_t)  # digital value 4

    # additional analog values, for example for analog inputs or outputs
    av0 = MemoryElement(AV0_OFFSET, float_t)  # analog value 0
    av1 = MemoryElement(AV1_OFFSET, float_t)  # analog value 1
    av2 = MemoryElement(AV2_OFFSET, float_t)  # analog value 2
    av3 = MemoryElement(AV3_OFFSET, float_t)  # analog value 3
    
    # signed values, for example for PID controllers, counters, etc.
    sv0 = MemoryElement(SV0_OFFSET, int32_t)  # signed value 0
    sv1 = MemoryElement(SV1_OFFSET, int32_t)  # signed value 1
    sv2 = MemoryElement(SV2_OFFSET, int32_t)  # signed value 2
    sv3 = MemoryElement(SV3_OFFSET, int32_t)  # signed value 3

    memory_lock = MemoryElement(MEM_UNLOCKED_OFFSET, uint32_t)


class MemoryReadOnly(XerxesMemoryType):
    """Represents the read-only memory of the Xerxes memory map.

    Attributes:
        status              (uint64_t): The status bits of the device.
        error               (uint64_t): The error code bits of the device.
        uid                 (uint64_t): The unique ID of the device.
        net_cycle_time_us   (uint32_t): The network cycle time in microseconds.
    """

    device_status = MemoryElement(STATUS_OFFSET, uint64_t, write_access=False)
    device_error = MemoryElement(ERROR_OFFSET, uint64_t, write_access=False)
    device_uid = MemoryElement(UID_OFFSET, uint64_t, write_access=False)

    net_cycle_time_us = MemoryElement(OFFSET_NET_CYCLE_TIME, uint32_t, write_access=False)


class XerxesMemoryMap(MemoryNonVolatile, MemoryVolatile, MemoryReadOnly):
    """Xerxes memory map class.
    
    This class is used to access the memory of the Xerxes device.
    
    The memory map is split into three classes:
    - MemoryNonVolatile: contains the non-volatile memory elements - these
        elements are stored in the EEPROM of the Xerxes device
    - MemoryVolatile: contains the volatile memory elements - these elements
        are stored in the RAM of the Xerxes device
    - MemoryReadOnly: contains the read-only memory elements - these elements
        are stored in the RAM of the Xerxes device and can only be read        
    """
