import time
import subprocess
import cantools
import can
import signal
import sys
import os
from datetime import datetime

formatted_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
print(formatted_datetime)

# Create the file name based on the formatted date and time
CAN_LOG_FILE = f"{formatted_datetime}.txt"


def shutdown_handler(signum, frame):
    print("Shutting down gracefully...")
    save_data_to_file()
    sys.exit(0)

def save_data_to_file():
    with open(CAN_LOG_FILE, "a") as log_file:
        log_file.write(CAN_DECODED_DATA + '\n')

def create_log_file():
    if not os.path.isfile(CAN_LOG_FILE):
        with open(CAN_LOG_FILE, "w") as log_file:
            log_file.write("Log file for CAN decoded data\n")

signal.signal(signal.SIGTERM, shutdown_handler)

create_log_file()

time.sleep(1)
can_bus = can.interface.Bus('can0', bustype='socketcan')

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
print(CAN_DECODED_DATA + '\n')

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

    finally:
        print(CAN_DECODED_DATA)
