from DataAcquisition import data
from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QGridLayout
from Scenes.MultiDataGraph.MDG_init_props import MDGInitProps
from Utilities.general_constants import TIME_OPTION
from functools import partial
from typing import List, Dict, Tuple
import logging
import numpy
import os
import pyqtgraph as pg

logger = logging.getLogger("Plotting")

# loads the .ui file from QT Designer
uiPlotWidget, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                              'graphWidget.ui'))


class CustomPlotWidget(QtWidgets.QWidget, uiPlotWidget):
    def __init__(self, sensor_name, parent=None,
                 enable_scroll: Tuple[bool, bool] = (False, False),
                 MDG_init_props: MDGInitProps = None, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.sensor_name = sensor_name

        pg.setConfigOption('foreground', 'w')

        self.enable_multi_plot = (MDG_init_props is not None)
        if self.enable_multi_plot:
            self.MDG_init_props: MDGInitProps = MDG_init_props
            self.setObjectName("MDG #" + str(sensor_name))
            self.mdg_is_line_graph = MDG_init_props.is_line_graph
            # sets the current x and y sensors plotted on the graph
            self.mdg_x_sensor: str = MDG_init_props.x_sensor
            self.mdg_y_sensors: List[str] = \
                MDG_init_props.y_sensors if MDG_init_props.y_sensors else []
            if MDG_init_props.read_only:
                self.INIT_SENSOR_VALUES: Dict[str, numpy.ndarray] = \
                    MDG_init_props.initial_data_values
                # by default limits the max number of sensors plotted
                self.mdg_y_sensors = self.mdg_y_sensors[:5]

        self.setMinimumSize(QtCore.QSize(200, 200))
        self.setMaximumSize(QtCore.QSize(16777215, 400))

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHorizontalStretch(4)
        self.setSizePolicy(sizePolicy)

        # disable mouse-scroll zooming on the graph
        self.plotWidget.setMouseEnabled(enable_scroll[0], enable_scroll[1])

        # adds a legend describing what each line represents based on the 'name'
        self.plotWidget.addLegend()

        if self.enable_multi_plot:
            # set title and axes
            self.plotWidget.setLabels(
                bottom="Time (s)" if self.mdg_x_sensor == TIME_OPTION else "",
                title=str(self.objectName()))
        else:
            # set title and axes
            self.plotWidget.setLabels(
                left=f"{str(data.get_display_name(sensor_name))} "
                     f"({str(data.get_unit_short(sensor_name))})",
                bottom="Time (s)",
                title=f"{str(data.get_display_name(sensor_name))} Graph")

        self.plotWidget.showGrid(x=True, y=True, alpha=.2)
        self.plotWidget.setBackground("#343538")

        # Number of value to show on the x_axis
        self.samplingFreq = 200
        self.graph_width = kwargs.get("graph_width_seconds", 10) \
                           * self.samplingFreq

        # the layout object the plot is embedded within
        self.embedLayout = kwargs.get("layout", None)

        # Frequency of values to show (if set to 5 will show every 5th value
        # collected)
        self.show_width = kwargs.get("show_width", 5)

        # Row and column span of plot on the grid
        self.rowSpan = kwargs.get("rowspan", 1)
        self.rowSpan = kwargs.get("columnspan", 1)

        valueArray = numpy.zeros(self.graph_width)

        self.multi_plots: dict = dict()
        if self.enable_multi_plot:
            self.__create_multi_graphs()
        else:
            self.plot = self.plotWidget.plot(valueArray,
                                             name=self.sensor_name,
                                             pen=pg.mkPen(color="#ff0d9e"),
                                             width=1)

        self.initialCounter = 0

        self.configFile = QtCore.QSettings('DAATA_plot', self.sensor_name)
        self.configFile.clear()
        self.loadStylesheet()
        self.loadSettings()

    def loadStylesheet(self):
        self.stylesheetDefault = """
        CustomPlotWidget {
        background-color: #343538;
        color: white;
        }
        CustomPlotWidget * { 
        background-color: transparent;
        color: white;
        }
        """

        self.stylesheetHighlight = """
        CustomPlotWidget {
        background-color: #343538;
        border: 3px solid #196dff;
        color: white;
        }
        CustomPlotWidget * { 
        background-color: transparent;
        color: white;
        }
        """"""
        CustomPlotWidget {
        background-color: #343538;
        color: white;
        }
        CustomPlotWidget * { 
        background-color: transparent;
        color: white;
        }
        """
        self.setStyleSheet(self.stylesheetDefault)

    def set_graphWidth(self, seconds):
        try:
            self.graph_width = int(seconds) * self.samplingFreq
        except Exception:
            self.graph_width = 10 * self.samplingFreq

    def set_yMinMax(self, yMin, yMax):
        self.plotWidget.setYRange(0, 100)
        self.enable_autoRange(True)
        self.plotWidget.setLimits(yMin=None, yMax=None)
        if yMax != 'auto' and yMin == 'auto':
            self.plotWidget.setLimits(yMax=int(yMax))
        if yMin != 'auto' and yMax == 'auto':
            self.plotWidget.setLimits(yMin=int(yMin))
        if (yMin != 'auto') and (yMax != 'auto'):
            # self.plotWidget.setLimits(yMin = int(yMin), yMax = int(yMax))
            # Set strict visible range
            self.plotWidget.setYRange(int(yMin), int(yMax), padding=0)
        if (yMin == 'auto') and (yMax == 'auto'):
            self.enable_autoRange(True)
            self.plotWidget.setLimits(yMin=None, yMax=None)

    def enable_autoRange(self, enable=True):
        self.plotWidget.enableAutoRange(enable)

    def set_height(self, height):
        self.setMinimumSize(QtCore.QSize(200, height))
        self.setMaximumSize(QtCore.QSize(16777215, height))

    def initialize_values(self, timeArray: list, valueArray: list):
        self.plot.setData(timeArray, valueArray)

    def initialize_MDG_values(self):
        if self.mdg_is_line_graph:
            for sensor in self.mdg_y_sensors:
                self.multi_plots[sensor].setData(
                    self.INIT_SENSOR_VALUES[self.mdg_x_sensor],
                    self.INIT_SENSOR_VALUES[sensor])
        else:
            for sensor in self.mdg_y_sensors:
                self.multi_plots[sensor].addPoints(
                    self.INIT_SENSOR_VALUES[self.mdg_x_sensor],
                    self.INIT_SENSOR_VALUES[sensor])

    def update_graph(self):
        if self.enable_multi_plot:
            self.update_multi_graphs()
        else:
            index_time = data.get_most_recent_index()
            index_sensor = data.get_most_recent_index(
                sensor_name=self.sensor_name)
            valueArray = data.get_values(self.sensor_name, index_sensor,
                                         self.graph_width)
            timeArray = data.get_values("time_internal_seconds", index_time,
                                        self.graph_width)
            self.plot.setData(timeArray, valueArray)

    @staticmethod
    def __create_pen_brush(color_choice=0, create_pen=True):
        """
        Returns a pyqtgraph 'pg' pen or brush object of a color depending on
        the color_choice input integer. Colors should be colorblind-friendly
        :param color_choice: an integer to choose which color, value will be
        reduced modulated (%) to the number of possible colors
        :param create_pen: True if you want to return a pen object, False if
        want a brush
        :return: A brush or a pen depending on create_pen.
        """
        # 10 colors = green, red, blue, orange, purple,
        # black, pink, brown, gray, blue-green
        COLORS = ["#9ACD32",  # Atlantis or light green
                  "#FFA500",  # Web orange
                  "#0000FF",  # Blue
                  "#FF0000",  # Red
                  "#DA70D6",  # Orchid
                  "#FFFFFF",  # White
                  "#FFC0CB",  # Pink
                  "#964B00",  # Brown
                  "#797979",  # Boulder
                  "#0d98ba"]  # Pacific blue
        if create_pen:
            return pg.mkPen(color=COLORS[color_choice % len(COLORS)])
        else:
            return pg.mkBrush(color=COLORS[color_choice % len(COLORS)])

    def __create_multi_graphs(self):
        # clears all plots listed made after x-y sensor selection changes
        self.multi_plots.clear()

        # set title and axes
        self.plotWidget.setLabels(
            bottom="Time (s)" if self.mdg_x_sensor == TIME_OPTION else "",
            title=self.objectName())

        valueArray = numpy.zeros(self.graph_width)

        if self.mdg_is_line_graph:
            # creates the individual line plots on the graph and adds them to a
            # list
            for sensor_i, sensor in enumerate(self.mdg_y_sensors):
                pen = self.__create_pen_brush(sensor_i, True)
                plot = self.plotWidget.plot(valueArray,
                                            name=sensor,
                                            pen=pen,
                                            width=1)
                self.multi_plots[sensor] = plot
        else:
            # creates the individual line plots on the graph and adds them to a
            # list
            for sensor_i, sensor in enumerate(self.mdg_y_sensors):
                brush = self.__create_pen_brush(sensor_i, False)
                scatter = pg.ScatterPlotItem(size=10,
                                             brush=brush)
                self.plotWidget.addItem(scatter)
                self.multi_plots[sensor] = scatter

    def update_multi_graphs(self) -> None:
        """
        Updates all line plots contained in list self.multi_plots according to
        which x-y sensors are selected
        :return: None
        """
        if self.mdg_is_line_graph:
            for sensor_i, sensor in enumerate(self.mdg_y_sensors):
                index_time = data.get_most_recent_index()
                index_sensor = data.get_most_recent_index(sensor_name=sensor)
                valueArrayY = data.get_values(sensor, index_sensor,
                                              self.graph_width)
                if self.mdg_x_sensor == TIME_OPTION:
                    timeArray = data.get_values("time_internal_seconds",
                                                index_time, self.graph_width)
                    self.multi_plots[sensor].setData(timeArray, valueArrayY)
                else:
                    index_sensorX = data.get_most_recent_index(
                        sensor_name=self.mdg_x_sensor)
                    valueArrayX = data.get_values(self.mdg_x_sensor,
                                                  index_sensorX,
                                                  self.graph_width)
                    self.multi_plots[sensor].setData(valueArrayX, valueArrayY)
        else:
            for sensor_i, sensor in enumerate(self.mdg_y_sensors):
                index_time = data.get_most_recent_index()
                index_sensor = data.get_most_recent_index(sensor_name=sensor)
                valueArrayY = data.get_values(sensor, index_sensor,
                                              self.graph_width)
                if self.mdg_x_sensor == TIME_OPTION:
                    # get time values
                    timeArray = data.get_values("time_internal_seconds",
                                                index_time, self.graph_width)
                    # add points
                    self.multi_plots[sensor].addPoints(timeArray,
                                                       valueArrayY)
                else:
                    index_sensorX = data.get_most_recent_index(
                        sensor_name=self.mdg_x_sensor)
                    valueArrayX = data.get_values(self.mdg_x_sensor,
                                                  index_sensorX,
                                                  self.graph_width)
                    self.multi_plots[sensor].addPoints(valueArrayX,
                                                       valueArrayY)

    def update_xy_sensors(self, x_sensor, y_sensors):
        self.mdg_x_sensor = x_sensor
        self.mdg_y_sensors = y_sensors
        self.__create_multi_graphs()
        if self.MDG_init_props.read_only:
            self.initialize_MDG_values()

    def open_SettingsWindow(self):
        if self.enable_multi_plot:
            PlotSettingsDialogMDG(self, self.embedLayout,
                                  self.mdg_x_sensor, self.mdg_y_sensors,
                                  self.MDG_init_props)
        else:
            PlotSettingsDialog(self, self.embedLayout, self.sensor_name)

    def connectSignalSlots(self):
        self.button_settings.clicked.connect(
            partial(self.open_SettingsWindow, self))

    def saveSettings(self):
        pass

    def loadSettings(self):
        yMin = self.configFile.value("yMin")
        yMax = self.configFile.value("yMax")
        if yMin is None:
            self.configFile.setValue("yMin", "auto")
            yMin = "auto"
        if yMax is None:
            self.configFile.setValue("yMax", "auto")
            yMax = "auto"
        self.set_graphWidth(self.configFile.value("graph_width"))

        self.set_yMinMax(yMin, yMax)

    # allow color scheme of class to be changed by CSS stylesheets
    def paintEvent(self, pe):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()
        s.drawPrimitive(QtGui.QStyle.PE_Widget, opt, p, self)


# loads the .ui file from QT Designer
uiSettingsDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                                  'plotSettings.ui'))


