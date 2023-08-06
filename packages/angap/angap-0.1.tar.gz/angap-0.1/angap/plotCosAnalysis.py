import matplotlib.pyplot as plt
from findPPDBothMethods import *
from findMaxGapTime import *
import numpy as np
import glob
import shelve

# inc = np.array([0,0,10,10,20,20,30,30,40,40,50,50,60,60,70,70,80,100,110,110,120,120,130,130,140,140,150,150,160,160,170,170])
# lat = np.array([10,20,20,30,30,40,40,50,50,60,60,70,70,80,80,90,90,90,80,90,70,80,60,70,50,60,40,50,30,40,20,30])
# soap = np.array([12.89,12.83,7.19,2.40,5.03,1.86,4.41,1.72,4.27,1.76,4.52,2.00,5.29,2.70,7.75,13.79,13.84,13.84,7.87,
#                  13.79,5.51,14.00,4.83,2.10,4.67,1.90,4.92,1.89,5.71,2.09,8.06,5.71])
# alt = 440.0
# el = 5.0
# E_CON = ConstantsStruct()
#
#
# ppd_array = np.zeros((2,len(inc)))
# #for i in range(len(inc)):
# #    ppd_cos = findPPDBothMethods(np.array([lat[i]]), inc[i], alt, el, E_CON, True)
# #    ppd_new = findPPDBothMethods(np.array([lat[i]]), inc[i], alt, el, E_CON, False)
# #
# #    ppd_array[0,i] = ppd_cos
# #    ppd_array[1,i] = ppd_new
# ppd_cos = [12.75,12.75,7.20,2.49,5.00,1.88,4.35,1.71,4.20,1.72,4.42,1.93,5.17,2.59,7.56,13.41,13.58,13.93,7.95,14.10,5.56,
#            14.25,4.86,2.11,4.70,1.92,4.93,1.94,5.73,2.16,8.31,'-inf']
# ppd_new = [12.77,12.81,7.23,2.52,5.03,1.91,4.38,1.74,4.24,1.75,4.47,1.97,5.23,2.65,7.66,13.75,13.75,13.75,7.86,13.75,5.50,
#            13.93,4.81,2.07,4.66,1.89,4.90,1.91,5.70,2.13,8.29,'-inf']
# ppd_array[0,:] = ppd_cos
# ppd_array[1,:] = ppd_new
# print(len(ppd_cos))

# import ppds
filename='shelve_cos_analysis.out'
my_shelf = shelve.open(filename)
for key in my_shelf:
    globals()[key]=my_shelf[key]
my_shelf.close()

inc = []
lat = []
alt = []
el = []
ppd_array = np.zeros((2,len(inc_lat_alt_el_ppdSOAP_ppdUSMA_ppdOURS_table)))
soap = np.zeros((1,len(inc_lat_alt_el_ppdSOAP_ppdUSMA_ppdOURS_table)))

for p_idx,p in enumerate(inc_lat_alt_el_ppdSOAP_ppdUSMA_ppdOURS_table):
    inc.append(p[0])
    lat.append(p[1])
    alt.append(p[2])
    el.append(p[3])
    soap[0,p_idx] = p[4]
    ppd_array[0,p_idx] = p[5]
    ppd_array[1,p_idx] = p[6]

# create labels
labels=[]
for i in range(len(inc)):
    labels.append('i='+str(inc[i])+'$\degree$, $\lambda^\prime$='+str(lat[i])+'$\degree$')

plt.figure(figsize=(10,4))
plt.plot(np.linspace(0,len(inc)-1,len(inc)),np.transpose(soap[0,:])-ppd_array[1,:],'b*',np.linspace(0,len(inc)-1,len(inc)),np.transpose(soap[0,:])-ppd_array[0,:],'r*')
plt.legend(['Error from SOAP using Eq. 28','Error from SOAP using cos(i)'])
plt.ylabel('Error (PPD)')
plt.xticks(np.linspace(0,len(inc)-1,len(inc)), labels, rotation='vertical')
plt.subplots_adjust(bottom=0.3)
plt.tight_layout()
plt.grid()
plt.show()

print('ours',np.sqrt(((soap[0,:] - ppd_array[1,:]) ** 2).mean()))
print('usma',np.sqrt(((soap[0,:] - ppd_array[0,:]) ** 2).mean()))
