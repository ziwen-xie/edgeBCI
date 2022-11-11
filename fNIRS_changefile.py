import numpy as np
import matplotlib.pyplot as plt
import csv


# import txt data files
def import_data(name1, name2, type):
    arr1 = []
    arr2 = []
    if type == 1:

        with open(name1, 'r') as f:

            for line in f:
                current_line = line.split("}")
                for i in range(len(current_line) - 1):
                    temp = current_line[i].split("{")
                    if temp != '':
                        arr1.append(temp[0])

            f.close()

        with open(name2, 'r') as f:

            for line in f:
                current_line = line.split("}")
                for i in range(len(current_line) - 1):
                    temp = current_line[i].split("{")
                    if temp != '':
                        arr2.append(temp[0])

            f.close()

    if type == 2:
        with open(name1, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if (row[1] != '') & (row[1] != 'x'):
                    arr1.append(row[1])
        csv_file.close()

        with open(name2, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if (row[1] != '') & (row[1] != 'x'):
                    arr2.append(row[1])
        csv_file.close()
    print(arr1)
    return arr1, arr2


def dpf(age, wv):
    dpf = 223.3 + 0.05624 * pow(age, 0.8493) - 5.723 * pow(10, -7) * pow(wv, 3) + 0.01245 * wv * wv - 0.9025 * wv
    return dpf

def fNIRS_algo1(OD1, OD2, DPF1, DPF2, L1, L2, E, R):
    E_T = np.transpose(E)
    R_inv = np.linalg.inv(R)
    delta_OD1 = OD1 / (L1 * dpf_1)
    delta_OD2 = OD2 / (L2 * dpf_2)
    print(len(delta_OD2))
    delta_OD1 = delta_OD1[0:len(delta_OD2)]
    print(delta_OD1.shape)
    print(delta_OD2.shape)
    OD_mat = np.zeros((2, len(delta_OD1)))
    OD_mat[0] = delta_OD1
    OD_mat[1] = delta_OD2
    print(OD_mat)

    coe_mat = np.linalg.inv(E_T * R_inv * E) * E_T * R_inv
    oxy = coe_mat * OD_mat



    return delta_OD1,delta_OD2,oxy


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

    return delta_OD1,delta_OD2,oxy

def cal_change(I0_w1,I0_w2,OD1,OD2):
    for i in range(len(OD1)):
        if OD1[i] != 0:
            OD1[i] = np.log(I0_w1 / OD1[i])
    # print(OD1)

    for i in range(len(OD2)):
        if OD2[i] != 0:
            OD2[i] = np.log(I0_w2 / OD2[i])
    return OD1,OD2



"""
#plot
plt.plot(arr1)
plt.show()
plt.plot(arr2)
plt.show()
"""

# algorithm
name1 = 'test1.csv'
name2 = '770nm.csv'


arr1, arr2 = import_data(name1, name2, 2)


# define and initialize
OD1 = np.asarray(arr1, dtype=float)  # change to numpy array
OD2 = np.asarray(arr2, dtype=float)

I0_w1 = OD1[0]  # define the baseline
I0_w2 = OD2[0]

cal_change(I0_w1, I0_w2, OD1, OD2)
# calculate OD
# define coefficients
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
DPF1 = 6  # DPF
DPF2 = 6




delta_OD1,delta_OD2,oxy = fNIRS_algo2(OD1, OD2, dpf_1, dpf_2, L1, E)

t = np.arange(len(delta_OD1))
plt.plot(t, delta_OD1, label='850nm')
plt.plot(t, delta_OD2, label='770nm')
plt.title('Raw Signal')
plt.xlabel("time(ms)")
plt.ylabel("Change of Intensity")

plt.legend()
plt.show()


print(oxy[0].shape)
t = np.arange(len(np.transpose(oxy[0])))
plt.plot(t, np.transpose(oxy[0]), label='HbO2')
plt.plot(t, np.transpose(oxy[1]), label='HbR')
plt.title('Change of concentration over time')
plt.xlabel("time(ms)")
plt.ylabel("change of concentration(uM)")

plt.legend()
plt.show()

