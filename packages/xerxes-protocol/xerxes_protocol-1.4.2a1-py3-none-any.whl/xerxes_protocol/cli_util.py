#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xerxes_protocol import (
    Leaf,
    XerxesNetwork,
    XerxesRoot,
    LeafConfig,
    DebugSerial
)
from serial import Serial
import time
import argparse
import sys
import time
import logging

# parse arguments
parser = argparse.ArgumentParser(description='Read process values from Xerxes Cutter device and print them in tight loop. Use Ctrl+C to exit.')
parser.add_argument(
    '-a', 
    "--address", 
    metavar='ADDR', 
    required=False, 
    type=int, 
    help='address of Xerxes Cutter device'
)
parser.add_argument(
    "-p", 
    '--port', 
    metavar='PORT', 
    required=False, 
    type=str, 
    default="/dev/ttyUSB0", 
    help='port on which Xerxes Cutter device is listening'
)
# add argument whether to use debug serial or not
parser.add_argument(
    "-d", 
    "--debug", 
    action="store_true", 
    help="use debug serial"
)
parser.add_argument(
    "-t",
    "--timeout",
    metavar="TIMEOUT",
    required=False,
    type=float,
    default=0.02,
    help="timeout in seconds for serial communication"
)
parser.add_argument(
    "-l",
    "--loglevel",
    metavar="LOGLEVEL",
    required=False,
    type=str,
    default="INFO",
    help="log level"
)

args = parser.parse_args()

log = logging.getLogger(__name__)
if args.debug:
    level = logging.DEBUG
    port = DebugSerial(args.port)
else:
    port = Serial("/dev/ttyUSB0")
    level = logging.getLevelName(args.loglevel)

logging.basicConfig(
    level=level,
    # print out, module, function and line number
    format="%(module)s %(funcName)s:%(lineno)d %(levelname)s %(message)s"
)

xn = XerxesNetwork(port)
xn.init(timeout=args.timeout)
xr = XerxesRoot(0x1E, xn)


def address_config():
    if args.address is not None:
        leaf = Leaf(args.address, xr)
    else:
        print("looking for leafs...")
        for i in range(0, 254):
            try:
                print(f"{i}", end=", ", flush=True)
                leaf = Leaf(i, xr)
                leaf.ping()
                break
            except TimeoutError:
                pass
    print(f"Ping: {leaf.ping()}")
    print(f"Address: {leaf.device_address}")
    print(f"Config: {leaf.device_config}")
    print(f"device_uid: {leaf.device_uid}")
    
    new_addr = int(input("New address: "))
    leaf.address = new_addr    
    assert leaf.device_address == new_addr
    print(f"Address changed to: {leaf.device_address}")
    enable_freerun = input("Enable freerun? (y/n): ").lower() == "y"
    enable_stat = input("Enable statistic? (y/n): ").lower() == "y"
    config = LeafConfig.freeRun if enable_freerun else 0
    config |= LeafConfig.calcStat if enable_stat else 0
    leaf.device_config = config
    assert leaf.device_config == config
    print(f"Config changed to: {leaf.device_config}")
        

if __name__ == "__main__":
    while True:
        try:
            address_config()
            time.sleep(1)
        except KeyboardInterrupt:
            log.info("Exiting...")
            break
        except Exception as e:
            log.error(f"Error: {e}")
            time.sleep(1)
    port.close()
