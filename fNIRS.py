import numpy as np
import matplotlib.pyplot as plt


#import txt data files
arr1 = []
arr2 = []

with open('test1.txt','r') as f:

    for line in f:
        current_line = line.split("}")
        for i in range(len(current_line)-1):
            temp = current_line[i].split("{")
            #content = f.readlines()
            if temp != '':
                arr1.append(temp[0])

    f.close()
            
with open('850.txt','r') as f:

    for line in f:
        current_line = line.split("}")
        for i in range(len(current_line)-1):
            temp = current_line[i].split("{")
            if temp != '':
                arr2.append(temp[0])

    f.close()

print(arr1)

"""
#plot
plt.plot(arr1)
plt.show()
plt.plot(arr2)
plt.show()
"""
    
#algorithm

#define and initialize
OD1=np.asarray(arr1,dtype=float)   #change to numpy array
OD2=np.asarray(arr2,dtype=float) 

I0_w1 = OD1[0]   #define the baseline
I0_w2 = OD2[0]

E_850_hbo2= 1058  #extonction coefficients
E_850_hb = 691.32
E_770_hbo2 = 650
E_770_hb = 1311.88

E = np.matrix([[E_850_hbo2, E_850_hb],[E_770_hbo2, E_770_hb]]) #define E
R = np.matrix([[1,0],[0,1]]) # R matrix

E_T = np.transpose(E)
R_inv = np.linalg.inv(R)

L1 = 10  #path length
L2 = 10
DPF1 =6   #DPF
DPF2 = 6

delta_OD1 = OD1/(L1*DPF1)
delta_OD2 = OD2/(L2*DPF2)
print(len(delta_OD2))
delta_OD1 = delta_OD1[0:len(delta_OD2)]
print(delta_OD1.shape)
print(delta_OD2.shape)
OD_mat =  np.zeros((2,len(delta_OD1)))
OD_mat[0] = delta_OD1
OD_mat[1] = delta_OD2
print(OD_mat)

coe_mat = np.linalg.inv(E_T * R_inv * E)*E_T*R_inv
oxy = coe_mat*OD_mat




#calculate OD
for i in range(len(arr1)):
    if OD1[i] != 0:
        OD1[i] = np.log(I0_w1/OD1[i])
#print(OD1)

for i in range(len(arr2)):
    if OD2[i] != 0:
        OD2[i] = np.log(I0_w2/OD2[i])
#print(OD2)

print(oxy)




        

