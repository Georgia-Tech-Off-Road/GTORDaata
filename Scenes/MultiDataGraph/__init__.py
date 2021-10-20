from enum import Enum

from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QPalette
import os

import pyqtgraph as pg
from functools import partial
import DataAcquisition
from DataAcquisition import data
from Utilities.CustomWidgets.Plotting import CustomPlotWidget, GridPlotLayout
from Scenes import DAATAScene
import logging

# Default plot configuration for pyqtgraph
pg.setConfigOption('background', 'w')   # white
pg.setConfigOption('foreground', 'k')   # black

# load the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'MultiDataGraph.ui'))

logger = logging.getLogger("MultiDataGraph")

# Todo List      ####################################
# add warning dialog if trying to start recording data while teensy is not plugged in (checked with data.is_connected)


class MultiDataGraph(DAATAScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.hide()

        # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)
        self.update_period = 3

        self.graph_objects = dict()
        # self.checkbox_objects = dict()
        # self.currentKeys = data.get_sensors(is_plottable=True)
        # TODO change this to all connected sensors
        self.connected_sensors = []
        self.update_connected_sensors()
        self.y_sensors = []

        self.line_graph = "line_graph"
        self.scatter_plot = "scatter_plot"

        self.gridPlotLayout = GridPlotLayout(self.scrollAreaWidgetContents)
        self.gridPlotLayout.setObjectName("gridPlotLayout")
        self.scrollAreaWidgetContents.setLayout(self.gridPlotLayout)

        self.create_graph_dimension_combo_box()
        self.create_graph(0)
        # self.create_grid_plot_layout()

        from MainWindow import is_data_collecting
        self.is_data_collecting = is_data_collecting

        self.connect_slots_and_signals()
        self.configFile = QSettings('DAATA', 'MultiDataGraph')
        self.configFile.clear()
        self.load_settings()

    def create_graph_dimension_combo_box(self):
        """
        This function creates the drop down box that allows changing the number of graphs on the screen.

        :return: None
        """
        max_rows = 4
        max_cols = 3
        for row in range(1, max_rows + 1):
            for col in range(1, max_cols + 1):
                self.comboBox_graphDimension.addItem("{0}x{1}".format(row, col))

    def create_grid_plot_layout(self):
        # self.gridPlotLayout = GridPlotLayout(self.scrollAreaWidgetContents)
        # self.gridPlotLayout.setObjectName("gridPlotLayout")
        # self.scrollAreaWidgetContents.setLayout(self.gridPlotLayout)

        currDim = self.comboBox_graphDimension.currentText().split('x')
        max_rows = int(currDim[0])
        max_cols = int(currDim[1])

        row = 0
        col = 0

        leftMar, topMar, rightMar, botMar = \
            self.gridPlotLayout.getContentsMargins()
        hSpace = self.gridPlotLayout.horizontalSpacing()
        vSpace = self.gridPlotLayout.verticalSpacing()
        scroll_area_height = self.scrollArea_graphs.height()
        if scroll_area_height <= 30:
            scroll_area_height = 646  # an arbitrary number

        graphHeight = (scroll_area_height
                       - topMar - botMar
                       - vSpace * (max_rows - 1)) / max_rows

        for key in self.graph_objects.keys():
            # if self.graph_objects[key].isVisible():
            try:
                self.gridPlotLayout.removeWidget(self.graph_objects[key])
                self.graph_objects[key].hide()
            except:
                print(key + " is " + self.graph_objects[key].isVisible())

        for key in self.graph_objects.keys():
            # if self.checkbox_objects[key].isChecked():
            if col == max_cols:
                col = 0
                row += 1
            self.graph_objects[key].set_height(graphHeight)
            self.gridPlotLayout.addWidget((self.graph_objects[key]), row, col, 1, 1)
            self.graph_objects[key].show()
            col += 1

        self.spacerItem_gridPlotLayout = \
            QtWidgets.QSpacerItem(20, 1000000, QtWidgets.QSizePolicy.Minimum,
                                  QtWidgets.QSizePolicy.Expanding)
        self.gridPlotLayout.addItem(self.spacerItem_gridPlotLayout)

    def create_graph(self, key):
        self.graph_objects.pop(key, None)
        self.graph_objects[key] = CustomPlotWidget(key,
                                       parent=self.scrollAreaWidgetContents,
                                       layout=self.gridPlotLayout,
                                       graph_width_seconds=8,
                                       y_sensors=self.y_sensors,
                                       enable_multi_plot=True,
                                       plot_type=self.line_graph)
        # activate settings button
        widget = self.graph_objects[key]
        settings = widget.button_settings.clicked.connect(
            partial(self.graph_objects[key].open_SettingsWindow))

        self.graph_objects[key].show()
        self.create_grid_plot_layout()

    def slot_data_collecting_state_change(self):
        if self.button_display.isChecked():
            self.indicator_onOrOff.setText("On")
            self.indicator_onOrOff.setStyleSheet("color: green;")
            self.button_display.setText("Stop Collecting Data")
            self.is_data_collecting.set()
        else:
            self.indicator_onOrOff.setText("Off")
            self.indicator_onOrOff.setStyleSheet("color: red;")
            self.button_display.setText("Start Collecting Data")
            self.is_data_collecting.clear()
            self.popup_dataSaveLocation()
            # conf = self.popup_stopDataConfirmation()
            # if conf == QtWidgets.QDialog.Accepted:
            #     self.button_display.setText("Start Collecting Data")
            #     self.is_data_collecting.clear()
            #     self.popup_dataSaveLocation()

    def update_sensor_count(self):
        self.active_sensor_count = 0
        # for key in self.checkbox_objects.keys():
        #     if self.checkbox_objects[key].isVisible():
        #         if self.checkbox_objects[key].isChecked():
        #             self.active_sensor_count = self.active_sensor_count + 1
        self.label_active_sensor_count.setText('(' + str(self.active_sensor_count) + '/' + str(len(self.graph_objects)) + ')')

    def update_graphs(self):
        for key in self.graph_objects.keys():
            # if self.graph_objects[key].isVisible():
            self.graph_objects[key].update_graph()

    def update_time_elapsed(self):
        """
        This function updates the timer that is displayed in the layout that indicates how long a test has been running
        for.

        :return: None
        """
        try:
            seconds_elapsed = DataAcquisition.data.get_value("time_internal_seconds",
                                                             DataAcquisition.data.get_most_recent_index())
            seconds_elapsed_int = int(seconds_elapsed)
            hours_elapsed = int(seconds_elapsed_int / 3600)
            minutes_elapsed = int((seconds_elapsed_int - hours_elapsed * 3600) / 60)
            seconds_elapsed = seconds_elapsed % 60
            format_time = "{hours:02d}:{minutes:02d}:{seconds:05.2f}"
            str_time = format_time.format(hours=hours_elapsed, minutes=minutes_elapsed, seconds=seconds_elapsed)
            self.label_timeElapsed.setText(str_time)
        except TypeError:
            pass

    """
    Will update the sensor checkboxes if new sensors are added.
    :return: None
    """
    def update_connected_sensors(self):
        connected_sensors = data.get_sensors(is_plottable=True,
                                             is_connected=True)
        self.connected_sensors = connected_sensors

    def update_active(self):
        """
        This function will update only if the Data Collection tab is the current tab. This function will get called
        at whatever frequency self.update_freq is set at. It is called via the update_all function from the
        MainWindow.

        :return: None
        """

        if self.is_data_collecting.is_set():
            if self.button_display.isChecked():
                self.update_graphs()
                self.update_time_elapsed()

        # temporary implementation of global recording button update
        if self.is_data_collecting.is_set():
            self.indicator_onOrOff.setText("On")
            self.indicator_onOrOff.setStyleSheet("color: green;")
            self.button_display.setText("Stop Collecting Data")
            self.button_display.setChecked(True)
        else:
            self.indicator_onOrOff.setText("Off")
            self.indicator_onOrOff.setStyleSheet("color: red;")
            self.button_display.setText("Start Collecting Data")
            self.button_display.setChecked(False)

    def update_passive(self):
        self.update_connected_sensors()

    """
    Adds one more independent multi data graph to the scene
    """
    def addMDG(self):
        newMDGNumber = int(self.mdgNumber.text()) + 1
        self.mdgNumber.setText(str(newMDGNumber))

        current_MDG_count = len(self.graph_objects)
        self.create_graph(current_MDG_count)

    """
    Removes the most recently added multi data graph from the scene
    """
    def removeMDG(self):
        newMDGNumber = int(self.mdgNumber.text()) - 1
        if newMDGNumber < 0:
            newMDGNumber = 0
        self.mdgNumber.setText(str(newMDGNumber))

        current_MDG_count = len(self.graph_objects)
        del self.graph_objects[current_MDG_count - 1]
        self.create_grid_plot_layout()

    def connect_slots_and_signals(self):
        self.button_display.clicked.connect(
            self.slot_data_collecting_state_change)

        # for key in self.currentKeys:
        #     self.checkbox_objects[key].clicked.connect(self.create_grid_plot_layout)
        #     self.checkbox_objects[key].clicked.connect(self.save_settings)

        self.comboBox_graphDimension.currentTextChanged.connect(
            self.create_grid_plot_layout)
        self.comboBox_graphDimension.currentTextChanged.connect(
            self.save_settings)

        self.plusMDGButton.clicked.connect(self.addMDG)
        self.minusMDGButton.clicked.connect(self.removeMDG)

    def save_settings(self):
        """
        This function will save the settings for a given scene to a config file so that they can be loaded in again
        the next time that the scene is opened (even if the entire GUI is restarted).

        :return: None
        """
        self.configFile.setValue('graph_dimension', self.comboBox_graphDimension.currentText())
        self.configFile.setValue('scrollArea_graphs_height', self.scrollArea_graphs.height())

        enabledSensors = []
        # for key in self.graph_objects.keys():
        #     if self.checkbox_objects[key].isChecked():
        #         enabledSensors.append(key)
        # self.configFile.setValue('enabledSensors', enabledSensors)

        logger.debug("Data Collection config files saved")
        # self.debug_settings()

    def load_settings(self):
        """
        This function loads in the previously saved settings.

        :return: None
        """
        try:
            active_sensor_count = 0
            for key in self.configFile.value('enabledSensors'):
                print(key)
                # self.checkbox_objects[key].setChecked(True)
                self.graph_objects[key].show()
                active_sensor_count = active_sensor_count + 1
                self.label_active_sensor_count.setText(
                    '(' + str(active_sensor_count) + '/' + str(len(self.graph_objects)) + ')')
        except TypeError or KeyError:
            logger.error("Possibly invalid key in config. May need to clear config file using self.configFile.clear()")
            pass

        self.comboBox_graphDimension.setCurrentText(self.configFile.value('graph_dimension'))
        # self.slot_graphDimension()
        # self.create_grid_plot_layout()
        logger.debug("Data Collection config files loaded")
        # self.debug_settings()

    def debug_settings(self):
        """
        This method allows you to view the contents of what is currently stored in settings
        :return:
        """
        for key in self.configFile.allKeys():
            print(key + ":\t\t" + str(self.configFile.value(key)))

    # --- imported methods --- #
    from Utilities.DataExport.dataSaveLocation import popup_dataSaveLocation
    from Utilities.Popups.popups import popup_stopDataConfirmation
    from Utilities.DataExport.exportMAT import saveMAT

    # --- Overridden event methods --- #
    def closeEvent(self):
        self.save_settings()
        self.window().setWindowTitle('closed tab')

    ## The line QtGui.QStyleOption() will throw an error
    '''
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
    '''
