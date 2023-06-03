import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtWidgets, uic, QtCore, QtGui
import os
from Scenes import DAATAScene

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation
import numpy as np
import math as m

from DataAcquisition import data

DEBUG = False

uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'AccVis.ui'))  # loads the .ui file from QT Desginer

def Rx(theta):
    return np.matrix([[1, 0, 0],
                      [0, m.cos(theta), -m.sin(theta)],
                      [0, m.sin(theta), m.cos(theta)]])

def Ry(theta):
    return np.matrix([[m.cos(theta), 0, m.sin(theta)],
                      [0, 1, 0],
                      [-m.sin(theta), 0, m.cos(theta)]])

def Rz(theta):
    return np.matrix([[m.cos(theta), -m.sin(theta), 0],
                      [m.sin(theta), m.cos(theta), 0],
                      [0, 0, 1]])

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, fig):
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class AccVis(DAATAScene, uiFile):
    def __init__(self):
        self.showInit = True
        super().__init__()

        # self.setupUi(self)

        self.fig = Figure(figsize=(4, 4), dpi=100)
        self.sc = MplCanvas(self.fig)
        
        # self.cube_pos = [0, 0, 0]
        self.cube_vert = [[1, 1, 1], 
                          [-1, -1, -1],
                          [1, 1, -1],
                          [1, -1, 1],
                          [1, -1, -1],
                          [-1, 1, 1],
                          [-1, -1, 1],
                          [-1, 1, -1]]
        self.cube_vel = [0, 0, 0]
        self.cube_size = 1

        self.layoutMAT = QtWidgets.QVBoxLayout()
        self.layoutMAT.addWidget(self.sc)

        self.setLayout(self.layoutMAT)
            

        # Create the figure and start the animation
        self.hide()
        self.update_period = 3  # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)
        self.ani = matplotlib.animation.FuncAnimation(self.fig, self.animate, interval=self.update_period * 20)
        self.ani.pause()

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
        self.update_cube(i)

    def update_cube(self, i):
        # Get the acceleration data for this time step
        ax = data.get_current_value("imu_gyro_x")
        if (ax is None):
            ax = 0
        ay = data.get_current_value("imu_gyro_y")
        if (ay is None):
            ay = 0
        az = data.get_current_value("imu_gyro_z") 
        if (az is None):
            az = 0

        if DEBUG:
            print("AX:", ax)
            print("AY:", ay)
            print("AZ:", az, "\n")
        
        # Update the cube position based on the acceleration data
        self.cube_vel[0] += ax * self.update_period * 10 / 1000
        self.cube_vel[1] += ay * self.update_period * 10 / 1000
        self.cube_vel[2] += az * self.update_period * 10 / 1000

        # self.cube_pos[0] += self.cube_vel[0] * self.update_period * 10 / 1000
        # self.cube_pos[1] += self.cube_vel[1] * self.update_period * 10 / 1000
        # self.cube_pos[2] += self.cube_vel[2] * self.update_period * 10 / 1000

        rotation_matrix = np.dot(np.dot(Rx(self.cube_vel[0]), Ry(self.cube_vel[1])), Rz(self.cube_vel[2]))

        for vertex_num in range(len(self.cube_vert)):
            for vel in self.cube_vel:
                self.cube_vert[vertex_num] = np.dot(self.cube_vert[vertex_num], rotation_matrix)

        
        # Def1ine the 12 edges of the cube
        edges = np.array([
            [0, 1], [1, 2], [2, 3], [3, 0],
            [4, 5], [5, 6], [6, 7], [7, 4],
            [0, 4], [1, 5], [2, 6], [3, 7]
        ])
        
        # Plot the cube
        ax = self.fig.add_subplot(projection='3d')
        ax.clear()
        ax.set_xlim([-10, 10])
        ax.set_ylim([-10, 10])
        ax.set_zlim([-10, 10])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('IMU Cube Demo')
        for vert in self.cube_vert:
            ax.scatter(vert[0], vert[1], vert[2], marker=m)
        
        # Return the plot
        return ax
    
    def closeEvent(self):
        self.ani.pause()
        if (DEBUG): 
            print("Closing Tab")