from serial import Serial
import logging
_log = logging.getLogger(__name__)


class DebugSerial(Serial):
    """Debug serial port encapsulation class.
    
    This class is used to debug the serial communication. It is a wrapper
    around the serial.Serial class. Each time a serial communication is
    performed, the data is printed to the console.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the DebugSerial class.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)


    def write(self, data: bytes) -> int:
        """Write data to the serial port.

        Args:
            data (bytes): Data to write to the serial port.

        Returns:
            int: Number of bytes written to the serial port.
        """
        _log.debug(f"Write: {data.hex(':')}")
        return super().write(data)


    def read(self, size: int = 1) -> bytes:
        """Read data from the serial port.

        Args:
            size (int, optional): Number of bytes to read. Defaults to 1.

        Returns:
            bytes: Data read from the serial port.
        """
        data: bytes = super().read(size)
        _log.debug(f"Read: {data.hex(':')}")
        return data


    def read_until(self, terminator: bytes = b"\n", size: int = None) -> bytes:
        """Read data from the serial port until the terminator is found.

        Args:
            terminator (bytes, optional): Terminator to search for. Defaults to b"\n".
            size (int, optional): Maximum number of bytes to read. Defaults to None.

        Returns:
            bytes: Data read from the serial port.
        """
        data = super().read_until(terminator, size)
        _log.debug(f"Read: {data}")
        return data


    def read_all(self) -> bytes:
        """Read all data from the serial port.

        Returns:
            bytes: Data read from the serial port.
        """
        data = super().read_all()
        _log.debug(f"Read: {data}")
        return data


    def read_line(self) -> bytes:
        """Read a line from the serial port.

        Returns:
            bytes: Data read from the serial port.
        """
        data = super().read_line()
        _log.debug(f"Read: {data}")
        return data


    def readlines(self) -> list:
        """Read all lines from the serial port.

        Returns:
            list: Data read from the serial port.
        """
        data = super().readlines()
        _log.debug(f"Read: {data}")
        return data


    def readline(self, size: int = -1) -> bytes:
        """Read a line from the serial port.

        Args:
            size (int, optional): Maximum number of bytes to read. Defaults to -1.

        Returns:
            bytes: Data read from the serial port.
        """
        data = super().readline(size)
        _log.debug(f"Read: {data}")
        return data
