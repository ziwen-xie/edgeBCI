import json

import serial

import pylsl
from pylsl import StreamInfo, StreamOutlet

# user parameters ##########################################################################
port = '/dev/tty.usbmodem14301'
srate = 10
stream_name = 'EdgeBCI'
stream_type = 'fNIRS'
num_channels = 1
is_debug = False

# init variables ##########################################################################
info = StreamInfo(stream_name, stream_type, num_channels, srate, 'float32', 'EdgeBCIID')
outlet = StreamOutlet(info)
arduino = serial.Serial(port=port, baudrate=115200, timeout=.1)


# Start of the receiving & sending data loop  ##########################################################################
while True:
    line = arduino.readline()
    if is_debug: print("Received: {0}".format(line))

    if len(line) > 0:
        cleaned_line = line.decode('utf-8').strip('\r').strip('\n')
        cleaned_line = cleaned_line.strip('\r')
        json_loaded = json.loads(cleaned_line)
        if is_debug: print("json loaded result {0}".format(json.loads(cleaned_line)))

        if type(json_loaded) is dict:
            data_point = json_loaded['x']
            print("Received data point: {0}".format(data_point))
            outlet.push_sample([data_point])

