'''
This module logs CAN messages and decodes them using DBC files (exported from MSXV)
'''

import os
import time
import subprocess
import cantools
import can

can_bus = can.interface.Bus('can0', bustype='socketcan')
subprocess.run(
    ['sudo', 'ip', 'link', 'set', 'can0', 'up', 'type', 'can', 'bitrate', '500000']
)
time.sleep(1)
# Try again
subprocess.run(
    ['sudo', 'ip', 'link', 'set', 'can0', 'up', 'type', 'can', 'bitrate', '500000']
)
subprocess.run(
    ['sudo', 'ip', 'link', 'set', 'can0', 'up'], check=True
)

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
    db = cantools.database.load_file("dbc/system_can.dbc")
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

    except Exception as error:
        CAN_DECODED_DATA = (
            time.asctime(time.localtime())
            + '  |  '
            + '[CAN ERROR]'
            + '  |  '
            + 'CAN ID (Hex): '
            + hex(error.args[0])[2:].zfill(3)
        )
    finally:
        print(CAN_DECODED_DATA)
