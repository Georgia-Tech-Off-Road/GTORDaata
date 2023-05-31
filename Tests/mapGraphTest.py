import matplotlib.pyplot as plt
import matplotlib.animation
import numpy as np

import sys
sys.path.append('..')

from DataAcquisition import data

# Set coordinate bounds of map
boundsBox = [44.09426, 44.08128, -88.53080, -88.51538]
# Make a test middle point on the map
latPoint = prevLatPoint = (boundsBox[0] + boundsBox[1]) / 2
longPoint = prevLongPoint = (boundsBox[2] + boundsBox[3]) / 2
# Read downloaded map image using boundsBox coordinates
oshkosh_m = plt.imread('WashougalMap.png')

fig, ax = plt.subplots(figsize = (8,7))
ax.imshow(oshkosh_m, zorder=0, extent = boundsBox, aspect= 'equal')
ax.set_title('Plotting Spatial Data on Washougal Map')
ax.set_xlim(boundsBox[0],boundsBox[1])
ax.set_ylim(boundsBox[2],boundsBox[3])
x, y = [],[]
x.append(prevLatPoint)
y.append(prevLongPoint)
sc = ax.scatter(x,y)

def animate(i):
    global latPoint
    global prevLatPoint
    global longPoint
    global prevLongPoint

    latPoint = data.get_current_value("gps_lattitude")
    longPoint = data.get_current_value("gps_longitude")

    if ((latPoint != prevLatPoint) or (longPoint != prevLongPoint)):
        x.clear()
        y.clear()
        x.append(latPoint)
        y.append(longPoint)
        sc.set_offsets(np.c_[x,y])
        prevLatPoint = latPoint
        prevLongPoint = longPoint
#        plt.pause(0.5)

ani = matplotlib.animation.FuncAnimation(fig, animate, frames=2, interval=100, repeat=True) 
plt.show()