class PlotSettingsDialog(QtWidgets.QDialog, uiSettingsDialog):
    def __init__(self, parent, embedLayout, sensor_name):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.embedLayout = embedLayout
        self.sensor_name = sensor_name
        self.window().setWindowTitle(
            data.get_display_name(sensor_name) + " Plot Settings")
        self.connectSlotsSignals()
        self.reposition()

        self.configFile = QtCore.QSettings('DAATA_plot', self.sensor_name)
        self.loadSettings()
        self.parent.setStyleSheet(self.parent.stylesheetHighlight)
        returnValue = self.exec()

    def loadSettings(self):
        self.lineEdit_graph_width_seconds.setText(
            str(self.parent.graph_width / self.parent.samplingFreq))
        self.lineEdit_yMin.setText(self.configFile.value("yMin"))
        self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def applySettings(self):
        self.saveSettings()
        self.parent.set_yMinMax(self.configFile.value("yMin"),
                                self.configFile.value("yMax"))
        self.parent.set_graphWidth(self.configFile.value("graph_width"))
        self.lineEdit_yMin.setText(self.configFile.value("yMin"))
        self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def saveSettings(self):
        self.configFile.setValue("graph_width",
                                 self.lineEdit_graph_width_seconds.text())
        self.configFile.setValue("yMin", self.lineEdit_yMin.text())
        self.configFile.setValue("yMax", self.lineEdit_yMax.text())

    # direction can be 'up','left','right','down'
    def sendMoveSignal(self, direction):
        self.embedLayout.moveWidget(self.parent, direction)

    def reposition(self, **kwargs):
        xOverride = kwargs.get("xOverride", 0)
        yOverride = kwargs.get("yOverride", 0)

        if xOverride == 0:
            x = self.embedLayout.parent().mapToGlobal(QtCore.QPoint(0,
                                                                    0)).x() + self.embedLayout.parent().width() + 20
            # x = self.parent.mapToGlobal(QtCore.QPoint(0, 0)).x() + self.embedLayout.width()

        else:
            x = xOverride

        if yOverride == 0:
            y = self.embedLayout.parent().mapToGlobal(QtCore.QPoint(0,
                                                                    0)).y() + self.embedLayout.parent().height() / 3
        else:
            y = yOverride

        self.move(x, y)

    def resetYMax(self):
        self.parent.enable_autoRange(True)
        self.lineEdit_yMax.setText("auto")
        self.configFile.setValue("yMax", self.lineEdit_yMax.text())
        self.parent.set_yMinMax(self.configFile.value("yMin"),
                                self.configFile.value("yMax"))

        # self.lineEdit_yMin.setText(self.configFile.value("yMin"))

    def resetYMin(self):
        self.parent.enable_autoRange(True)
        self.lineEdit_yMin.setText("auto")
        self.configFile.setValue("yMin", self.lineEdit_yMin.text())
        self.parent.set_yMinMax(self.configFile.value("yMin"),
                                self.configFile.value("yMax"))

        # self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def connectSlotsSignals(self):
        self.pushButton_apply.clicked.connect(self.applySettings)
        self.button_moveDown.clicked.connect(
            partial(self.sendMoveSignal, 'down'))
        self.button_moveLeft.clicked.connect(
            partial(self.sendMoveSignal, 'left'))
        self.button_moveRight.clicked.connect(
            partial(self.sendMoveSignal, 'right'))
        self.button_moveUp.clicked.connect(partial(self.sendMoveSignal, 'up'))

        self.button_resetYMax.clicked.connect(self.resetYMax)
        self.button_resetYMin.clicked.connect(self.resetYMin)

    def closeEvent(self, e):
        self.parent.setStyleSheet(self.parent.stylesheetDefault)
        del self


