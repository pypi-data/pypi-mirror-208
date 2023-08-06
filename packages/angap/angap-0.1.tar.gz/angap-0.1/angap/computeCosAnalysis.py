from parseRiseSetTimeFile import *
from findMaxGapTime import *
from findPPDBothMethods import *
import numpy as np
import matplotlib.pyplot as plt
from parseRiseSetTimeFile import *
import glob
import shelve

E_CON = ConstantsStruct()

## READ IN RISE/SET TIME CSVs AND COMPUTE MAX GAP TIME.
files_to_parse = glob.glob("Rise-Set Report View 975-*")

lat_table = []
alt_inc_el_table = []
ppd_table = []
for f in files_to_parse:
    mgt, lat, acc, ppd, mpt = parseRiseSetTimeFile(f)
    alt,inc,el = parseFileName(f)
    lat_table.append(lat)
    alt_inc_el_table.append([alt,inc,el])
    ppd_table.append(ppd)

inc_lat_alt_el_ppdSOAP_ppdUSMA_ppdOURS_table = []
for i in range(len(ppd_table)):
    for j in range(len(ppd_table[i])):
        alt = alt_inc_el_table[i][0]
        inc = alt_inc_el_table[i][1]
        el = alt_inc_el_table[i][2]
        lat = lat_table[i][j]

        if(inc<90):
            if(lat>inc):
                ppd_soap = ppd_table[i][j]
                ppd_usma = findPPDBothMethods(np.array([lat]),inc,alt,el,E_CON,True)
                ppd_ours = findPPDBothMethods(np.array([lat]),inc,alt,el,E_CON,False)
                inc_lat_alt_el_ppdSOAP_ppdUSMA_ppdOURS_table.append([inc,lat,alt,el,ppd_soap,ppd_usma[0],ppd_ours[0]])
        else:
            if(lat>(180-inc)):
                ppd_soap = ppd_table[i][j]
                ppd_usma = findPPDBothMethods(np.array([lat]),inc,alt,el,E_CON,True)
                ppd_ours = findPPDBothMethods(np.array([lat]),inc,alt,el,E_CON,False)
                inc_lat_alt_el_ppdSOAP_ppdUSMA_ppdOURS_table.append([inc,lat,alt,el,ppd_soap,ppd_usma[0],ppd_ours[0]])

for i in inc_lat_alt_el_ppdSOAP_ppdUSMA_ppdOURS_table:
    print(i)

vars_to_save = [
    'inc_lat_alt_el_ppdSOAP_ppdUSMA_ppdOURS_table'
]

filename='shelve_cos_analysis.out'
my_shelf = shelve.open(filename,'n') # 'n' for new

for key in vars_to_save:
    my_shelf[key] = globals()[key]

my_shelf.close()