'''
This module logs CAN messages and decodes them using DBC files (exported from MSXV)
'''

import os
import time
import subprocess
from dotenv import load_dotenv
import cantools
import can

load_dotenv()
can_bus = can.interface.Bus('can0', bustype='socketcan')
subprocess.run(
    ['sudo', 'ip', 'link', 'set', 'can0', 'up', 'type', 'can', 'bitrate', '500000'], check=True
)
time.sleep(1)
# Try again
subprocess.run(
    ['sudo', 'ip', 'link', 'set', 'can0', 'up', 'type', 'can', 'bitrate', '500000'], check=True
)
subprocess.run(
    ['sudo', 'ip', 'link', 'set', 'can0', 'up'], check=True
)

try:
    db = cantools.database.load_file(os.getenv("DBC_PATH"))
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
            + '     '
            + name
            + '  |  '
            + sender
            + '  |  '
            + str(decoded)
            + '  |  '
            + (' '.join(hex(byte)[2:].zfill(2) for byte in msg.data))
        )

    except Exception as error:
        CAN_DECODED_DATA = '[CAN ERROR/DECODE ERROR]' + '  |  ' + str(error)
    finally:
        print(CAN_DECODED_DATA)
