"""
This module logs CAN messages and decodes them using DBC files (exported from MSXV).
"""

from tabulate import tabulate
import os
import time
import subprocess
import cantools
import can

# Set up CAN interface
can_bus = can.interface.Bus('can0', bustype='socketcan')

# Configure CAN interface settings
subprocess.run(['sudo', 'ip', 'link', 'set', 'can0', 'up', 'type', 'can', 'bitrate', '500000'])
time.sleep(1)

# Try again
subprocess.run(['sudo', 'ip', 'link', 'set', 'can0', 'up', 'type', 'can', 'bitrate', '500000'])
subprocess.run(['sudo', 'ip', 'link', 'set', 'can0', 'up'], check=True)

# Header for CAN decoded data table
CAN_DECODED_DATA_HEADER = [
    'TIME',
    'CAN STATE',
    'CAN ID (Hex)',
    'Name',
    'Sender',
    'Decoded',
    'Bytes'
]

print(tabulate([CAN_DECODED_DATA_HEADER], tablefmt="plain"))

try:
    db = cantools.database.load_file("dbc/system_can.dbc")
except FileNotFoundError:
    print("DBC file not found. Generate DBC file first.")
    print("Ensure that you have specified the path of the DBC file in .env")

while True:
    try:
        # Receive CAN message
        msg = can_bus.recv()

        # Decode CAN message
        decoded = db.decode_message(msg.arbitration_id, msg.data)
        name = db.get_message_by_frame_id(msg.arbitration_id).name
        sender = db.get_message_by_frame_id(msg.arbitration_id).senders[0]

        # Format and print decoded data using tabulate
        data_row = [
            time.asctime(time.localtime()),
            '[CAN WORKS]',
            f'CAN ID (Hex): {str(hex(msg.arbitration_id)[2:].zfill(3))}',
            name,
            sender,
            str(decoded),
            ' '.join(hex(byte)[2:].zfill(2) for byte in msg.data)
        ]

    except Exception as error:
        # Handle CAN decoding error
        data_row = [
            time.asctime(time.localtime()),
            '[CAN ERROR]',
            f'CAN ID (Hex): {hex(error.args[0])[2:].zfill(3)}'
        ]
    finally:
        print(tabulate([data_row], tablefmt="plain"))
