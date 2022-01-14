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

# Load the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'data_collection.ui'))

logger = logging.getLogger("DataCollection")

# Todo List      ####################################
# add warning dialog if trying to start recording data while teensy is not plugged in (checked with data.is_connected)


class DataCollection(DAATAScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.hide()

        # Tab updates every x*10 ms (ex. 3*10 = every 30 ms)
        self.update_period = 3  

        self.graph_objects = dict()
        self.checkbox_objects = dict()
        self.currentKeys = data.get_sensors(is_plottable=True)

        self.gridPlotLayout = GridPlotLayout(self.scrollAreaWidgetContents)
        self.gridPlotLayout.setObjectName("gridPlotLayout")
        self.scrollAreaWidgetContents.setLayout(self.gridPlotLayout)

        self.create_sensor_checkboxes()
        self.create_graph_dimension_combo_box()
        self.create_graphs()
        self.create_grid_plot_layout()

        from MainWindow import is_data_collecting
        self.is_data_collecting = is_data_collecting

        self.connect_slots_and_signals()
        self.configFile = QSettings('DAATA', 'data_collection')
        self.configFile.clear()
        self.load_settings()

    def create_sensor_checkboxes(self):
        """
        Creates checkboxes for each active sensor and for selecting all active sensors.

        :return: None
        """

        # Create the checkbox for selecting all of the sensors
        self.selectAll_checkbox = QtWidgets.QCheckBox("Select All", self.scrollAreaWidgetContents_2, objectName="selectAll_checkbox")
        self.selectAll_checkbox.setToolTip(self.selectAll_checkbox.objectName())
        self.gridLayout_2.addWidget(self.selectAll_checkbox)

        # Create a checkbox for each sensor in dictionary in self.scrollAreaWidgetContents_2
        for key in self.currentKeys:
            self.checkbox_objects[key] = QtWidgets.QCheckBox(data.get_display_name(key), self.scrollAreaWidgetContents_2, objectName=key)
            self.gridLayout_2.addWidget(self.checkbox_objects[key])

        # Create a vertical spacer that forces checkboxes to the top
        spacerItem1 = QtWidgets.QSpacerItem(20, 1000000, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1)

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
        """
        Creates the layout of grids based on selected sensors to be shown and 
        the selected plot configuration (i.e. 2X3).

        :return: None
        """

        currDim = self.comboBox_graphDimension.currentText().split('x')
        max_rows = int(currDim[0])
        max_cols = int(currDim[1])

        row = 0
        col = 0

        leftMar, topMar, rightMar, botMar = self.gridPlotLayout.getContentsMargins()        
        vSpace = self.gridPlotLayout.verticalSpacing()
        graphHeight = (self.scrollArea_graphs.height()-topMar-botMar-vSpace*(max_rows-1)) / max_rows

        for key in self.graph_objects.keys():
            if self.graph_objects[key].isVisible():
                try:
                    self.gridPlotLayout.removeWidget(self.graph_objects[key])
                    self.graph_objects[key].hide()
                except:
                    print(key + " is " + self.graph_objects[key].isVisible())

        for key in self.checkbox_objects.keys():
            if self.checkbox_objects[key].isChecked():
                if col == max_cols:
                    col = 0
                    row += 1
                self.graph_objects[key].set_height(graphHeight)
                self.gridPlotLayout.addWidget((self.graph_objects[key]), row, col, 1, 1)
                self.graph_objects[key].show()

                col += 1

        self.spacerItem_gridPlotLayout = QtWidgets.QSpacerItem(20, 1000000, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridPlotLayout.addItem(self.spacerItem_gridPlotLayout)

    def create_graphs(self):
        """
        Populates graph dictionary with graphs based on active sensors.

        :return: None
        """

        for key in self.currentKeys:
            self.graph_objects[key] = CustomPlotWidget(key, parent=self.scrollAreaWidgetContents, layout=self.gridPlotLayout, graph_width_seconds = 8)
            self.graph_objects[key].setObjectName(key)
            self.graph_objects[key].hide()

    def slot_data_collecting_state_change(self):
        """
        Handles toggling data collecting button and changes values and
        attributes accordingly.

        :return: None
        """

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

    def slot_checkbox_state_change(self):
        """
        Handles checkbox functionality after checking or unchecking events and updates
        sensors and the grid plot accordingly.

        :return: None
        """

        if self.selectAll_checkbox.isChecked():
            for key in self.currentKeys:
                self.checkbox_objects[key].setChecked(True)
        else:
            for key in self.currentKeys:
                self.checkbox_objects[key].setChecked(False)
        self.update_sensor_count()
        self.create_grid_plot_layout()

    def update_sensor_count(self):
        """
        Updates the count of active sensors based on selected sensors
        in the checkbox.

        :return: None
        """

        self.active_sensor_count = 0
        for key in self.checkbox_objects.keys():
            if self.checkbox_objects[key].isVisible() and self.checkbox_objects[key].isChecked():
                    self.active_sensor_count = self.active_sensor_count + 1
        self.label_active_sensor_count.setText('(' + str(self.active_sensor_count) + '/' + str(len(self.graph_objects)) + ')')

    def update_graphs(self):
        """
        Updates the graph objects with their respective values if they are visible.

        :return: None
        """

        for key in self.currentKeys:
            if self.graph_objects[key].isVisible():
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

    def update_sensor_checkboxes(self):
        """
        Will update the sensor checkboxes if new sensors are added.

        :return: None
        """

        connected_sensors = data.get_sensors(is_plottable=True, is_connected=True)
        for key in connected_sensors:
            if key not in self.currentKeys:
                self.checkbox_objects[key].show()
        for key in self.currentKeys:
            if key not in connected_sensors:
                try:
                    self.checkbox_objects[key].hide()
                except Exception:
                    pass
        self.currentKeys = connected_sensors

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
        """
        This function will update no matter what scene is selected to keep
        the checkboxes accurate with active sensors.
        Called by MainWindow.__init__.py.

        :return: None
        """

        self.update_sensor_checkboxes()

    def connect_slots_and_signals(self):
        """
        Assigns button clicks and UI element events with their respective functions.

        :return: None
        """

        self.button_display.clicked.connect(self.slot_data_collecting_state_change)

        for key in self.currentKeys:
            self.checkbox_objects[key].clicked.connect(self.create_grid_plot_layout)
            self.checkbox_objects[key].clicked.connect(self.save_settings)

        self.selectAll_checkbox.stateChanged.connect(self.slot_checkbox_state_change)

        self.comboBox_graphDimension.currentTextChanged.connect(self.create_grid_plot_layout)
        self.comboBox_graphDimension.currentTextChanged.connect(self.save_settings)

        ## connections to GridPlotLayout
        for key in self.graph_objects.keys():
            widget = self.graph_objects[key]
            settings = widget.button_settings.clicked.connect(partial(self.graph_objects[key].open_SettingsWindow))

    def save_settings(self):
        """
        This function will save the settings for a given scene to a config file so that they can be loaded in again
        the next time that the scene is opened (even if the entire GUI is restarted).

        :return: None
        """

        self.configFile.setValue('graph_dimension', self.comboBox_graphDimension.currentText())
        self.configFile.setValue('scrollArea_graphs_height', self.scrollArea_graphs.height())

        enabledSensors = []
        for key in self.graph_objects.keys():
            if self.checkbox_objects[key].isChecked():
                enabledSensors.append(key)
        self.configFile.setValue('enabledSensors', enabledSensors)

        # logger.debug("Data Collection config files saved")
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
                self.checkbox_objects[key].setChecked(True)
                self.graph_objects[key].show()
                active_sensor_count = active_sensor_count + 1
                self.label_active_sensor_count.setText(
                    '(' + str(active_sensor_count) + '/' + str(len(self.graph_objects)) + ')')
        except TypeError or KeyError:
            logger.error("Possibly invalid key in config. May need to clear config file using self.configFile.clear()")
            pass

        self.comboBox_graphDimension.setCurrentText(self.configFile.value('graph_dimension'))        
        self.create_grid_plot_layout()
        logger.debug("Data Collection config files loaded")        

    def debug_settings(self):
        """
        This method allows you to view the contents of what is currently stored in settings.

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
        """
        Handles closing of the DataCollection scene.

        :return: None
        """

        self.save_settings()
        self.window().setWindowTitle('closed tab')


    def paintEvent(self, pe):
        """
        This method allows the color scheme of the class to be changed by CSS stylesheets.

        :param pe:
        :return: None
        """

        # opt = QtGui.QStyleOption()
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()
        # s.drawPrimitive(QtGui.QStyle.PE_Widget, opt, p, self)
        s.drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, p, self)

    
