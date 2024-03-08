import time
import subprocess
import cantools
import can
import signal
import sys

def shutdown_handler(signum, frame):
    print("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)

time.sleep(10)
can_bus = can.interface.Bus('can0', bustype='socketcan')
subprocess.Popen(
    ['sudo', 'ip', 'link', 'set', 'can0', 'up', 'type', 'can', 'bitrate', '500000']
)
time.sleep(10)
subprocess.Popen(
    ['sudo', 'ip', 'link', 'set', 'can0', 'up']
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
