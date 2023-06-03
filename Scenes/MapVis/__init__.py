import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtWidgets, uic, QtCore, QtGui
import os
from Scenes import DAATAScene

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import numpy as np
import random as rand

from DataAcquisition import data

uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'MapVis.ui'))  # loads the .ui file from QT Desginer

# Set coordinate bounds of map
# TODO: Add in dynamic bounds
boundsBox = [45.6280, 45.6361, (-122.2587), (-122.2491)]

# Set image path
image_path = './Scenes/MapVis/'
image_name = 'WashougalMap.png'

DEBUG = False

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, fig : Figure):
        global boundsBox

        # Read downloaded map image using boundsBox coordinates
        image = plt.imread(image_path + image_name)
        
        self.axes = fig.add_subplot(111)

        # fig.figimage(image, resize=True, xo=corners[0][0], yo=corners[0][1])

        self.axes.imshow(image, zorder=0, extent = boundsBox, aspect= 'equal')

        self.axes.set_title('Plotting Spatial Data on Washougal Map')
        self.axes.set_xlim(xmin=boundsBox[0],xmax=boundsBox[1])
        self.axes.set_ylim(ymin=boundsBox[2],ymax=boundsBox[3])
        self.axes.set_autoscale_on(False)
        # self.axes.set_aspect(aspect='equal')
        self.axes.set_axis_off()
        # self.axes.set_xmargin(0)
        # self.axes.set_ymargin(0)

        super(MplCanvas, self).__init__(fig)

class MapVis(DAATAScene, uiFile):
    def __init__(self):
        global boundsBox

        self.showInit = True
        super().__init__()

        self.fig = Figure(figsize=(8, 7), dpi=100)
        self.sc = MplCanvas(self.fig)

        # Make a test middle point on the map
        self.latPoint = prevLatPoint = (boundsBox[0] + boundsBox[1]) / 2
        self.longPoint = prevLongPoint = (boundsBox[2] + boundsBox[3]) / 2

        self.prevLatPoint, self.prevLongPoint = 0, 0
        self.x, self.y = [],[]
        self.x.append(self.prevLatPoint)
        self.y.append(self.prevLongPoint)

        self.sc.axes.scatter(self.x,self.y)

        self.layoutMAT = QtWidgets.QVBoxLayout()
        self.layoutMAT.addWidget(self.sc)

        self.setLayout(self.layoutMAT)

        self.colors = []
        for i in range(100):
            self.x.append(0)
            self.y.append(0)
            self.colors.append([rand.random(), rand.random(), rand.random()])

        # Create the figure and start the animation
        self.hide()
        self.update_period = 10  # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)
        self.ani = FuncAnimation(self.fig, self.animate, frames=2, interval=self.update_period * 10, repeat=True)

    def update_active(self):
        if self.showInit:
            self.ani.resume()
            self.showInit = False
            if (DEBUG): 
                print("Animation Resumed")
        

    def update_passive(self):
        if not self.showInit and not self.isVisible():
            self.ani.pause()
            self.showInit = True
            if (DEBUG): 
                print("Animation Paused")

    def animate(self, i):
        if data.get_current_value("gps_lattitude") is not None:
            self.latPoint = (data.get_current_value("gps_lattitude") / 10000000)
        if data.get_current_value("gps_longitude") is not None:
            self.longPoint = (data.get_current_value("gps_longitude") / 100000000) - 152.976691

        self.x.append(self.latPoint)
        self.y.append(self.longPoint)
        while len(self.y) > 100:
            self.y.pop(0)
            self.x.pop(0)

        self.prevLatPoint = self.latPoint
        self.prevLongPoint = self.longPoint
        # self.sc.axes
        self.sc.axes.scatter(self.x,self.y, c=self.colors)