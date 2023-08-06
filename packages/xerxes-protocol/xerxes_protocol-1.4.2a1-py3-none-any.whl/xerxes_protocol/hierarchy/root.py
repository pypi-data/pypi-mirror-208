#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import time
from typing import Union
from xerxes_protocol.defaults import (
    DEFAULT_BROADCAST_ADDRESS,
    PROTOCOL_VERSION_MAJOR,
    PROTOCOL_VERSION_MINOR
)
from xerxes_protocol.ids import MsgId, DevId
from xerxes_protocol.network import (
    Addr,
    XerxesNetwork,
    NetworkError,
    XerxesPingReply,
    MessageIncomplete,
    ChecksumError
)
import logging
_log = logging.getLogger(__name__)


__author__ = "theMladyPan"
__version__ = "1.4.0"
__license__ = "MIT"
__email__ = "stanislav@rubint.sk"
__status__ = "Production"
__package__ = "xerxes_protocol"
__date__ = "2023-02-22"

__all__ = [
    "XerxesRoot",
    "BROADCAST_ADDR"
]


BROADCAST_ADDR = Addr(DEFAULT_BROADCAST_ADDRESS)


class XerxesRoot:
    """Root node of the Xerxes network.

    This class is the root node of the Xerxes network. It is used to send and
    receive messages from the network. It is also used to send and receive
    messages from the leaves.

    Args:
        my_addr (Union[Addr, int, bytes]): The address of this node.
        network (XerxesNetwork): The network to use.

    Attributes:
        _addr (Addr): The address of this node.
        network (XerxesNetwork): The network to use.
    """
    def __init__(self, my_addr: Union[int, bytes], network: XerxesNetwork):
        if isinstance(my_addr, int) or isinstance(my_addr, bytes):
            self._addr = Addr(my_addr)
        elif isinstance(my_addr, Addr):
            self._addr = my_addr
        else:
            raise TypeError(f"my_addr type wrong, expected Union[Addr, int, bytes], got {type(my_addr)} instead")  # noqa: E501
        assert isinstance(network, XerxesNetwork)
        self.network = network


    def __repr__(self) -> str:
        return f"XerxesRoot(my_addr={self._addr}, network={self.network})"


    def send_msg(self, destination: int | bytes | Addr, payload: bytes) -> int | None:
        """Send a message to the network.

        Args:
            destination (int | bytes | Addr): The destination address.
            payload (bytes): The payload to send.
        
        Returns:
            int | None: The number of bytes sent or None if the message was
                not sent.
        """
        
        # send the message to the network - all checks are done in the network
        bytes_sent = self.network.send_msg(
            source=self._addr,
            destination=destination,
            payload=payload
        )

        return bytes_sent

    @property
    def address(self):
        return self._addr


    @address.setter
    def address(self, __v):
        self._addr = Addr(__v)


    def broadcast(self, payload: bytes) -> None:
        """Broadcast a message to the network = all nodes."""
        self.network.send_msg(
            source=self.address,
            destination=BROADCAST_ADDR,
            payload=payload
        )


    def sync(self) -> None:
        """Send a sync message to the network."""
        self.broadcast(payload=bytes(MsgId.SYNC))


    def ping(self, addr: Addr | int | bytes, attempts: int = 3) -> XerxesPingReply:
        """Ping a node on the network.

        Args:
            addr (Addr | int | bytes): The address of the node to ping.
        
        Returns:
            XerxesPingReply: The ping reply. Contains the latency, the device
                ID, and the protocol version.
        """

        # sanitize the number of attempts
        attempts = max(1, int(attempts))

        # sanitize the address
        if isinstance(addr, int):
            addr = Addr(addr)
        
        addr = bytes(addr)
        
        assert isinstance(addr, bytes), f"addr type wrong, expected int, bytes or Addr, got {type(addr)} instead"

        for attempt in range(int(attempts)):
            start = time.perf_counter()

            self.network.send_msg(
                source=self.address,
                destination=addr,
                payload=bytes(MsgId.PING)
            )
            try:
                reply = self.network.read_msg()
            except TimeoutError:
                _log.debug(f"Timeout while waiting for ping reply, attempt {attempt + 1} of {attempts}")
                continue
            except MessageIncomplete:
                _log.debug(f"Message incomplete while waiting for ping reply, attempt {attempt + 1} of {attempts}")
                continue
            except ChecksumError:
                _log.debug(f"Checksum error while waiting for ping reply, attempt {attempt + 1} of {attempts}")
                continue

            end = time.perf_counter()

            if reply.message_id == MsgId.PING_REPLY:
                rpl = struct.unpack("BBB", reply.payload)
                ping_reply = XerxesPingReply(
                    dev_id=DevId(rpl[0]),
                    v_maj=int(rpl[1]),
                    v_min=int(rpl[2]),
                    latency=(end - start)
                )
                return ping_reply
            else:
                raise NetworkError("Invalid reply received ({reply.message_id})")
            
        raise TimeoutError("No ping reply received")


    @staticmethod
    def isPingLatest(pingPacket: XerxesPingReply) -> bool:
        """Check if the ping reply is the latest version of the protocol

        Args:
            pingPacket (XerxesPingReply): Ping packet to check

        Returns:
            bool: True if the ping reply is the latest version of the protocol
        """
        return (
            pingPacket.v_maj == PROTOCOL_VERSION_MAJOR and
            pingPacket.v_min == PROTOCOL_VERSION_MINOR and 
            pingPacket.dev_id != DevId.NULL
        )
