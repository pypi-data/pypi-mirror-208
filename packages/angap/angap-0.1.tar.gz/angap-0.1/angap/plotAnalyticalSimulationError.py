from findMaxGapTime import *
import numpy as np
import matplotlib.pyplot as plt
from parseRiseSetTimeFile import *
import glob
import shelve

filename='shelve_error.out'
my_shelf = shelve.open(filename)
for key in my_shelf:
    globals()[key]=my_shelf[key]
my_shelf.close()

mgt_rel_error = []
for i in range(len(rel_error)):
    if(np.abs(rel_error[i]) < 0.50):
        mgt_rel_error.append(rel_error[i])
mgt_main_error_median = np.nanmedian(np.array(mgt_rel_error))
mgt_main_error_std = np.std(np.array(mgt_rel_error))
print('MGT_MEDIAN: '+str(mgt_main_error_median))
print('MGT_STD: '+str(mgt_main_error_std))

mpt_error_median = np.nanmedian(np.array(mpt_error))
mpt_error_std = np.nanstd(np.array(mpt_error))
print('MPT_MEDIAN: '+str(mpt_error_median))
print('MPT_STD: '+str(mpt_error_std))

ppd_error_median = np.nanmedian(np.array(ppd_error))
ppd_error_std = np.nanstd(np.ma.masked_invalid(ppd_error))
print('PPD_MEDIAN: '+str(ppd_error_median))
print('PPD_STD: '+str(ppd_error_std))

plt.figure()
plt.hist(100*np.array(rel_error),400,(-110,110))
plt.xlabel('Maximum Gap Time Error (Percent of an Orbit Revolution)')
plt.ylabel('Counts')
plt.show()

plt.figure()
plt.hist(rel_error_lat,20,(0,2.00))
plt.xlabel('Maximum Gap Time Latitude Error (Degrees)')
plt.ylabel('Counts')
plt.show()

plt.figure()
plt.hist(100*np.array(ppd_error),400,(-50,50))
plt.xlabel('Passes Per Day Percent Error')
plt.ylabel('Counts')
plt.show()

plt.figure()
plt.hist(100*np.array(mpt_error),400,(-2,2))
plt.xlabel('Mean Pass Time Error (Percent of an Orbit Revolution)')
plt.ylabel('Counts')
plt.show()