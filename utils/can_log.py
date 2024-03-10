'''
This module autogenerates log files and writes CAN data to them
'''
import time
import signal
import subprocess
import sys
import os
from datetime import datetime
import cantools
import can

formatted_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
CAN_LOG_FILE = f"/home/midnightsun/Documents/{formatted_datetime}.log"

def shutdown_handler(signum, frame):
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
    with open(CAN_LOG_FILE, "a") as log_file:
        log_file.write(CAN_DECODED_DATA + '\n')

def create_log_file():
    '''
    Autogenerates the file if not created already, then writes to it
    '''
    if not os.path.isfile(CAN_LOG_FILE):
        with open(CAN_LOG_FILE, "w") as log_file:
            log_file.write("Log file for CAN decoded data\n")

signal.signal(signal.SIGTERM, shutdown_handler)

create_log_file()

subprocess.run(['sudo', 'ip', 'link', 'set', 'can0', 'up', 'type', 'can', 'bitrate', '500000'])
time.sleep(1)
subprocess.run(['sudo', 'ip', 'link', 'set', 'can0', 'up'])
can_bus = can.interface.Bus(channel='can0', bustype='socketcan')

CAN_DECODED_DATA = (
    'TIME                    '
    + '  |  '
    + '[CAN STATE]'
    + '  |  '
    + 'CAN ID (Hex)  '
    + '   '
    + '  |  '
    + 'DATA'
)
save_data_to_file()

try:
    db = cantools.database.load_file("/home/midnightsun/Downloads/telemMSXV/dbc/system_can.dbc")
except BaseException:
    print("Must generate DBC file first")
    print("Ensure that you have specified the path of the DBC file in .env")

while True:
    try:
        msg = can_bus.recv()
        decoded = db.decode_message(msg.arbitration_id, msg.data)
        name = db.get_message_by_frame_id(msg.arbitration_id).name
        sender = db.get_message_by_frame_id(msg.arbitration_id).senders[0]

        CAN_DECODED_DATA = (
            time.asctime(time.localtime())
            + '  |  '
            + '[CAN WORKS]'
            + '  |  '
            + 'CAN ID (Hex): '
            + str(hex(msg.arbitration_id)[2:].zfill(3))
            + '  |  '
            + 'Msg Name: '
            + name
            + '  |  '
            + 'Msg Sender: '
            + sender
            + '  |  '
            + str(decoded)
            + '  |  '
            + (' '.join(hex(byte)[2:].zfill(2) for byte in msg.data))
        )

        save_data_to_file()

    except Exception as error:
        CAN_DECODED_DATA = (
            time.asctime(time.localtime())
            + '  |  '
            + '[CAN ERROR]'
            + '  |  '
            + 'CAN ID (Hex): '
            + hex(error.args[0])[2:].zfill(3)
        )
        save_data_to_file()
