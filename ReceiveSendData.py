import json
import numpy as np
import matplotlib.pyplot as plt
import csv
import serial

import pylsl
from pylsl import StreamInfo, StreamOutlet


def data_change(I0,I_in):
    if I_in != 0:
        I_change = np.log(I0 / I_in)
        val = True
    else:
        I_change = I_in
        val = False
    return I_change,val

def dpf(age, wv):
    dpf = 223.3 + 0.05624 * pow(age, 0.8493) - 5.723 * pow(10, -7) * pow(wv, 3) + 0.01245 * wv * wv - 0.9025 * wv
    return dpf


def fNIRS_algo2(OD1, OD2, DPF1, DPF2, L1,E):
    E_inv = np.linalg.inv(E)
    delta_OD1 = OD1 / dpf_1
    delta_OD2 = OD2 / dpf_2
    delta_OD1 = delta_OD1[0:len(delta_OD2)]
    OD_mat = np.zeros((2, len(delta_OD1)))
    OD_mat[0] = delta_OD1
    OD_mat[1] = delta_OD2
    coe_mat = (1/L1) * E_inv
    oxy = coe_mat * OD_mat

    return oxy
# user parameters ##########################################################################

def stream_data(port,srate,stream_name,stream_type,num_channels,is_debug):
    port = port
    srate = srate
    stream_name = stream_name
    stream_type = stream_type
    num_channels = num_channels
    is_debug = is_debug


    # init variables ##########################################################################
    info = StreamInfo(stream_name, stream_type, num_channels, srate, 'float32', 'EdgeBCIID')
    outlet = StreamOutlet(info)
    arduino = serial.Serial(port=port, baudrate=9600, timeout=.1)

    #init variables for oxy
    threshold = 3
    I0 = 0
    I1 = 0
    I_change_1  = 0
    I_change_2 = 0

    lambda_1 = 850
    lambda_2 = 770
    age = 22
    dpf_1 = dpf(age, lambda_1)
    dpf_2 = dpf(age, lambda_2)

    E_850_hbo2 = 1058  # extinction coefficients
    E_850_hb = 691.32
    E_770_hbo2 = 650
    E_770_hb = 1311.88

    E = np.matrix([[E_850_hbo2, E_850_hb], [E_770_hbo2, E_770_hb]])  # define E
    R = np.matrix([[1, 0], [0, 1]])  # R matrix

    L1 = 10  # path length
    L2 = 10

    state = 0
    count = 0
    val = False

    # Start of the receiving & sending data loop  ##########################################################################
    while True:
        print("line here")
        val = False
        line = arduino.readline()
        print(line)
        if is_debug: print("Received: {0}".format(line))
        if state == 0:
            if len(line) > 0:
                #print("Inloop")
                cleaned_line = line.decode('utf-8').strip('\r').strip('\n')
                cleaned_line = cleaned_line.strip('\r')
                json_loaded = json.loads(cleaned_line)
                if is_debug: print("json loaded result {0}".format(json.loads(cleaned_line)))
                count = count + 1
                if count > threshold :
                    state = 1
                if type(json_loaded) is dict:
                    print(json_loaded)
                    if 'x'in json_loaded:
                        data_point = json_loaded['x']
                        print("Received data point: {0}".format(data_point))
                        I0 = data_point
                        #outlet.push_sample([0])
                    elif 'x2'in json_loaded:
                        data_point = json_loaded['x2']
                        print("Received data point: {0}".format(data_point))
                        I1 = data_point
                        #outlet.push_sample([0])
        else:
            if len(line) > 0:
                #print("loop2")
                cleaned_line = line.decode('utf-8').strip('\r').strip('\n')
                cleaned_line = cleaned_line.strip('\r')
                json_loaded = json.loads(cleaned_line)
                if is_debug: print("json loaded result {0}".format(json.loads(cleaned_line)))
                count  = count + 1
                if type(json_loaded) is dict:
                    if 'x' in json_loaded:
                        data_point = json_loaded['x']
                        print("Received data point: {0}".format(data_point))
                        I_change_1, val = data_change(I0,data_point)


                    elif 'x2' in json_loaded:
                        data_point = json_loaded['x2']
                        print("Received data point: {0}".format(data_point))
                        I_change_2, val = data_change(I1, data_point)

        if val == True:
            # print("I_change_1 = ",I_change_1)
            # print("I_change_2 = ",I_change_2)
            I_change_1 = np.asarray([I_change_1], dtype=float)
            I_change_2 = np.asarray([I_change_2], dtype=float)

            oxy = fNIRS_algo2(I_change_1, I_change_2, dpf_1, dpf_2, L1, E)
            print(oxy)
        #
            outlet.push_sample([oxy[0],oxy[1]])

        return 0

"""
port = '/dev/cu.usbserial-A6027M9K'
srate = 10
stream_name = 'EdgeBCI'
stream_type = 'fNIRS'
num_channels = 2
is_debug = False

stream_data(port,srate,stream_name,stream_type,num_channels,is_debug)
"""
