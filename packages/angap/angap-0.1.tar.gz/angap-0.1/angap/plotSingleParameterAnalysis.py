import matplotlib.pyplot as plt
from findPPDBothMethods import *
from findMaxGapTime import *
import numpy as np

lat = np.linspace(0,90,901)
alt = 400.0
el = 5.0
inc = 20.0
E_CON = ConstantsStruct()

mgt,val,ppd,mpt = findMaxGapTime(lat, inc, alt, el, E_CON)

fig, ax1 = plt.subplots()
ax1.plot(lat,mgt/3600, 'b-')
ax1.set_xlabel('Latitude ($\degree$)')
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('Max Gap Time (hr)', color='b')
ax1.tick_params('y', colors='b')

ax2 = ax1.twinx()
ax2.plot(lat, ppd, 'r-')
ax2.set_ylabel('Passes Per Day', color='r')
ax2.tick_params('y', colors='r')

ax3 = ax1.twinx()
fig.subplots_adjust(right=0.62)
ax3.spines['right'].set_position(('axes',1.2))
ax3.set_frame_on(True)
ax3.patch.set_visible(False)
ax3.plot(lat, mpt/60, 'g-')
ax3.set_ylabel('Mean Pass Time (min)', color='g')
ax3.tick_params('y', colors='g')

ax4 = ax1.twinx()
ax4.spines['right'].set_position(('axes',1.35))
ax4.set_frame_on(True)
ax4.patch.set_visible(False)
ax4.plot(lat, np.multiply(mpt,ppd)/60, 'k-')
ax4.set_ylabel('Mean Coverage Per Day (min)', color='k')
ax4.tick_params('y', colors='k')

ax1.set_yticks(np.linspace(ax1.get_yticks()[0],ax1.get_yticks()[-1],len(ax1.get_yticks())))
ax2.set_yticks(np.linspace(ax2.get_yticks()[0],ax2.get_yticks()[-1],len(ax1.get_yticks())))
ax3.set_yticks(np.linspace(ax3.get_yticks()[0],ax3.get_yticks()[-1],len(ax1.get_yticks())))
ax4.set_yticks(np.linspace(ax4.get_yticks()[0],ax4.get_yticks()[-1],len(ax1.get_yticks())))
plt.locator_params(axis='x',nticks=10)

#fig.tight_layout()
plt.grid()
plt.show()