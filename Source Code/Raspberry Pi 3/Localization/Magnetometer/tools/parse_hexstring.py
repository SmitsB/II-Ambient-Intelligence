import argparse
import fileinput

from bitstring import ConstBitStream

from d7a.alp.parser import Parser as AlpParser
from d7a.dll.parser import Parser as ForegroundFrameParser
from d7a.serial_console_interface.parser import Parser as SerialParser

parser_types = ["fg", "alp", "serial"]
argparser = argparse.ArgumentParser()
argparser.add_argument("-t", "--type", choices=parser_types, required=True)
argparser.add_argument('data', help="The data to be parsed, input as an hexstring")
args = argparser.parse_args()

hexstring = args.data.strip().replace(' ', '')
data = bytearray(hexstring.decode("hex"))
if args.type == "alp":
  print AlpParser().parse(ConstBitStream(data), len(data))
  exit(0)
if args.type == "serial":
  parser = SerialParser()
if args.type == "fg":
  parser = ForegroundFrameParser()

cmds, info = parser.parse(data)
for cmd in cmds:
  print cmd

print info