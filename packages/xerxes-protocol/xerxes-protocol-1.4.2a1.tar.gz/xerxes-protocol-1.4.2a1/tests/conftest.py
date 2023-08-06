import warnings
import pytest
import serial
import os


@pytest.fixture
def port_name():
    if os.name == "nt":
        # som na windows
        return "COM14"
    else:
        # on linux machine:
        return "/dev/ttyUSB0"
    

@pytest.fixture
def com_port(port_name) -> serial.Serial:
    try:
        com = serial.Serial(port=port_name, baudrate=115200, timeout=0.02)
        yield com
        com.close()
    except serial.SerialException:
        if os.name == "nt":    
            yield None
        else:
            import pty
            master, slave = pty.openpty()
            s_name = os.ttyname(slave)
            com = serial.Serial(s_name, baudrate=115200, timeout=0.02)
            yield com
            com.close

    

@pytest.fixture
def hw_com(com_port, port_name):
    if com_port.port != port_name:
        warnings.warn(UserWarning(f"Using mockup COM port: {com_port}"))
    return com_port.port == port_name

