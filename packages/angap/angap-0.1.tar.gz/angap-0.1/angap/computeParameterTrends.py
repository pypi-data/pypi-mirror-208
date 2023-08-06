from findMaxGapTime import *
import numpy as np
import matplotlib.pyplot as plt
from parseRiseSetTimeFile import *
import glob
import shelve

E_CON = ConstantsStruct()
# One Parameter Analysis
i_base = 87.0
alt_base = 400.0
el_base = 5.0
lat_base = 50.0*np.ones((1,1))

# Varying Altitude
alt = np.linspace(200,2000,int((2000-200)/10+1))
mgt_f_of_alt = np.zeros(alt.shape)
ppd_f_of_alt = np.zeros(alt.shape)
mpt_f_of_alt = np.zeros(alt.shape)
val_ar_f_of_alt = np.zeros(alt.shape)
for i in range(len(alt)):
    mgt,val,ppd,mpt = findMaxGapTime(lat_base,i_base,alt[i],el_base,E_CON)
    mgt_f_of_alt[i] = mgt
    val_ar_f_of_alt[i] = val
    ppd_f_of_alt[i] = ppd
    mpt_f_of_alt[i] = mpt

# Varying Inclination
inc = np.linspace(0,180,1801)
mgt_f_of_inc = np.zeros(inc.shape)
ppd_f_of_inc = np.zeros(inc.shape)
mpt_f_of_inc = np.zeros(inc.shape)
val_ar_f_of_inc = np.zeros(inc.shape)
for i in range(len(inc)):
    mgt,val,ppd,mpt = findMaxGapTime(lat_base,inc[i],alt_base,el_base,E_CON)
    mgt_f_of_inc[i] = mgt
    ppd_f_of_inc[i] = ppd
    mpt_f_of_inc[i] = mpt
    val_ar_f_of_inc[i] = val

# Varying Elevation Angle
el = np.linspace(0,25,251)
mgt_f_of_el = np.zeros(el.shape)
ppd_f_of_el = np.zeros(el.shape)
mpt_f_of_el = np.zeros(el.shape)
val_ar_f_of_el = np.zeros(el.shape)
for i in range(len(el)):
    mgt,val,ppd,mpt = findMaxGapTime(lat_base,i_base,alt_base,el[i],E_CON)
    mgt_f_of_el[i] = mgt
    ppd_f_of_el[i] = ppd
    mpt_f_of_el[i] = mpt
    val_ar_f_of_el[i] = val

# run analytical solution
lat = np.linspace(0.0,90.0,901)
val_ar_f_of_lat = np.zeros(lat.shape)
mgt_f_of_lat,val_ar_f_of_lat,ppd_f_of_lat,mpt_f_of_lat = findMaxGapTime(lat,i_base,alt_base,el_base,E_CON)

# Two Parameter Analysis
# el/inc
el = np.linspace(0,25,51)
inc = np.linspace(0,180,361)
mgt_f_of_el_inc = np.zeros((len(el),len(inc)))
ppd_f_of_el_inc = np.zeros((len(el),len(inc)))
mpt_f_of_el_inc = np.zeros((len(el),len(inc)))
val_ar_f_of_el_inc = np.zeros((len(el),len(inc)))
for i in range(len(el)):
    for j in range(len(inc)):
        mgt,val,ppd,mpt = findMaxGapTime(lat_base, inc[j], alt_base, el[i], E_CON)
        mgt_f_of_el_inc[i,j] = mgt
        ppd_f_of_el_inc[i,j] = ppd
        mpt_f_of_el_inc[i,j] = mpt
        val_ar_f_of_el_inc[i,j] = val

# el/alt NEED TO HAVE IT NOT PLOT FOR CASES WHERE SWATHS DON'T OVERLAP
el = np.linspace(0,25,51)
alt = np.linspace(200,2000,int((2000-200)/10+1))
mgt_f_of_el_alt = np.zeros((len(el),len(alt)))
ppd_f_of_el_alt = np.zeros((len(el),len(alt)))
mpt_f_of_el_alt = np.zeros((len(el),len(alt)))
val_ar_f_of_el_alt = np.zeros((len(el),len(alt)))
for i in range(len(el)):
    for j in range(len(alt)):
        mgt,val,ppd,mpt = findMaxGapTime(lat_base, i_base, alt[j], el[i], E_CON)
        mgt_f_of_el_alt[i,j] = mgt
        ppd_f_of_el_alt[i,j] = ppd
        mpt_f_of_el_alt[i,j] = mpt
        val_ar_f_of_el_alt[i,j] = val

