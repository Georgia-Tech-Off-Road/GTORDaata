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

import sys
import numpy as np
from pyqtgraph.opengl import GLViewWidget, MeshData, GLMeshItem

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

        self.create_viewer()

    def create_viewer(self):
        """
        This function will generate the 3D viewer window

        :return: None
        """
        print(os.getcwd())
        from stl import mesh
        stl_mesh = mesh.Mesh.from_file('Scenes/Viewer3D/topBoxV2.STL')

        points = stl_mesh.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)

        mesh_data = MeshData(vertexes=points, faces=faces)
        mesh = GLMeshItem(meshdata=mesh_data, smooth=True, drawFaces=False, drawEdges=True, edgeColor=(0, 1, 0, 1))
        self.view.addItem(mesh)

        self.view.show()

    def __reset_all(self):
        # NOTE: If this Python file doesn't work, try commenting these two lines
        # -Faris
        data.reset_hard()

    def slot_select_imu(self):
        logger.info("Changing imu input for 3D viewer")
        pass

    def update_viewer(self):
        """
        This function will update the 3D viewer based on the IMU angle that is received

        :return:
        """
        pass

    def update_active(self):
        """
        This function will update only if the Data Collection tab is the current tab. This function will get called
        at whatever frequency self.update_freq is set at. It is called via the update_all function from the
        MainWindow.

        :return: None
        """
        if self.accel_x_lcd.isEnabled():
            self.accel_x_lcd.display(data.get_current_value("dyno_engine_speed"))
        if self.accel_y_lcd.isEnabled():
            self.accel_y_lcd.display(data.get_current_value("dyno_secondary_speed"))
        if self.accel_z_lcd.isEnabled():
            self.accel_z_lcd.display(data.get_current_value("force_enginedyno_lbs"))

        # TODO If imu is connected then update 3D viewer based on imu angle
        pass

    def update_passive(self):
        """
        This funciton with check if an imu is connected. If so, then enable the lcds. Also check for new imu sensors
        that are connected.

        :return:
        """
        # Enable or disable the lcd displays based on what sensors are connected
        if data.get_is_connected("dyno_engine_speed"):
            self.accel_x_lcd.setEnabled(True)
        else:
            self.accel_x_lcd.setEnabled(False)

        if data.get_is_connected("dyno_secondary_speed"):
            self.accel_y_lcd.setEnabled(True)
        else:
            self.accel_y_lcd.setEnabled(False)

        if data.get_is_connected("force_enginedyno_lbs"):
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
