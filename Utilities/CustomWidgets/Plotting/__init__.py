import logging
import sys, os
import time
from enum import Enum

import pyqtgraph as pg
from functools import partial
from PyQt5 import QtCore, QtWidgets, uic, QtGui
import numpy
from PyQt5.QtWidgets import QGridLayout
from DataAcquisition import data

logger = logging.getLogger("Plotting")


# loads the .ui file from QT Designer
uiPlotWidget, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                              'graphWidget.ui'))


class CustomPlotWidget(QtWidgets.QWidget, uiPlotWidget):
    class PlotTypes(Enum):
        Line_Graph = 1
        Scatter_plot = 2

    def __init__(self, sensor_name, parent=None, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.sensor_name = sensor_name

        self.line_graph = "line_graph"
        self.scatter_plot = "scatter_plot"

        self.enable_multi_plot = kwargs.get("enable_multi_plot", False)

        self.plot_type = kwargs.get("plot_type", self.line_graph)

        # a common arbitrarily key for the time option for x axis
        self.time_option = "Time"
        self.DEF_BRUSH_SIZE = 10

        # sets the current x and y sensors plotted on the graph
        self.y_sensors = kwargs.get("multi_sensors", None)
        self.x_sensor = kwargs.get("x_sensor", self.time_option)

        self.setMinimumSize(QtCore.QSize(200, 200))
        self.setMaximumSize(QtCore.QSize(16777215, 400))

        # all connected sensors, periodically updated from Scenes/<a scene>
        self.connected_sensors = []

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHorizontalStretch(4)
        self.setSizePolicy(sizePolicy)

        # disable mouse-scroll zooming on the graph
        self.plotWidget.setMouseEnabled(False, False)

        # adds a legend describing what each line represents based on the 'name'
        self.plotWidget.addLegend()

        if self.enable_multi_plot:
            # set title and axes, if multi-plot, set labels at
            # create_multi_graphs
            self.plotWidget.setLabels(bottom='Time (s)',
                                      title="Multi Sensor 1 Graph")

        self.plotWidget.showGrid(x=True, y=True, alpha=.2)
        self.plotWidget.setBackground(None)
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

        self.multi_plots = []
        if self.enable_multi_plot:
            self.create_multi_graphs()
        else:
            self.plot = self.plotWidget.plot(valueArray,
                                             name=self.sensor_name,
                                             pen='b',
                                             width=1)

        self.initialCounter = 0

        self.configFile = QtCore.QSettings('DAATA_plot', self.sensor_name)
        self.configFile.clear()
        self.loadStylesheet()
        self.loadSettings()

    def loadStylesheet(self):
        self.stylesheetDefault = """
        CustomPlotWidget {
        background-color: white;
        }
        CustomPlotWidget * { 
        background-color: transparent;
        }
        """

        self.stylesheetHighlight = """
        CustomPlotWidget {
        background-color: white;
        border: 3px solid #196dff;
        }
        CustomPlotWidget * { 
        background-color: transparent;
        }
        """"""
        CustomPlotWidget {
        background-color: white;
        }
        CustomPlotWidget * { 
        background-color: transparent;
        }
        """
        self.setStyleSheet(self.stylesheetDefault)

    # updates all connected sensors
    def update_connected_sensors(self, connected_sensors):
        self.connected_sensors = connected_sensors

    def set_graphWidth(self, seconds):
        try:
            self.graph_width = int(seconds) * self.samplingFreq
        except:
            self.graph_width = 10 * self.samplingFreq

    def set_yMinMax(self, yMin, yMax):
        self.plotWidget.setYRange(0, 100)
        self.enable_autoRange(True)
        self.plotWidget.setLimits(yMin = None, yMax = None)
        if yMax != 'auto' and yMin == 'auto':
            self.plotWidget.setLimits(yMax = int(yMax))
        if yMin != 'auto' and yMax == 'auto':
            self.plotWidget.setLimits(yMin = int(yMin))
        if (yMin != 'auto') and (yMax != 'auto'):
            # self.plotWidget.setLimits(yMin = int(yMin), yMax = int(yMax))
            # Set strict visible range
            self.plotWidget.setYRange(int(yMin), int(yMax), padding=0)
        if (yMin == 'auto') and (yMax == 'auto'):
            self.enable_autoRange(True)
            self.plotWidget.setLimits(yMin = None, yMax = None)

    def enable_autoRange(self, enable=True):
        self.plotWidget.enableAutoRange(enable)

    def set_height(self, height):
        self.setMinimumSize(QtCore.QSize(200, height))
        self.setMaximumSize(QtCore.QSize(16777215, height))

    def update_graph(self):
        if self.enable_multi_plot:
            self.update_multi_graphs()
        else:
            index_time = data.get_most_recent_index()
            index_sensor = data.get_most_recent_index(sensor_name=self.sensor_name)
            valueArray = data.get_values(self.sensor_name, index_sensor, self.graph_width)
            timeArray = data.get_values("time_internal_seconds", index_time, self.graph_width)
            self.plot.setData(timeArray, valueArray)

    """
        Returns a pyqtgraph 'pg' pen or brush object of a color depending on the
        color_choice input integer. Colors should be colorblind-friendly
        :param color_choice: an integer to choose which color, value will be 
        reduce modulated (%) to the number of possible colors
        :param create_pen: True if you want to return a pen object, False if want a 
        brush 
        :return: A brush or a pen depending on create_pen
    """
    def create_pen_brush(self, color_choice=0, create_pen=True):
        # 10 colors = green, red, blue, orange, purple,
        # black, pink, brown, gray, blue-green
        colors = ["#9ACD32", "#FFA500", "#0000FF", "#FF0000", "#DA70D6",
                  "#000000", "#FFC0CB", "#964B00", "#797979", "#0d98ba"]
        if create_pen:
            return pg.mkPen(color=colors[color_choice % len(colors)])
        else:
            return pg.mkBrush(color=colors[color_choice % len(colors)])

    def create_multi_graphs(self):
        # clears all of the plots listed made after x-y sensor selection changes
        self.multi_plots.clear()

        # set title and axes
        if self.x_sensor == self.time_option:
            self.plotWidget.setLabels(
                bottom='Time (s)',
                title=str('Multi Data Graph 1'))
        else:
            self.plotWidget.setLabels(
                bottom='',
                title=str('Multi Data Graph 1'))

        valueArray = numpy.zeros(self.graph_width)

        if self.plot_type == self.line_graph:
            # creates the individual line plots on the graph and adds them to a
            # list
            for sensor_i in range(len(self.y_sensors)):
                sensor = self.y_sensors[sensor_i]
                pen = self.create_pen_brush(sensor_i, True)
                plot = self.plotWidget.plot(valueArray,
                                            name=sensor,
                                            pen=pen,
                                            width=1)
                self.multi_plots.append(plot)
        elif self.plot_type == self.scatter_plot:
            # creates the individual line plots on the graph and adds them to a
            # list
            for sensor_i in range(len(self.y_sensors)):
                brush = self.create_pen_brush(sensor_i, False)
                scatter = pg.ScatterPlotItem(size=self.DEF_BRUSH_SIZE,
                                             brush=brush)
                self.plotWidget.addItem(scatter)
                self.multi_plots.append(scatter)

    # updates all line plots contained in list self.multi_plots according to
    # which x-y sensors are selected
    def update_multi_graphs(self):
        if self.plot_type == self.line_graph:
            for sensor_i in range(len(self.y_sensors)):
                sensor = self.y_sensors[sensor_i]
                index_time = data.get_most_recent_index()
                index_sensor = data.get_most_recent_index(sensor_name=sensor)
                valueArrayY = data.get_values(sensor, index_sensor,
                                                  self.graph_width)
                if self.x_sensor == self.time_option:
                    timeArray = data.get_values("time_internal_seconds",
                                                index_time, self.graph_width)
                    self.multi_plots[sensor_i].setData(timeArray, valueArrayY)
                else:
                    index_sensorX = data.get_most_recent_index(
                        sensor_name=self.x_sensor)
                    valueArrayX = data.get_values(self.x_sensor, index_sensorX,
                                                  self.graph_width)
                    self.multi_plots[sensor_i].setData(valueArrayX, valueArrayY)
        elif self.plot_type == self.scatter_plot:
            for sensor_i in range(len(self.y_sensors)):
                sensor = self.y_sensors[sensor_i]
                index_time = data.get_most_recent_index()
                index_sensor = data.get_most_recent_index(sensor_name=sensor)
                valueArrayY = data.get_values(sensor, index_sensor,
                                              self.graph_width)
                if self.x_sensor == self.time_option:
                    # get time values
                    timeArray = data.get_values("time_internal_seconds",
                                                index_time, self.graph_width)
                    # add points
                    self.multi_plots[sensor_i].addPoints(timeArray,
                                                         valueArrayY)
                else:
                    index_sensorX = data.get_most_recent_index(
                        sensor_name=self.x_sensor)
                    valueArrayX = data.get_values(self.x_sensor, index_sensorX,
                                                  self.graph_width)
                    self.multi_plots[sensor_i].addPoints(valueArrayX,
                                                         valueArrayY)


    def open_SettingsWindow(self):
        if self.enable_multi_plot:
            PlotSettingsDialogMDG(self, self.embedLayout)
        else:
            PlotSettingsDialog(self, self.embedLayout, self.sensor_name)

    def connectSignalSlots(self):
        self.button_settings.clicked.connect(partial(self.open_SettingsWindow, self))

    def saveSettings(self):
        pass

    def loadSettings(self):
        if self.configFile.value("yMin") == None:
            self.configFile.setValue("yMin","auto")
        if self.configFile.value("yMax") == None:
            self.configFile.setValue("yMax","auto")
        self.set_graphWidth(self.configFile.value("graph_width"))

        self.set_yMinMax(self.configFile.value("yMin"), self.configFile.value("yMax"))

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
        self.window().setWindowTitle(data.get_display_name(sensor_name) + " Plot Settings")
        self.connectSlotsSignals()
        self.reposition()

        self.configFile = QtCore.QSettings('DAATA_plot', self.sensor_name)
        self.loadSettings()
        self.parent.setStyleSheet(self.parent.stylesheetHighlight)
        returnValue = self.exec()

    def loadSettings(self):
        self.lineEdit_graph_width_seconds.setText(str(self.parent.graph_width/self.parent.samplingFreq))
        self.lineEdit_yMin.setText(self.configFile.value("yMin"))
        self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def applySettings(self):
        self.saveSettings()
        self.parent.set_yMinMax(self.configFile.value("yMin"),self.configFile.value("yMax"))
        self.parent.set_graphWidth(self.configFile.value("graph_width"))
        self.lineEdit_yMin.setText(self.configFile.value("yMin"))
        self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def saveSettings(self):
        self.configFile.setValue("graph_width", self.lineEdit_graph_width_seconds.text())
        self.configFile.setValue("yMin", self.lineEdit_yMin.text())
        self.configFile.setValue("yMax", self.lineEdit_yMax.text())

    # direction can be 'up','left','right','down'
    def sendMoveSignal(self, direction):
        self.embedLayout.moveWidget(self.parent, direction)

    def reposition(self, **kwargs):
        xOverride = kwargs.get("xOverride", 0)
        yOverride = kwargs.get("yOverride", 0)

        if xOverride == 0:
            x = self.embedLayout.parent().mapToGlobal(QtCore.QPoint(0, 0)).x() + self.embedLayout.parent().width() + 20
            # x = self.parent.mapToGlobal(QtCore.QPoint(0, 0)).x() + self.embedLayout.width()

        else:
            x = xOverride

        if yOverride == 0:
            y = self.embedLayout.parent().mapToGlobal(QtCore.QPoint(0, 0)).y() + self.embedLayout.parent().height()/3
        else:
            y = yOverride

        self.move(x,y)

    def resetYMax(self):
        self.parent.enable_autoRange(True)
        self.lineEdit_yMax.setText("auto")
        self.configFile.setValue("yMax", self.lineEdit_yMax.text())
        self.parent.set_yMinMax(self.configFile.value("yMin"),self.configFile.value("yMax"))

        # self.lineEdit_yMin.setText(self.configFile.value("yMin"))

    def resetYMin(self):
        self.parent.enable_autoRange(True)
        self.lineEdit_yMin.setText("auto")
        self.configFile.setValue("yMin", self.lineEdit_yMin.text())
        self.parent.set_yMinMax(self.configFile.value("yMin"),self.configFile.value("yMax"))

        # self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def connectSlotsSignals(self):
        self.pushButton_apply.clicked.connect(self.applySettings)
        self.button_moveDown.clicked.connect(partial(self.sendMoveSignal, 'down'))
        self.button_moveLeft.clicked.connect(partial(self.sendMoveSignal, 'left'))
        self.button_moveRight.clicked.connect(partial(self.sendMoveSignal, 'right'))
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
    def __init__(self, parent, embedLayout):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.embedLayout = embedLayout
        self.time_option = parent.time_option

        multi_graph_name = "Multi Sensors 1"
        self.window().setWindowTitle(multi_graph_name + " Plot Settings")

        self.connected_sensors = parent.connected_sensors

        # Adds the sensor options for the x and y axis.
        # x and y dict() is in form sensor_1:<RadioButton object>.
        # self.checked_x_key  is currently selected x sensor key and
        # self.checked_y_keys are currently selected y sensor keys; updated
        # every time the Apply button is clicked
        self.x_radio_objects = dict()
        self.checked_x_key = parent.x_sensor
        self.addXSensorCheckboxes()

        self.y_checkbox_objects = dict()
        self.checked_y_keys = parent.y_sensors
        self.addYSensorCheckboxes()

        self.connectSlotsSignals()
        self.reposition()

        self.configFile = QtCore.QSettings('DAATA_plot', multi_graph_name)
        self.loadSettings()
        self.parent.setStyleSheet(self.parent.stylesheetHighlight)

        self.lineEdit_yMin.setText("auto")  # TODO REMOVE
        self.lineEdit_yMax.setText("auto")  # TODO REMOVE

        returnValue = self.exec()

    # adds all sensor checkboxes for x axis representing all connected
    # sensors; the currently plotted x sensors are selected.
    def addXSensorCheckboxes(self):
        # adds the time option radio button as one option for x axis
        self.x_radio_objects[self.time_option] = QtWidgets.QRadioButton(
            self.time_option, self.xSensorContents,
            objectName=self.time_option)
        self.x_radio_objects[self.time_option].setToolTip(
            self.x_radio_objects[self.time_option].objectName())
        self.xGridLayout.addWidget(self.x_radio_objects[self.time_option])

        # creates a radio button for each connected sensors in dictionary in
        # self.xSensorContents; only one sensor can be in the x axis
        for key in self.connected_sensors:
            self.x_radio_objects[key] = QtWidgets.QRadioButton(
                data.get_display_name(key), self.xSensorContents,
                objectName=key)
            self.x_radio_objects[key].setToolTip(
                self.x_radio_objects[key].objectName())
            self.xGridLayout.addWidget(self.x_radio_objects[key])

        self.x_radio_objects[self.checked_x_key].setChecked(True)

    # adds all sensor checkboxes for y axis representing Time and all connected
    # sensors; Time is selected by default.
    def addYSensorCheckboxes(self):
        # creates a checkbox button for each sensor in dictionary in
        # self.ySensorsContents; multiple sensors can be plotted in the y axis
        # NB: ySensorsContents has 's' after ySensor, but not xSensorContents
        for key in self.connected_sensors:
            self.y_checkbox_objects[key] = QtWidgets.QCheckBox(
                data.get_display_name(key), self.ySensorsContents,
                objectName=key)
            self.y_checkbox_objects[key].setToolTip(
                self.y_checkbox_objects[key].objectName())
            self.yGridLayout.addWidget(self.y_checkbox_objects[key])

        # checks all the currently plotted y sensors on this graph
        for key in self.checked_y_keys:
            self.y_checkbox_objects[key].setChecked(True)

    # updates the current stored selection of x and y sensors
    def update_xy_sensors(self):
        # if time_option is selected, then the checked_x_key will be the
        # time_option and we won't check the rest of x sensor options.
        # This is important because time_option is not part of connected_sensors
        if self.x_radio_objects[self.time_option].isChecked():
            self.checked_x_key = self.time_option

            self.checked_y_keys.clear()
            for key in self.connected_sensors:
                # adds selected y sensors to the checked_y_keys list, removes
                # unselected sensors
                if self.y_checkbox_objects[key].isChecked():
                    self.checked_y_keys.append(key)

        else:
            self.checked_y_keys.clear()
            for key in self.connected_sensors:
                # adds selected y sensors to the checked_y_keys list, removes
                # unselected sensors
                if self.y_checkbox_objects[key].isChecked():
                    self.checked_y_keys.append(key)

                # updates the selected x sensor to a variable
                if self.x_radio_objects[key].isChecked():
                    self.checked_x_key = key

    def loadSettings(self):
        self.lineEdit_graph_width_seconds.setText(str(
            self.parent.graph_width/self.parent.samplingFreq))
        self.lineEdit_yMin.setText(self.configFile.value("yMin"))
        self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def applySettings(self):
        self.saveSettings()
        self.parent.set_yMinMax(self.configFile.value("yMin"),self.configFile.value("yMax"))
        self.parent.set_graphWidth(self.configFile.value("graph_width"))
        self.lineEdit_yMin.setText(self.configFile.value("yMin"))
        self.lineEdit_yMax.setText(self.configFile.value("yMax"))

        # updates the plot graph based on selections of x and y sensors
        self.update_this_MDG()

    # updates this multi data graph with the newly selected x-y sensors
    def update_this_MDG(self):
        self.update_xy_sensors()
        self.parent.plotWidget.clear()

        self.parent.y_sensors = self.checked_y_keys
        self.parent.x_sensor = self.checked_x_key
        self.parent.multi_plots.clear()
        self.parent.create_multi_graphs()
        pass

    def saveSettings(self):
        self.configFile.setValue("graph_width", self.lineEdit_graph_width_seconds.text())
        self.configFile.setValue("yMin", self.lineEdit_yMin.text())
        self.configFile.setValue("yMax", self.lineEdit_yMax.text())

    # direction can be 'up','left','right','down'
    def sendMoveSignal(self, direction):
        self.embedLayout.moveWidget(self.parent, direction)

    def reposition(self, **kwargs):
        xOverride = kwargs.get("xOverride", 0)
        yOverride = kwargs.get("yOverride", 0)

        if xOverride == 0:
            x = self.embedLayout.parent().mapToGlobal(QtCore.QPoint(0, 0)).x() + self.embedLayout.parent().width() + 20
            # x = self.parent.mapToGlobal(QtCore.QPoint(0, 0)).x() + self.embedLayout.width()

        else:
            x = xOverride

        if yOverride == 0:
            y = self.embedLayout.parent().mapToGlobal(QtCore.QPoint(0, 0)).y() + self.embedLayout.parent().height()/3
        else:
            y = yOverride

        self.move(x,y)

    def resetYMax(self):
        self.parent.enable_autoRange(True)
        self.lineEdit_yMax.setText("auto")
        self.configFile.setValue("yMax", self.lineEdit_yMax.text())
        self.parent.set_yMinMax(self.configFile.value("yMin"),self.configFile.value("yMax"))

        # self.lineEdit_yMin.setText(self.configFile.value("yMin"))

    def resetYMin(self):
        self.parent.enable_autoRange(True)
        self.lineEdit_yMin.setText("auto")
        self.configFile.setValue("yMin", self.lineEdit_yMin.text())
        self.parent.set_yMinMax(self.configFile.value("yMin"),self.configFile.value("yMax"))

        # self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def connectSlotsSignals(self):
        self.pushButton_apply.clicked.connect(self.applySettings)
        self.pushButton_ok.clicked.connect(self.closeSavePlotSettings)
        self.button_moveDown.clicked.connect(partial(self.sendMoveSignal, 'down'))
        self.button_moveLeft.clicked.connect(partial(self.sendMoveSignal, 'left'))
        self.button_moveRight.clicked.connect(partial(self.sendMoveSignal, 'right'))
        self.button_moveUp.clicked.connect(partial(self.sendMoveSignal, 'up'))

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
    def __init__(self, parent = None):
        super(GridPlotLayout, self).__init__(parent)
        spacing = 6
        self.setContentsMargins(spacing,spacing,spacing,spacing)
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
            newCol = oldCol+1
        elif 'down' == direction:
            newRow = oldRow + 1
            newCol = oldCol
        else:
            raise ValueError('moveWidget(self, widg, direction): argument 2 has invalid \'str\' value (up, left, right, down)')


        try:
            displacedWidg = self.widgetAtPosition(newRow,newCol)
            if displacedWidg == None:
                return AttributeError
            self.removeWidget(widg)
            self.removeWidget(displacedWidg)
            self.addWidget(widg, newRow, newCol)
            self.addWidget(displacedWidg, oldRow, oldCol)
        except AttributeError:
            pass

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