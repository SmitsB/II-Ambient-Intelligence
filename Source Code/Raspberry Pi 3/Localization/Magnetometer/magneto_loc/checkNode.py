#!/usr/bin/env python

import argparse

from d7a.alp.command import Command
from d7a.alp.interface import InterfaceType
from d7a.d7anp.addressee import Addressee, IdType
from d7a.sp.configuration import Configuration
from d7a.sp.qos import QoS, ResponseMode
from d7a.system_files.uid import UidFile
from modem.modem import Modem
import time

#Data
mag_values = []
pitchs = []
rolls = []
yaws = []
bars = []

def received_command_callback(cmd):
    dataLocal = cmd.actions[0].operand.data
    print dataLocal
    # mag_values.append(int(format(dataLocal[0], '#010b') + format(dataLocal[1], '08b'),2))
    # pitchs.append(int(format(dataLocal[2], '#010b') + format(dataLocal[3], '08b'), 2))
    # rolls.append(int(format(dataLocal[4], '#010b') + format(dataLocal[5], '08b'), 2))
    # yaws.append(int(format(dataLocal[6], '#010b') + format(dataLocal[7], '08b'), 2))
    # bars.append(int(format(dataLocal[8], '#010b') + format(dataLocal[9], '08b'), 2))


argparser = argparse.ArgumentParser()
argparser.add_argument("-d", "--device", help="serial device /dev file modem",
                            default="/dev/ttyUSB0")
argparser.add_argument("-r", "--rate", help="baudrate for serial device", type=int, default=115200)
argparser.add_argument("-v", "--verbose", help="verbose", default=False, action="store_true")
config = argparser.parse_args()

modem = Modem(config.device, config.rate, receive_callback=received_command_callback, show_logging=config.verbose)

modem.start_reading()


while True:
  pass
