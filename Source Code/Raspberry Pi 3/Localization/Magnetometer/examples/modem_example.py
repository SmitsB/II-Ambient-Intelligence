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


def received_command_callback(cmd):
    print "Link buget = " + str(cmd.interface_status.operand.interface_status.link_budget)


argparser = argparse.ArgumentParser()
argparser.add_argument("-d", "--device", help="serial device /dev file modem",
                            default="/dev/ttyUSB0")
argparser.add_argument("-r", "--rate", help="baudrate for serial device", type=int, default=115200)
argparser.add_argument("-v", "--verbose", help="verbose", default=False, action="store_true")
config = argparser.parse_args()

modem = Modem(config.device, config.rate, receive_callback=received_command_callback, show_logging=config.verbose)

# while True:
#     modem.d7asp_fifo_flush(
#         alp_command=Command.create_with_return_file_data_action(
#             file_id=1,
#             data=[0x00, 0x01],
#             interface_type=InterfaceType.D7ASP,
#             interface_configuration=Configuration(
#                 qos=QoS(resp_mod=ResponseMode.RESP_MODE_ALL),
#                 addressee=Addressee(
#                     access_class=0x01,
#                     id_type=IdType.NOID
#                 )
#             )
#         )
#     )
#     time.sleep(5)

modem.start_reading()


while True:
  pass
