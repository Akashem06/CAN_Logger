#!/bin/bash

CAN_INTERFACE="can0"
pid=$$


cleanup() {
    LOG_FILE=$(grep -o "candump.*log" output.log)
    echo $LOG_FILE
    gawk -i inplace 'match($0, /\(([^)]*)\)/, arr) {
                gsub(/\(([^)]*)\)/, "(" strftime("%c", arr[1]) ")", $0)
            };1' $LOG_FILE
    gawk -i inplace 'match($0, /#([0-9A-Fa-f]+)/, arr) {
        gsub(/../, " & ", arr[1])
        gsub(/#([0-9A-Fa-f]+)/, " " arr[1], $0)
    };1' $LOG_FILE
    echo "KILLING LOGGING SCRIPT"
    exit 0
}

trap cleanup EXIT

touch output.log
sudo ip link set can0 up type can bitrate 500000
sleep 1
sudo ip link set can0 up type can bitrate 500000 # 2nd try
sudo ip link set can0 up
sleep 1
candump -l $CAN_INTERFACE 2> output.log