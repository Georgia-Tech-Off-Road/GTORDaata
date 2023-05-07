import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

boundsBox = [44.09426, 44.08128, -88.53080, -88.51538]
oshkosh_m = plt.imread('c:/Users/samue/Downloads/map.png')

fig, ax = plt.subplots(figsize = (8,7))
ax.set_title('Plotting Spatial Data on Oshkosh Map')
ax.set_xlim(boundsBox[0],boundsBox[1])
ax.set_ylim(boundsBox[2],boundsBox[3])
ax.imshow(oshkosh_m, zorder=0, extent = boundsBox, aspect= 'equal')

latPoint = 44.08626
longPoint = -88.52080
ax.scatter(latPoint, longPoint, zorder=1, alpha= 1, c='r', s=10)

plt.show()