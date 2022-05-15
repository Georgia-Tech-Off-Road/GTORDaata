from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QPalette
import os

import pyqtgraph as pg
from functools import partial
import DataAcquisition
from DataAcquisition import data
from DataAcquisition import data_import
from Utilities.CustomWidgets.Plotting import CustomPlotWidget, GridPlotLayout
from Scenes import DAATAScene
import logging
from datetime import datetime

from stl import mesh
import sys
import numpy as np
from pyqtgraph.opengl import GLViewWidget, MeshData, GLMeshItem
import math

# Default plot configuration for pyqtgraph
pg.setConfigOption('background', 'w')   # white
pg.setConfigOption('foreground', 'k')   # black

# load the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), '3d_viewer.ui'))

logger = logging.getLogger("Viewer3D")


class Viewer3D(DAATAScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.hide()

        self.update_period = 5  # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)

        self.is_sensors_attached = False
        self.load_cell_taring = False

        self.connect_slots_and_signals()
        self.configFile = QSettings('DAATA', 'data_collection')

        self.slot_select_imu()
        self.view = GLViewWidget()
        self.graph_layout.addWidget(self.view)
        self.gl_mesh = None
        self.prev_angle = [-90, 1, 0, 0]

        self.create_viewer()

    def create_viewer(self):
        """
        This function will generate the 3D viewer window

        :return: None
        """
        stl_mesh = mesh.Mesh.from_file('Scenes/Viewer3D/ChassisV3.STL')

        points = stl_mesh.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)

        mesh_data = MeshData(vertexes=points, faces=faces)
        self.gl_mesh = GLMeshItem(meshdata=mesh_data, smooth=True, drawFaces=False, drawEdges=True, edgeColor=(0, 1, 0, 1))
        self.view.addItem(self.gl_mesh)

        self.gl_mesh.scale(0.002, 0.002, 0.002)

        self.view.show()

    def __reset_all(self):
        # NOTE: If this Python file doesn't work, try commenting these two lines
        # -Faris
        data.reset_hard()

    def quaternion_to_axisangle(self, qx, qy, qz, qw):
        try:
            axis_angle = [0, 0, 0, 0]
            axis_angle[0] = 180 / math.pi * 2 * math.acos(qw)  # angle
            axis_angle[1] = qx / math.sqrt(1 - qw ** 2)
            axis_angle[3] = qy / math.sqrt(1 - qw ** 2)
            axis_angle[2] = qz / math.sqrt(1 - qw ** 2)
        except ZeroDivisionError:
            axis_angle = [0, 1, 0, 0]
            logger.error("Divide by zero in quaternion_to_axisangle")
        return axis_angle

    def slot_select_imu(self):
        logger.info("Changing imu input for 3D viewer")
        pass

    def update_viewer(self):
        """
        This function will update the 3D viewer based on the IMU angle that is received

        :return:
        """
        #logger.debug("Updating viewer")
        #self.gl_mesh.rotate(10, 1, 0, 0)
        qw = data.get_current_value("dashboard_quaternion_1")
        qx = data.get_current_value("dashboard_quaternion_2")
        qy = data.get_current_value("dashboard_quaternion_3")
        qz = data.get_current_value("dashboard_quaternion_4")
        angle = self.quaternion_to_axisangle(qx, qy, qz, qw)
        print(angle)
        self.gl_mesh.rotate(-self.prev_angle[0], self.prev_angle[1], self.prev_angle[2], self.prev_angle[3])
        self.prev_angle = angle
        self.gl_mesh.rotate(angle[0], angle[1], angle[2], angle[3])

    def update_active(self):
        """
        This function will update only if the Data Collection tab is the current tab. This function will get called
        at whatever frequency self.update_freq is set at. It is called via the update_all function from the
        MainWindow.

        :return: None
        """
        if self.accel_x_lcd.isEnabled():
            self.accel_x_lcd.display(data.get_current_value("dashboard_accel_x"))
        if self.accel_y_lcd.isEnabled():
            self.accel_y_lcd.display(data.get_current_value("dashboard_accel_y"))
        if self.accel_z_lcd.isEnabled():
            self.accel_z_lcd.display(data.get_current_value("dashboard_accel_z"))

        # TODO If imu is connected then update 3D viewer based on imu angle
        if data.get_is_connected("dashboard_quaternion_1"):
            self.update_viewer()
        #self.update_viewer()

    def update_passive(self):
        """
        This funciton with check if an imu is connected. If so, then enable the lcds. Also check for new imu sensors
        that are connected.

        :return:
        """
        # Enable or disable the lcd displays based on what sensors are connected
        if data.get_is_connected("dashboard_accel_x"):
            self.accel_x_lcd.setEnabled(True)
        else:
            self.accel_x_lcd.setEnabled(False)

        if data.get_is_connected("dashboard_accel_y"):
            self.accel_y_lcd.setEnabled(True)
        else:
            self.accel_y_lcd.setEnabled(False)

        if data.get_is_connected("dashboard_accel_z"):
            self.accel_z_lcd.setEnabled(True)
        else:
            self.accel_z_lcd.setEnabled(False)

        pass


    def connect_slots_and_signals(self):
        # TODO: connect the dropdown box with updating which imu is controlling the 3D viewer
        self.imu_combobox.activated.connect(self.slot_select_imu)


    # --- Overridden event methods --- #
    def closeEvent(self):
        self.window().setWindowTitle('closed tab')

    def paintEvent(self, pe):
        """
        This method allows the color scheme of the class to be changed by CSS stylesheets

        :param pe:
        :return: None
        """
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()
        s.drawPrimitive(QtGui.QStyle.PE_Widget, opt, p, self)
