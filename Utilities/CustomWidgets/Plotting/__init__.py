from DataAcquisition import data
from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QGridLayout
from Scenes.MultiDataGraph.MDG_init_props import MDGInitProps
from Utilities.CustomWidgets.Plotting.plot_settings import PlotSettingsDialog, \
    PlotSettingsDialogMDG
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
    def __init__(self, sensor_name: str, parent=None,
                 enable_scroll: Tuple[bool, bool] = (False, False),
                 MDG_init_props: MDGInitProps = None,
                 is_read_only: bool = False, **kwargs):
        super().__init__()
        self.setupUi(self)

        # local variables instantiation
        self.sensor_name = sensor_name
        self.__is_read_only = is_read_only
        self.__enable_multi_plot = (MDG_init_props is not None)
        self.__is_paused: bool = False

        # MDG-only props
        if self.__enable_multi_plot:
            self.__MDG_init_props: MDGInitProps = MDGInitProps()
            self.__mdg_x_sensor: str = ""
            self.__mdg_y_sensors: List[str] = []
            self.__INIT_SENSOR_VALUES: Dict[str, numpy.ndarray] = dict()
            self.__mdg_is_line_graph: bool = True

        # aiming to get this as close to the real frequency
        self.__seconds_in_view: float = kwargs.get("seconds_in_view", 10)
        # Number of value to show on the x-axis
        self.__sampling_freq = 57.9710144928  # Hz, updated passively
        self.__graph_width: int = int(
            self.__seconds_in_view * self.__sampling_freq)
        # the layout object the plot is embedded within
        self.embedLayout = kwargs.get("layout", None)
        # Frequency of values to show (if set to 5 will show every 5th value
        # collected)
        self.__show_width = kwargs.get("show_width", 5)
        # Row and column span of plot on the grid
        self.__rowSpan = kwargs.get("rowspan", 1)
        self.__rowSpan = kwargs.get("columnspan", 1)
        # self.plotWidget used in plot_settings.py
        self.plotWidget: pg.PlotWidget = self.plotWidget
        self.__multi_plots: dict = dict()

        self.__setup(sensor_name, enable_scroll, MDG_init_props)

        self.__configFile = QtCore.QSettings('DAATA_plot', self.objectName())
        self.__configFile.clear()
        self.__loadStylesheet()
        self.__loadSettings()

    def __setup(self, sensor_name: str,
                enable_scroll: Tuple[bool, bool] = (False, False),
                MDG_init_props: MDGInitProps = None):
        pg.setConfigOption('foreground', 'w')
        self.setObjectName(str(sensor_name))

        if self.__enable_multi_plot:
            self.__MDG_init_props = MDG_init_props
            self.setObjectName("MDG #" + str(sensor_name))
            self.__mdg_is_line_graph = MDG_init_props.is_line_graph
            # sets the current x and y sensors plotted on the graph
            self.__mdg_x_sensor: str = MDG_init_props.x_sensor
            self.__mdg_y_sensors: List[str] = \
                MDG_init_props.y_sensors if MDG_init_props.y_sensors[:] else []
            if self.__is_read_only:
                self.__INIT_SENSOR_VALUES: Dict[str, numpy.ndarray] = \
                    MDG_init_props.initial_data_values
                # by default limits the max number of sensors plotted
                self.__mdg_y_sensors = self.__mdg_y_sensors[:5]
            # set title and axes
            self.plotWidget.setLabels(
                bottom="Time (s)" if self.__mdg_x_sensor == TIME_OPTION else "",
                title=str(self.objectName()))
        else:
            # set title and axes
            self.plotWidget.setLabels(
                left=f"{str(data.get_display_name(sensor_name))} "
                     f"({str(data.get_unit_short(sensor_name))})",
                bottom="Time (s)",
                title=f"{str(data.get_display_name(sensor_name))} Graph")

        self.setMinimumSize(QtCore.QSize(200, 200))
        self.setMaximumSize(QtCore.QSize(16777215, 400))

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHorizontalStretch(4)
        self.setSizePolicy(sizePolicy)

        self.plotWidget.setMouseEnabled(enable_scroll[0], enable_scroll[1])

        # adds a legend describing what each line represents based on the 'name'
        self.plotWidget.addLegend()

        self.plotWidget.showGrid(x=True, y=True, alpha=.2)
        self.plotWidget.setBackground("#343538")  # dark gray

        if self.__enable_multi_plot:
            self.__create_multi_graphs()
        else:
            valueArray = numpy.zeros(self.__graph_width)
            self.plot: pg.PlotDataItem = \
                self.plotWidget.plot(valueArray, name=data.get_display_name(
                    self.sensor_name), pen=pg.mkPen(color="#00ff00"), width=1)

        self.plotWidget.getAxis('left').setTextPen('w')
        self.plotWidget.getAxis('left').setPen('w')
        self.plotWidget.getAxis('bottom').setTextPen('w')
        self.plotWidget.getAxis('bottom').setPen('w')

    def __loadStylesheet(self):
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

    def set_graphWidth(self, seconds: str):
        # used in plot_settings.py
        try:
            self.__seconds_in_view = float(seconds)
            self.__graph_width = int(
                self.__seconds_in_view * self.__sampling_freq)
        except (ValueError, TypeError):
            self.__graph_width = int(
                self.__seconds_in_view * self.__sampling_freq)

    def set_yMinMax(self, yMin, yMax):
        # used in plot_settings.py
        self.plotWidget.setYRange(0, 100)
        self.enable_autoRange(True)
        self.plotWidget.setLimits(yMin=None, yMax=None)
        if yMax != 'auto' and yMin == 'auto':
            self.plotWidget.setLimits(yMax=int(yMax))
        if yMin != 'auto' and yMax == 'auto':
            self.plotWidget.setLimits(yMin=int(yMin))
        if yMin != 'auto' and yMax != 'auto':
            # self.plotWidget.setLimits(yMin = int(yMin), yMax = int(yMax))
            # Set strict visible range
            self.plotWidget.setYRange(int(yMin), int(yMax), padding=0)
        if yMin == 'auto' and yMax == 'auto':
            self.plotWidget.setLimits(yMin=None, yMax=None)
            self.enable_autoRange(True)
            # self.plotWidget.enableAutoRange(axis='y')
            # self.plotWidget.setAutoVisible(y=True)

    def enable_autoRange(self, enable=True):
        # used in plot_settings.py
        self.plotWidget.setAutoVisible(y=True)
        self.plotWidget.enableAutoRange(enable)

    def set_height(self, height):
        self.setMinimumSize(QtCore.QSize(200, height))
        self.setMaximumSize(QtCore.QSize(16777215, height))

    def initialize_values(self, timeArray: list, valueArray: list):
        self.plot.setData(timeArray, valueArray)

    def initialize_MDG_values(self):
        if self.__mdg_is_line_graph:
            for sensor in self.__mdg_y_sensors:
                self.__multi_plots[sensor].setData(
                    self.__INIT_SENSOR_VALUES[self.__mdg_x_sensor],
                    self.__INIT_SENSOR_VALUES[sensor])
        else:
            for sensor in self.__mdg_y_sensors:
                self.__multi_plots[sensor].addPoints(
                    self.__INIT_SENSOR_VALUES[self.__mdg_x_sensor],
                    self.__INIT_SENSOR_VALUES[sensor])

    @property
    def seconds_in_view(self) -> float:
        # Used in another plot_settings.py implicitly, do not delete
        return self.__seconds_in_view

    def update_graph(self):
        if self.__enable_multi_plot:
            self.__update_multi_graphs()
        else:
            index_time = data.get_most_recent_index()
            index_sensor = data.get_most_recent_index(
                sensor_name=self.sensor_name)
            # collects all value and time data from time 0 to present
            valueArray = data.get_values(self.sensor_name, index_sensor,
                                         index_sensor + 1)
            timeArray = data.get_values("time_internal_seconds", index_time,
                                        index_time + 1)
            self.plot.setData(timeArray, valueArray)
            self.plotWidget.setLimits(
                xMin=timeArray[-1] - self.__seconds_in_view, xMax=timeArray[-1])

    @staticmethod
    def __create_pen_brush(color_choice=0, create_pen=True):
        """
        Returns a pyqtgraph 'pg' pen or brush object of a color depending on
        the color_choice input integer. Colors should be colorblind-friendly
        :param color_choice: an integer to choose which color, value will be
        reduced modulated (%) to the number of possible colors
        :param create_pen: True if you want to return a pen object, False if you
        want a brush
        :return: A brush or a pen depending on create_pen.
        """
        # 10 colors = green, red, blue, orange, purple,
        # black, pink, brown, gray, blue-green
        COLORS = ["#00FF00",  # Green
                  "#FFA500",  # Web orange
                  "#ADD8E6",  # Light Blue
                  "#00FF00",  # Blue
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

    def update_graph_width(self, new_sampling_freq):
        self.__sampling_freq = new_sampling_freq
        self.__graph_width = int(self.__seconds_in_view * self.__sampling_freq)

    def __create_multi_graphs(self):
        # clears all plots listed made after x-y sensor selection changes
        self.__multi_plots.clear()

        # set title and axes
        self.plotWidget.setLabels(
            bottom="Time (s)" if self.__mdg_x_sensor == TIME_OPTION else "",
            title=self.objectName())

        valueArray = numpy.zeros(self.__graph_width)

        if self.__mdg_is_line_graph:
            # creates the individual line plots on the graph and adds them to a
            # list
            for sensor_i, sensor in enumerate(self.__mdg_y_sensors):
                pen = self.__create_pen_brush(sensor_i, True)
                plot = self.plotWidget.plot(valueArray,
                                            name=data.get_display_name(sensor),
                                            pen=pen,
                                            width=1)
                self.__multi_plots[sensor] = plot
        else:
            # creates the individual line plots on the graph and adds them to a
            # list
            for sensor_i, sensor in enumerate(self.__mdg_y_sensors):
                brush = self.__create_pen_brush(sensor_i, False)
                scatter = pg.ScatterPlotItem(size=4,
                                             name=data.get_display_name(sensor),
                                             brush=brush)
                self.plotWidget.addItem(scatter)
                self.__multi_plots[sensor] = scatter

    def __update_multi_graphs(self) -> None:
        """
        Updates all line plots contained in list self.__multi_plots according to
        which x-y sensors are selected
        :return: None
        """
        if self.__mdg_is_line_graph:
            for sensor_i, sensor in enumerate(self.__mdg_y_sensors):
                index_time = data.get_most_recent_index()
                index_sensor = data.get_most_recent_index(sensor_name=sensor)
                valueArrayY = data.get_values(sensor, index_sensor,
                                              self.__graph_width)
                if self.__mdg_x_sensor == TIME_OPTION:
                    timeArray = data.get_values("time_internal_seconds",
                                                index_time, self.__graph_width)
                    self.__multi_plots[sensor].setData(timeArray, valueArrayY)
                else:
                    index_sensorX = data.get_most_recent_index(
                        sensor_name=self.__mdg_x_sensor)
                    valueArrayX = data.get_values(self.__mdg_x_sensor,
                                                  index_sensorX,
                                                  self.__graph_width)
                    self.__multi_plots[sensor].setData(valueArrayX, valueArrayY)
        else:
            for sensor_i, sensor in enumerate(self.__mdg_y_sensors):
                index_time = data.get_most_recent_index()
                index_sensor = data.get_most_recent_index(sensor_name=sensor)
                valueArrayY = data.get_values(sensor, index_sensor,
                                              self.__graph_width)
                if self.__mdg_x_sensor == TIME_OPTION:
                    # get time values
                    timeArray = data.get_values("time_internal_seconds",
                                                index_time, self.__graph_width)
                    # add points
                    self.__multi_plots[sensor].setData(timeArray, valueArrayY)
                else:
                    index_sensorX = data.get_most_recent_index(
                        sensor_name=self.__mdg_x_sensor)
                    valueArrayX = data.get_values(self.__mdg_x_sensor,
                                                  index_sensorX,
                                                  self.__graph_width)
                    self.__multi_plots[sensor].addPoints(valueArrayX,
                                                         valueArrayY)

    def update_xy_sensors(self, x_sensor: str = "",
                          y_sensors: List[str] = None) -> None:
        """
        Updates the current plotted x- and y-sensors, if provided. Then, clears
        all current plots for new data collection.
        :param x_sensor: x-sensor to be plotted
        :param y_sensors: y-sensors to be plotted together
        :return: None
        """
        # used in plot_settings.py
        if x_sensor:
            self.__mdg_x_sensor = x_sensor
        if y_sensors:
            self.__mdg_y_sensors = y_sensors
        self.__create_multi_graphs()
        if self.__is_read_only:
            self.initialize_MDG_values()

    def open_SettingsWindow(self):
        view_range_x = self.plotWidget.viewRange()[0]
        new_seconds_range = round(view_range_x[1] - view_range_x[0], 3)
        if self.__enable_multi_plot:
            if self.__is_read_only:
                available_sensors = list(
                    self.__MDG_init_props.initial_data_values.keys())
            else:
                available_sensors = data.get_sensors(is_plottable=True,
                                                     is_connected=True)
            PlotSettingsDialogMDG(self, self.embedLayout, self.__mdg_x_sensor,
                                  self.__mdg_y_sensors,
                                  self.__mdg_is_line_graph,
                                  self.__is_read_only,
                                  available_sensors,
                                  new_seconds_range=new_seconds_range)
        else:
            PlotSettingsDialog(self, self.embedLayout, self.sensor_name,
                               new_seconds_range=new_seconds_range,
                               is_read_only=self.__is_read_only)

    def toggle_pause_state(self):
        self.__is_paused = not self.__is_paused
        if self.__is_paused:
            self.plotWidget.setLimits(xMin=None, xMax=None)
        else:
            if self.__enable_multi_plot:
                last_index = data.get_most_recent_index(self.__mdg_x_sensor)
                last_x = data.get_value(self.__mdg_x_sensor, last_index)
            else:
                last_index = data.get_most_recent_index()
                last_x = data.get_value("time_internal_seconds", last_index)
            self.plotWidget.setLimits(xMin=last_x - self.__seconds_in_view,
                                      xMax=last_x)

    def connectSignalSlots(self):
        self.button_settings.clicked.connect(
            partial(self.open_SettingsWindow, self))

    @property
    def mdg_is_line_graph(self) -> bool:
        # used in plot_settings.py
        return self.__mdg_is_line_graph

    @property
    def is_paused(self) -> bool:
        return self.__is_paused

    def update_plot_type(self, is_line_plot: bool):
        # used in plot_settings.py
        self.__mdg_is_line_graph = is_line_plot

    def __saveSettings(self):
        pass

    def __loadSettings(self):
        yMin = self.__configFile.value("yMin")
        yMax = self.__configFile.value("yMax")
        if yMin is None:
            self.__configFile.setValue("yMin", "auto")
            yMin = "auto"
        if yMax is None:
            self.__configFile.setValue("yMax", "auto")
            yMax = "auto"
        saved_graph_seconds = self.__configFile.value("seconds_in_view")
        if saved_graph_seconds:
            self.set_graphWidth(saved_graph_seconds)
        else:
            self.__configFile.setValue("seconds_in_view",
                                       str(self.__seconds_in_view))

        self.set_yMinMax(yMin, yMax)

    # allow color scheme of class to be changed by CSS stylesheets
    def paintEvent(self, pe):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()
        s.drawPrimitive(QtGui.QStyle.PE_Widget, opt, p, self)


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
