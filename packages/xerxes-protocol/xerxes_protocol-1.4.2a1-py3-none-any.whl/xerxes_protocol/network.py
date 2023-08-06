#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from dataclasses import dataclass, asdict
import struct
import time
from typing import Union
import serial
from xerxes_protocol.ids import DevId, MsgId
from xerxes_protocol.defaults import DEFAULT_BAUDRATE, DEFAULT_TIMEOUT


_all_ = [
    "ChecksumError",
    "MessageIncomplete",
    "InvalidMessage",
    "LengthError",
    "NetworkError",
    "checksum",
    "Addr",
    "XerxesMessage",
    "XerxesPingReply",
    "FutureXerxesNetwork",
    "XerxesNetwork"
]


__author__ = "theMladyPan"
__version__ = "1.4.2"
__license__ = "MIT"
__email__ = "stanislav@rubint.sk"
__status__ = "Production"
__package__ = "xerxes_protocol"
__date__ = "2023-05-15"


class ChecksumError(Exception): 
    """Raised when the checksum of a message is invalid."""


class MessageIncomplete(Exception): 
    """Raised when the message is incomplete."""


class InvalidMessage(Exception): 
    """Raised when the message is invalid."""


class NetworkError(Exception): 
    """Raised when the network is not ready or any other network error occurs."""


def checksum(message: bytes) -> bytes:
    """Calculates the checksum of the message.
    
    Args:
        message (bytes): Message to calculate the checksum of.
    
    Returns:
        bytes: Checksum of the message.
    """

    summary = sum(message)
    summary ^= 0xFF  # get complement of summary
    summary += 1  # get 2's complement
    summary %= 0x100  # get last 8 bits of summary
    return summary.to_bytes(1, "little")


class Addr(int):
    """Address of a node in the Xerxes network.

    Args:
        addr (Union[int, bytes]): Address of the node.

    Attributes:
        addr (int): Address of the node.

    Raises:
        AssertionError: If the address is not of type int or bytes.
        AssertionError: If the address is negative.
        AssertionError: If the address is greater than 255. 
    """

    def __new__(cls, addr: Union[int, bytes]) -> None:
        if isinstance(addr, bytes):
            addr = int(addr.hex(), 16)

        assert isinstance(addr, int), f"address must be of type bytes|int, got {type(addr)} instead."
        assert addr >= 0, "address must be positive"
        assert addr < 256, "address must be lower than 256"

        return super().__new__(cls, addr)


    def to_bytes(self):
        """Converts the address to bytes."""

        return int(self).to_bytes(1, "little")


    def __bytes__(self):
        return self.to_bytes()


    def __repr__(self):
        return f"Addr(0x{self.to_bytes().hex()})"


    def __eq__(self, __o: object) -> bool:
        return int(self) == int(__o)


    def __hash__(self) -> int:
        return int(self)


@dataclass
class XerxesMessage:
    """Data class for Xerxes message.
    
    Attributes:
        source (Addr): Source address
        destination (Addr): Destination address
        length (int): Length of the message
        message_id (MsgId): Message id
        payload (bytes): Payload of the message
        latency (float): Latency of the message
        crc (int): Checksum of the message        
    """

    source: Addr
    destination: Addr
    length: int
    message_id: MsgId
    payload: bytes
    latency: float = 0.0
    crc: int = 0
    

@dataclass
class XerxesPingReply:
    """Data class for Xerxes ping reply.

    Attributes:
        dev_id (DevId): Device id
        v_maj (int): Major version of the device
        v_min (int): Minor version of the device
        latency (float): Latency of the message
    """

    dev_id: DevId
    v_maj: int
    v_min: int
    latency: float

    def as_dict(self):
        return {
            "dev_id": str(self.dev_id),
            "version": f"{self.v_maj}.{self.v_min}",
            "latency": self.latency
        }