# el/lat
el = np.linspace(0,25,51)
lat = np.linspace(0.0,90.0,181)
mgt_f_of_el_lat = np.zeros((len(el),len(lat)))
ppd_f_of_el_lat = np.zeros((len(el),len(lat)))
mpt_f_of_el_lat = np.zeros((len(el),len(lat)))
val_ar_f_of_el_lat = np.zeros((len(el),len(lat)))
for i in range(len(el)):
    for j in range(len(lat)):
        mgt,val,ppd,mpt = findMaxGapTime(lat[j]*np.ones((1,1)), i_base, alt_base, el[i], E_CON)
        mgt_f_of_el_lat[i,j] = mgt
        ppd_f_of_el_lat[i,j] = ppd
        mpt_f_of_el_lat[i,j] = mpt
        val_ar_f_of_el_lat[i,j] = val

# inc/lat
inc = np.linspace(0,180,361)
lat = np.linspace(0.0,90.0,181)
mgt_f_of_inc_lat = np.zeros((len(inc),len(lat)))
ppd_f_of_inc_lat = np.zeros((len(inc),len(lat)))
mpt_f_of_inc_lat = np.zeros((len(inc),len(lat)))
val_ar_f_of_inc_lat = np.zeros((len(inc),len(lat)))
for i in range(len(inc)):
    for j in range(len(lat)):
        mgt,val,ppd,mpt = findMaxGapTime(lat[j]*np.ones((1,1)), inc[i], alt_base, el_base, E_CON)
        mgt_f_of_inc_lat[i,j] = mgt
        ppd_f_of_inc_lat[i,j] = ppd
        mpt_f_of_inc_lat[i,j] = mpt
        val_ar_f_of_inc_lat[i,j] = val

# inc/alt
inc = np.linspace(0,180,361)
alt = np.linspace(200,2000,int((2000-200)/10+1))
mgt_f_of_inc_alt = np.zeros((len(inc),len(alt)))
ppd_f_of_inc_alt = np.zeros((len(inc),len(alt)))
mpt_f_of_inc_alt = np.zeros((len(inc),len(alt)))
val_ar_f_of_inc_alt = np.zeros((len(inc),len(alt)))
for i in range(len(inc)):
    for j in range(len(alt)):
        mgt,val,ppd,mpt = findMaxGapTime(lat_base, inc[i], alt[j], el_base, E_CON)
        mgt_f_of_inc_alt[i,j] = mgt
        ppd_f_of_inc_alt[i,j] = ppd
        mpt_f_of_inc_alt[i,j] = mpt
        val_ar_f_of_inc_alt[i,j] = val

# alt/lat
alt = np.linspace(200,2000,int((2000-200)/10+1))
lat = np.linspace(0.0,90.0,181)
mgt_f_of_alt_lat = np.zeros((len(alt),len(lat)))
ppd_f_of_alt_lat = np.zeros((len(alt),len(lat)))
mpt_f_of_alt_lat = np.zeros((len(alt),len(lat)))
val_ar_f_of_alt_lat = np.zeros((len(alt),len(lat)))
for i in range(len(alt)):
    for j in range(len(lat)):
        mgt,val,ppd,mpt = findMaxGapTime(lat[j]*np.ones((1,1)), i_base, alt[i], el_base, E_CON)
        mgt_f_of_alt_lat[i,j] = mgt
        ppd_f_of_alt_lat[i,j] = ppd
        mpt_f_of_alt_lat[i,j] = mpt
        val_ar_f_of_alt_lat[i,j] = val

filename='shelve_2d.out'
my_shelf = shelve.open(filename,'n') # 'n' for new

vars_to_save = [
    'mgt_f_of_alt',
    'ppd_f_of_alt',
    'mpt_f_of_alt',
    'val_ar_f_of_alt',

    'mgt_f_of_inc',
    'ppd_f_of_inc',
    'mpt_f_of_inc',
    'val_ar_f_of_inc',

    'mgt_f_of_el',
    'ppd_f_of_el',
    'mpt_f_of_el',
    'val_ar_f_of_el',

    'mgt_f_of_lat',
    'ppd_f_of_lat',
    'mpt_f_of_lat',
    'val_ar_f_of_lat',

    'mgt_f_of_el_inc',
    'ppd_f_of_el_inc',
    'mpt_f_of_el_inc',
    'val_ar_f_of_el_inc',

    'mgt_f_of_el_alt',
    'ppd_f_of_el_alt',
    'mpt_f_of_el_alt',
    'val_ar_f_of_el_alt',

    'mgt_f_of_el_lat',
    'ppd_f_of_el_lat',
    'mpt_f_of_el_lat',
    'val_ar_f_of_el_lat',

    'mgt_f_of_inc_lat',
    'ppd_f_of_inc_lat',
    'mpt_f_of_inc_lat',
    'val_ar_f_of_inc_lat',

    'mgt_f_of_inc_alt',
    'ppd_f_of_inc_alt',
    'mpt_f_of_inc_alt',
    'val_ar_f_of_inc_alt',

    'mgt_f_of_alt_lat',
    'ppd_f_of_alt_lat',
    'mpt_f_of_alt_lat',
    'val_ar_f_of_alt_lat']

for key in vars_to_save:
    my_shelf[key] = globals()[key]

my_shelf.close()