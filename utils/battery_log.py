'''
This module autogenerates log files and writes Battery stats to them
'''
import time
import signal
import subprocess
import sys
import os
from datetime import datetime
import can

formatted_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
BATTERY_LOG_FILE = f"/home/midnightsun/Documents/Battery/{formatted_datetime}.log"

COUNTER = 0
BATTERY_STATUS_ID = 0x001
BATTERY_VT_ID = 0x001 # needs to be updated

filters = [
  { "can_id": 0x001, "can_mask": 0xFFF, "extended": False }, # BATTERY STATUS ID
  { "can_id": 0x001, "can_mask": 0xFFF, "extended": False } # CURRENT SENSE DATA
]

def shutdown_hadnler(signum, frame):
  '''
  Shutdown handler when Rpi shutoff
  '''
  print("Shutting down gracefully...")
  save_data_to_file()
  sys.exit(0)

def save_data_to_file():
  '''
  Writes data to the file
  '''
  with open(BATTERY_LOG_FILE, "a") as log_file:
    log_file.write(BATTERY_STATS + '\n')

def create_log_file():
  '''
  Autogenerates the file if not created already, then writes to it
  '''
  if not os.path.isfile(BATTERY_LOG_FILE):
    with open(BATTERY_LOG_FILE, "w") as log_file:
      log_file.write("Log file for Battery status\n")

def unpack_message(msg):
  '''
  Unpacks the CAN message into readable data
  '''
  if msg.arbitration_id == BATTERY_STATUS_ID:
    fault = int.from_bytes(msg.data[0:2], byteorder='big')
    fan1_status = int.from_bytes(msg.data[2], byteorder='big')
    fan1_status = int.from_bytes(msg.data[3], byteorder='big')
  elif msg.arbitration_id == BATTERY_VT_ID:
    voltage = int.from_bytes(msg.data[0:2], byteorder='big')
    current = int.from_bytes(msg.data[2:4], byteorder='big')
    temperature = int.from_bytes(msg.data[4:6], byteorder='big')
    batt_soc = int.from_bytes(msg.data[6:8], byteorder='big')
  else:
    print("ERROR")

signal.signal(signal.SIGTERM, shutdown_hadnler)

create_log_file()
subprocess.run(['sudo', 'ip', 'link', 'set', 'can0', 'up', 'type', 'can', 'bitrate', '500000'])
time.sleep(1)
subprocess.run(['sudo', 'ip', 'link', 'set', 'can0', 'up'])
can_bus = can.interface.Bus(channel='can0', bustype='socketcan', can_filters=filters)

BATTERY_STATS = (
  'TIME                    '
  + '  |  '
  + 'MAX CELL VOLTAGE'
  + '  |  '
  + 'MIN CELL VOLTAGE'
  + '  |  '
  + 'CURRENT (mA)'
  + '  |  '
  + 'TEMPERATURE'
  + '  |  '
  + 'FAN 1'
  + '  |  '
  + 'FAN 2'
)
save_data_to_file()

while True:
  COUNTER = (COUNTER + 1) % 61
  if not COUNTER%60:
    subprocess.run(['cat', BATTERY_LOG_FILE])

  try:
    msg = can_bus.recv()
    unpack_message(msg)
    save_data_to_file()

  except Exception as error:
    BATTERY_STATS = (
      time.asctime(time.localtime())
      + '[LOGGING ERROR]'
    )
    save_data_to_file()