# loads the .ui file from QT Designer in case plotting a multi data graph
uiSettingsDialogMDG, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                                     'plotSettingsMultiDataGraph.ui'))


class PlotSettingsDialogMDG(QtWidgets.QDialog, uiSettingsDialogMDG):
    def __init__(self, parent: CustomPlotWidget, embedLayout, x_sensor: str,
                 y_sensors: List[str], MDG_init_props: MDGInitProps):
        super().__init__()
        self.setupUi(self)
        self.parent: CustomPlotWidget = parent
        self.embedLayout = embedLayout

        multi_graph_name = parent.objectName()
        self.window().setWindowTitle(multi_graph_name + " Plot Settings")
        self.read_only = MDG_init_props.read_only

        if self.read_only:
            self.available_sensors: List[str] = \
                list(MDG_init_props.initial_data_values.keys())
            if TIME_OPTION in self.available_sensors:
                self.available_sensors.remove(TIME_OPTION)
        else:
            if self.parent.mdg_is_line_graph:
                self.scatterOrLineBtn.setText("Scatter Plot")
            else:
                self.scatterOrLineBtn.setText("Line Plot")
            self.available_sensors: List[str] = data.get_sensors(
                is_plottable=True, is_connected=True)

        # Adds the sensor options for the x- and y-axis.
        # x and y dict() is in form sensor_1:<RadioButton object>.
        # self.checked_x_key  is currently selected x sensor key and
        # self.checked_y_keys are currently selected y sensor keys; updated
        # every time the Apply button is clicked
        self.x_radio_objects: Dict[str, QtWidgets.QRadioButton] = dict()
        self.checked_x_key: str = x_sensor
        self.addXSensorCheckboxes()

        self.y_checkbox_objects = dict()
        self.checked_y_keys = y_sensors
        self.addYSensorCheckboxes()

        self.connectSlotsSignals()
        self.reposition()

        self.configFile = QtCore.QSettings('DAATA_plot', multi_graph_name)
        self.loadSettings()
        self.parent.setStyleSheet(self.parent.stylesheetHighlight)

        self.lineEdit_yMin.setText("auto")
        self.lineEdit_yMax.setText("auto")

        returnValue = self.exec()

    def addXSensorCheckboxes(self):
        """
        Adds all sensor checkboxes for x-axis representing all connected
        sensors; the currently plotted x sensors are selected.
        :return: None
        """
        # adds the time option radio button as one option for x-axis

        self.x_radio_objects[TIME_OPTION] = QtWidgets.QRadioButton(
            TIME_OPTION, self.xSensorContents,
            objectName=TIME_OPTION)
        self.x_radio_objects[TIME_OPTION].setToolTip(
            self.x_radio_objects[TIME_OPTION].objectName())
        self.xGridLayout.addWidget(self.x_radio_objects[TIME_OPTION])

        # creates a radio button for each connected sensors in dictionary in
        # self.xSensorContents; only one sensor can be in the x-axis
        for key in self.available_sensors:
            self.x_radio_objects[key] = QtWidgets.QRadioButton(
                data.get_display_name(key), self.xSensorContents,
                objectName=key)
            self.x_radio_objects[key].setToolTip(
                self.x_radio_objects[key].objectName())
            self.xGridLayout.addWidget(self.x_radio_objects[key])

        self.x_radio_objects[self.checked_x_key].setChecked(True)

    def addYSensorCheckboxes(self):
        """
        Adds all sensor checkboxes for y-axis representing Time and all
        connected sensors; Time is selected by default.
        :return:
        """
        # creates a checkbox button for each sensor in dictionary in
        # self.ySensorsContents; multiple sensors can be plotted in the y-axis
        # NB: ySensorsContents has 's' after ySensor, but not xSensorContents

        # Create the checkbox for selecting all sensors
        self.select_all_y_checkbox = QtWidgets.QCheckBox(
            "Select All",
            self.ySensorsContents,
            objectName="select_all_y_checkbox")
        self.select_all_y_checkbox.setToolTip(
            self.select_all_y_checkbox.objectName())
        self.yGridLayout.addWidget(self.select_all_y_checkbox)

        for key in self.available_sensors:
            self.y_checkbox_objects[key] = QtWidgets.QCheckBox(
                data.get_display_name(key), self.ySensorsContents,
                objectName=key)
            self.y_checkbox_objects[key].setToolTip(
                self.y_checkbox_objects[key].objectName())
            self.yGridLayout.addWidget(self.y_checkbox_objects[key])

        # checks all the currently plotted y sensors on this graph
        if len(self.checked_y_keys) == len(self.available_sensors):
            # if all connected sensors are checked, set select all checkbox to
            # checked
            self.select_all_y_checkbox.setChecked(True)
        for key in self.checked_y_keys:
            self.y_checkbox_objects[key].setChecked(True)

    def select_all_btn_change(self):
        if self.select_all_y_checkbox.isChecked():
            for key in self.available_sensors:
                self.y_checkbox_objects[key].setChecked(True)
        else:
            for key in self.available_sensors:
                self.y_checkbox_objects[key].setChecked(False)
        # self.update_xy_sensors()

    def update_xy_sensors(self):
        """
        Updates the current stored selection of x and y sensors
        :return: None
        """
        # if TIME_OPTION is selected, then the checked_x_key will be the
        # TIME_OPTION, and we won't check the rest of x sensor options.
        # This is important because TIME_OPTION is not part of connected_sensors
        if self.x_radio_objects[TIME_OPTION].isChecked():
            self.checked_x_key = TIME_OPTION

            # if selected Select All y sensors, all connected sensors will be
            # added to the self.checked_y_keys list
            self.checked_y_keys.clear()
            if self.select_all_y_checkbox.isChecked():
                self.checked_y_keys.extend(self.available_sensors)
            else:
                # adds selected y sensors to the checked_y_keys list, removes
                # unselected sensors
                for key in self.available_sensors:
                    if self.y_checkbox_objects[key].isChecked():
                        self.checked_y_keys.append(key)
        else:
            self.checked_y_keys.clear()
            for key in self.available_sensors:
                # adds selected y sensors to the checked_y_keys list, removes
                # unselected sensors
                if self.y_checkbox_objects[key].isChecked():
                    self.checked_y_keys.append(key)

                # updates the selected x sensor to a variable
                if self.x_radio_objects[key].isChecked():
                    self.checked_x_key = key

    def loadSettings(self):
        self.lineEdit_graph_width_seconds.setText(str(
            self.parent.graph_width / self.parent.samplingFreq))
        self.lineEdit_yMin.setText(self.configFile.value("yMin"))
        self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def applySettings(self):
        self.saveSettings()
        self.parent.set_yMinMax(self.configFile.value("yMin"),
                                self.configFile.value("yMax"))
        self.parent.set_graphWidth(self.configFile.value("graph_width"))
        self.lineEdit_yMin.setText(self.configFile.value("yMin"))
        self.lineEdit_yMax.setText(self.configFile.value("yMax"))

        # updates the plot graph based on selections of x and y sensors
        self.update_this_MDG()

    def update_this_MDG(self):
        """
        Clears and updates this multi data graph with the newly selected
        x-y sensors and plot type option
        :return:
        """
        self.update_xy_sensors()
        self.parent.plotWidget.clear()
        self.parent.update_xy_sensors(self.checked_x_key, self.checked_y_keys)

    def saveSettings(self):
        self.configFile.setValue("graph_width",
                                 self.lineEdit_graph_width_seconds.text())
        self.configFile.setValue("yMin", self.lineEdit_yMin.text())
        self.configFile.setValue("yMax", self.lineEdit_yMax.text())

    def sendMoveSignal(self, direction):
        # direction can be 'up','left','right','down'
        self.embedLayout.moveWidget(self.parent, direction)

    def reposition(self, **kwargs):
        xOverride = kwargs.get("xOverride", 0)
        yOverride = kwargs.get("yOverride", 0)

        if xOverride == 0:
            x = self.embedLayout.parent().mapToGlobal(QtCore.QPoint(0,
                                                                    0)).x() + self.embedLayout.parent().width() + 20
            # x = self.parent.mapToGlobal(QtCore.QPoint(0, 0)).x() + self.embedLayout.width()

        else:
            x = xOverride

        if yOverride == 0:
            y = self.embedLayout.parent().mapToGlobal(QtCore.QPoint(0,
                                                                    0)).y() + self.embedLayout.parent().height() / 3
        else:
            y = yOverride

        self.move(x, y)

    def resetYMax(self):
        self.parent.enable_autoRange(True)
        self.lineEdit_yMax.setText("auto")
        self.configFile.setValue("yMax", self.lineEdit_yMax.text())
        self.parent.set_yMinMax(self.configFile.value("yMin"),
                                self.configFile.value("yMax"))

        # self.lineEdit_yMin.setText(self.configFile.value("yMin"))

    def resetYMin(self):
        self.parent.enable_autoRange(True)
        self.lineEdit_yMin.setText("auto")
        self.configFile.setValue("yMin", self.lineEdit_yMin.text())
        self.parent.set_yMinMax(self.configFile.value("yMin"),
                                self.configFile.value("yMax"))

        # self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def changePlotType(self):
        """
        Changes the plot type from scatter plot to line graph or vice versa and
        updates the MDG
        :return:
        """
        if self.scatterOrLineBtn.text() == self.scatter_plot_name:
            # change plot type to scatter plot
            self.scatterOrLineBtn.setText(self.line_graph_name)
            self.parent.mdg_is_line_graph = False
        elif self.scatterOrLineBtn.text() == self.line_graph_name:
            # change plot type to line graph
            self.scatterOrLineBtn.setText(self.scatter_plot_name)
            self.parent.mdg_is_line_graph = True
        # self.update_this_MDG()

    def connectSlotsSignals(self):
        self.pushButton_apply.clicked.connect(self.applySettings)
        self.pushButton_ok.clicked.connect(self.closeSavePlotSettings)
        self.button_moveDown.clicked.connect(
            partial(self.sendMoveSignal, 'down'))
        self.button_moveLeft.clicked.connect(
            partial(self.sendMoveSignal, 'left'))
        self.button_moveRight.clicked.connect(
            partial(self.sendMoveSignal, 'right'))
        self.button_moveUp.clicked.connect(partial(self.sendMoveSignal, 'up'))
        self.scatterOrLineBtn.clicked.connect(self.changePlotType)

        self.select_all_y_checkbox.clicked.connect(self.select_all_btn_change)

        self.button_resetYMax.clicked.connect(self.resetYMax)
        self.button_resetYMin.clicked.connect(self.resetYMin)

        # for key in self.x_radio_objects:

    def closeEvent(self, e):
        self.parent.setStyleSheet(self.parent.stylesheetDefault)
        del self

    def closeSavePlotSettings(self):
        self.applySettings()
        self.close()