class FutureXerxesNetwork:
    """Mock class for XerxesNetwork.
    
    Used for configuring the network before the real XerxesNetwork is created.   
    """

    def send_msg(self, __dst, __pld) -> None:
        raise NotImplementedError("You should assign real XerxesNetwork instead of FutureXN")
    
    
    def read_msg(self) -> None:
        raise NotImplementedError("You should assign real XerxesNetwork instead of FutureXN")
    
    
    def __repr__(self):
        return "FutureXerxesNetwork()"


class XerxesNetwork: 
    """Mock used for type hinting."""


class XerxesNetwork:
    """Class for communication with Xerxes network.

    Args:
        port (str): Serial port name

    Attributes:
        _ic (int): Internal counter for message ids
        _instances (dict): Dictionary of instances of XerxesNetwork
        _opened (bool): True if the port is opened, False otherwise
    
    Raises:
        AssertionError: If the port is not a serial.Serial object

    Example:
        >>> from xerxes_protocol import XerxesNetwork
        >>> from xerxes_protocol.ids import DevId
        >>> from xerxes_protocol.defaults import DEFAULT_BAUDRATE, DEFAULT_TIMEOUT
        >>> import serial
        >>> 
        >>> # create a serial port object
        >>> port = serial.Serial(port="/dev/ttyUSB0")
        >>>
        >>> # create a network object
        >>> network = XerxesNetwork(port)
        >>>
        >>> # initialize the network
        >>> network.init(baudrate=DEFAULT_BAUDRATE, timeout=DEFAULT_TIMEOUT)
        >>>
        >>> # send a message
        >>> network.send_msg(Addr(0x00), Addr(0x01), b"Hello World!")
        >>>
        >>> # read a message
        >>> msg = network.read_msg()
        >>> print(msg)
        XerxesMessage(source=Addr(0x01), destination=Addr(0x00), length=12, message_id=MsgId(0x00), payload=b'\x04\x01\x04', latency=0.015, crc='U')

    """

    _ic = 0  # not used yet
    _instances = {}
    _opened = False


    def __init__(self, port: serial.Serial) -> None:
        assert isinstance(port, serial.Serial)
        self._s = port

    
    def init(self, baudrate: int = DEFAULT_BAUDRATE, timeout: float = DEFAULT_TIMEOUT) -> XerxesNetwork:
        """Initializes the serial port.

        Args:
            baudrate (int, optional): Baudrate. Defaults to DEFAULT_BAUDRATE.
            timeout (float, optional): Timeout in seconds. Defaults to DEFAULT_TIMEOUT.
        
        Returns:
            XerxesNetwork: self
        """
        self._s.baudrate = baudrate
        self._s.timeout = timeout
        
        if not self._s.isOpen():
            self._s.open()
        self._opened = True
        self._s._reconfigure_port()

        return self
     

    @property
    def timeout(self) -> float:
        """Timeout for serial port in seconds."""

        return self._s.timeout
    

    @timeout.setter
    def timeout(self, value: float) -> None:
        """Timeout for serial port in seconds."""

        self._s.timeout = value
        self._s._reconfigure_port()


    @property
    def opened(self) -> bool:
        """Returns True if the serial port is opened."""

        return bool(self._opened)


    def __new__(cls: XerxesNetwork, port: str) -> XerxesNetwork:
        if port not in cls._instances.keys():
            cls._instances[port] = object.__new__(cls)

        return cls._instances[port]


    def __repr__(self) -> str:
        _repr = (
            f"XerxesNetwork(port=Serial(port='{self._s.port}',"
            f"baudrate={self._s.baudrate}, timeout={self._s.timeout}))"
        )
        return _repr
                


    def __del__(self):
        self._s.close()


    def read_msg(self) -> XerxesMessage:
        """Reads a Xerxes packet from the serial port.

        Returns:
            XerxesMessage: Message object

        Raises:
            TimeoutError: If no message is received in the timeout period
            MessageIncomplete: If the message is incomplete
            ChecksumError: If the checksum is invalid
        """
        assert self._opened, "Serial port not opened yet. Call .init() first"

        start_time = time.perf_counter_ns()

        # wait for start of message
        next_byte = self._s.read(1)
        while next_byte != b"\x01":
            next_byte = self._s.read(1)
            if len(next_byte) == 0:
                raise TimeoutError("No message in queue")

        chs = 0x01
        # read message length
        msg_len = int(self._s.read(1).hex(), 16)
        chs += msg_len

        # read source and destination address
        src = self._s.read(1)
        dst = self._s.read(1)

        for i in [src, dst]:
            chs += int(i.hex(), 16) 

        # read message ID
        msg_id_raw = self._s.read(2)
        if (len(msg_id_raw) != 2):
            raise MessageIncomplete("Invalid message id received")
        for i in msg_id_raw:
            chs += i

        msg_id = struct.unpack("H", msg_id_raw)[0]

        # read and unpack all data into array, assuming it is uint32_t, little-endian
        raw_msg = bytes(0)
        
        # for i in range(int(msg_len - 7)):
        #     next_byte = self._s.read(1)  # WIP: read multiple bytes at once for fuck sake
        #     if (len(next_byte) != 1):
        #         raise MessageIncomplete("Received message incomplete")
        #     raw_msg += next_byte
        #     chs += int(next_byte.hex(), 16)

        raw_msg += self._s.read(msg_len - 7)
        if len(raw_msg) != msg_len - 7:
            raise MessageIncomplete("Received message incomplete")
        
        for _b in raw_msg:
            chs += _b
        
        # read checksum
        rcvd_chks = self._s.read(1)
        if len(rcvd_chks) != 1:
            raise MessageIncomplete("Received message incomplete")
        chs += int(rcvd_chks.hex(), 16)
        chs %= 0x100
        if chs:
            raise ChecksumError("Invalid checksum received")
        
        end_time = time.perf_counter_ns()

        return XerxesMessage(
            source=Addr(src),
            destination=Addr(dst),
            length=msg_len,
            message_id=MsgId(msg_id),
            payload=raw_msg,
            latency=(end_time - start_time) / 1e9,
            crc=chs
        )
    
    
    def wait_for_reply(self, timeout: float) -> XerxesMessage:
        """Wait for reply from device for a given time
        
        Args:
            timeout (float): timeout in seconds

        Returns:
            XerxesMessage: reply message
        """
        old_t = self._s.timeout
        self._s.timeout = timeout
        self._s._reconfigure_port()
        rply = self.read_msg()
        self._s.timeout = old_t
        self._s._reconfigure_port()
        return rply


    def send_msg(self, source: int | bytes | Addr, destination: int | bytes | Addr, payload: bytes) -> int | None:    
        """Send message to device

        Args:
            source (int | bytes | Addr): source address
            destination (int | bytes | Addr): destination address
            payload (bytes): payload in bytes - must be less 247 bytes
        
        Raises:
            AssertionError: if serial port is not opened
            AssertionError: if payload is not bytes
            AssertionError: if source or destination is not int, bytes or Addr

        Returns:
            int | None: number of bytes sent or None if serial port is not opened or message was not sent
        """
        
        assert self._opened, "Serial port was not opened yet. Call .init() on XerxesNetwork object first"
        
        # if source or destination is int, convert to Addr
        if type(source) is int:
            source = Addr(source)

        if type(destination) is int:
            destination = Addr(destination)
        
        # payload must be in bytes
        assert isinstance(payload, bytes)

        # convert source and destination to bytes if they are not
        if isinstance(source, bytes):
            _b_source = source
        else:
            _b_source = bytes(source)

        if isinstance(destination, bytes):
            _b_destination = destination
        else:
            _b_destination = bytes(destination)
            
        # create message
        SOH = b"\x01"

        msg = SOH  # Start of header
        msg += (len(payload) + 5).to_bytes(1, "little")  # Length of the message
        msg += _b_source  # From - sender
        msg += _b_destination  # Destination address - recipient
        msg += payload  # Payload without checksum
        msg += checksum(msg)  # Checksum

        # send message and return number of bytes sent
        return self._s.write(msg) 
