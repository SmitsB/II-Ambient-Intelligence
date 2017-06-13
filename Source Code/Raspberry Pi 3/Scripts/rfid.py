#!/usr/bin/env python

import argparse
import os

from d7a.alp.command import Command
from d7a.alp.interface import InterfaceType
from d7a.d7anp.addressee import Addressee, IdType
from d7a.sp.configuration import Configuration
from d7a.sp.qos import QoS, ResponseMode
from d7a.system_files.uid import UidFile
from modem.modem import Modem



# UID of RFID
def received_command_callback(cmd): 
  dataSensor = cmd.actions[0].operand.data # get sensor data
  dataHeader = dataSensor[0]
  print "Data Header: " +  str(dataHeader)
  if (dataHeader == 4 or dataHeader == 0):
    print "RFID"
    b4 = format(dataSensor[1], '08b') # get fourth byte of data
    b3 = format(dataSensor[1], '08b') # get third byte of data
    b2 = format(dataSensor[1], '08b') # get second byte of data
    b1 = format(dataSensor[0], '08b') # get first byte of data
    UID = b1 + b2 + b3 + b4 #switch bytes
    UID = int(UID, 2) # bit to int
    print "UID: " + str(UID) #print UID
 
    if UID == 0:  #presence detection
      command = "mosquitto_pub -d -t sensors/uidD7/presence -m " + str(UID) + "\n"
      os.system("sudo bash /home/pi/shell_scripts/presenceLogger.sh" + "\n")
    else:                 #badge detection
      command = "mosquitto_pub -d -t sensors/uidD7/badge -m " + str(UID) + "\n" 
      os.system("sudo bash /home/pi/shell_scripts/MQTTLogger.sh " + str(UID) + "\n")
      os.system("sudo python /home/pi/profiles/lightshow.py " + str(UID) + "\n")

    #command = "mosquitto_pub -d -t sensors/uidD7 -m " + str(UID) + "\n"
    os.system(command)

  if dataHeader == 21:
    print "Mobile"
    bars = (int(format(dataSensor[1], '#010b') + format(dataSensor[2], '08b') + format(dataSensor[3],'08b'), 2))
    m_alt = bars >> 6
    l_alt = bars & 48
    #bars = int(format(m_alt,'#010b') + format(l_alt,'08b'),2)
    bars = int(m_alt + l_alt / 64)
    #temp = (int(format(dataSensor[10], '#010b') + format(dataSensor[11], '08b'), 2))
    os.system("mosquitto_pub -d -t stm/pressure -m " + str(bars) + "\n")
    m_t = int(dataSensor[4])
    l_t = int(dataSensor[5])
    if m_t > 127:
      m_t = m_t - 256
    temp = int(format(m_t,'#010b') + format(l_t,'08b'), 2)
    os.system("mosquitto_pub -d -t stm/temperature -m " + str(temp/256) + "\n")

argparser = argparse.ArgumentParser()
argparser.add_argument("-d", "--device", help="serial device /dev file modem",
                            default="/dev/ttyUSB0")
argparser.add_argument("-r", "--rate", help="baudrate for serial device", type=int, default=115200)
argparser.add_argument("-v", "--verbose", help="verbose", default=False, action="store_true")
config = argparser.parse_args()

modem = Modem(config.device, config.rate, receive_callback=received_command_callback, show_logging=config.verbose)
modem.d7asp_fifo_flush(
  alp_command=Command.create_with_read_file_action_system_file(
    file=UidFile(),
    interface_type=InterfaceType.D7ASP,
    interface_configuration=Configuration(
      qos=QoS(resp_mod=ResponseMode.RESP_MODE_ALL),
      addressee=Addressee(
        access_class=0x01,
        id_type=IdType.NOID
      )
    )
  )
)

modem.start_reading()
while True:
  pass