class GridPlotLayout(QGridLayout):
    def __init__(self, parent=None):
        super(GridPlotLayout, self).__init__(parent)
        spacing = 6
        self.setContentsMargins(spacing, spacing, spacing, spacing)
        self.setSpacing(spacing)

    def moveWidget(self, widg, direction):
        oldRow = self.rowOf(widg)
        oldCol = self.colOf(widg)

        if 'up' == direction:
            newRow = oldRow - 1
            newCol = oldCol
        elif 'left' == direction:
            newRow = oldRow
            newCol = oldCol - 1
        elif 'right' == direction:
            newRow = oldRow
            newCol = oldCol + 1
        elif 'down' == direction:
            newRow = oldRow + 1
            newCol = oldCol
        else:
            raise ValueError(
                'moveWidget(self, widg, direction): argument 2 has invalid '
                '\'str\' value (up, left, right, down)')

        try:
            displacedWidg = self.widgetAtPosition(newRow, newCol)
            if displacedWidg is None:
                return AttributeError
            self.removeWidget(widg)
            self.removeWidget(displacedWidg)
            self.addWidget(widg, newRow, newCol)
            self.addWidget(displacedWidg, oldRow, oldCol)
        except AttributeError:
            logger.debug(logger.findCaller(True))

    def widgetAtPosition(self, row, col):
        return self.itemAtPosition(row, col).widget()

    def rowOf(self, widg):
        index = self.indexOf(widg)
        position = self.getItemPosition(index)
        return position[0]

    def colOf(self, widg):
        index = self.indexOf(widg)
        position = self.getItemPosition(index)
        return position[1]

    def rowSpanOf(self, widg):
        index = self.indexOf(widg)
        position = self.getItemPosition(index)
        return position[2]

    def colSpanOf(self, widg):
        index = self.indexOf(widg)
        position = self.getItemPosition(index)
        return position[3]
