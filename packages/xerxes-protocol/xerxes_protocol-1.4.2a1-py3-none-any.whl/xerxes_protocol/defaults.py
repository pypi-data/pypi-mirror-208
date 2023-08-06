"""Default values for the Xerxes protocol.

This module contains the default values for the Xerxes protocol.

Attributes:
    DEFAULT_BAUDRATE (int): The default baudrate for the serial connection.
    DEFAULT_BROADCAST_ADDRESS (int): The default broadcast address.
    DEFAULT_TIMEOUT (float): The default timeout for the serial connection.
    PROTOCOL_VERSION_MAJOR (int): The major version of the Xerxes protocol.
    PROTOCOL_VERSION_MINOR (int): The minor version of the Xerxes protocol.
"""

__author__ = "theMladyPan"
__version__ = "1.4.0"
__license__ = "MIT"
__email__ = "stanislav@rubint.sk"
__status__ = "Production"
__package__ = "xerxes_protocol"
__date__ = "2023-02-22"


DEFAULT_BAUDRATE                = 115200
DEFAULT_BROADCAST_ADDRESS       = 0xFF
DEFAULT_TIMEOUT                 = 0.02

PROTOCOL_VERSION_MAJOR          = 1
PROTOCOL_VERSION_MINOR          = 4