from DataAcquisition import data
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSettings
from Scenes import DAATAScene
from Scenes.MultiDataGraph.MDG_init_props import MDGInitProps
from Utilities.CustomWidgets.Plotting import CustomPlotWidget, GridPlotLayout
from datetime import datetime
from functools import partial
from typing import Dict, List
import DataAcquisition
import logging
import os
import pyqtgraph as pg

# Default plot configuration for pyqtgraph
pg.setConfigOption('background', 'w')  # white
pg.setConfigOption('foreground', 'k')  # black

# load the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'MultiDataGraph.ui'))

logger = logging.getLogger("MultiDataGraph")


# Todo List      ####################################
# add warning dialog if trying to start recording data while teensy is not
# plugged in (checked with data.is_connected)


class MultiDataGraph(DAATAScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.hide()

        # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)
        self.update_period = 3

        self.graph_objects: Dict[int, CustomPlotWidget] = dict()
        self.connected_sensors: List[str] = []
        self.__update_connected_sensors()
        self.y_sensors: List[str] = []

        self.gridPlotLayout = GridPlotLayout(self.scrollAreaWidgetContents)
        self.gridPlotLayout.setObjectName("gridPlotLayout")
        self.scrollAreaWidgetContents.setLayout(self.gridPlotLayout)
        self.collection_start_time: datetime = datetime.min

        from MainWindow import is_data_collecting
        self.is_data_collecting = is_data_collecting

        self.__create_graph_dimension_combo_box()
        self.__addMDG()

        self.__connect_slots_and_signals()
        self.configFile = QSettings('DAATA', 'MultiDataGraph')
        self.configFile.clear()
        self.__load_settings()

    def __create_graph_dimension_combo_box(self):
        """
        This function creates the drop-down box that allows changing the
        number of graphs on the screen.

        :return: None
        """
        max_rows = 4
        max_cols = 3
        for row in range(1, max_rows + 1):
            for col in range(1, max_cols + 1):
                self.comboBox_graphDimension.addItem("{0}x{1}".format(row, col))

    def __create_grid_plot_layout(self):
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
            self.gridPlotLayout.addWidget((self.graph_objects[key]), row, col,
                                          1, 1)
            self.graph_objects[key].show()
            col += 1

        self.spacerItem_gridPlotLayout = \
            QtWidgets.QSpacerItem(20, 1000000, QtWidgets.QSizePolicy.Minimum,
                                  QtWidgets.QSizePolicy.Expanding)
        self.gridPlotLayout.addItem(self.spacerItem_gridPlotLayout)

    def __create_graph(self, key: int):
        self.graph_objects.pop(key, None)
        MDG_initial_props = MDGInitProps(y_sensors=self.connected_sensors[:3])
        self.graph_objects[key] = CustomPlotWidget(str(key),
                                                   parent=self.scrollAreaWidgetContents,
                                                   layout=self.gridPlotLayout,
                                                   graph_width_seconds=8,
                                                   MDG_init_props=MDG_initial_props)

        self.graph_objects[key].show()
        self.__create_grid_plot_layout()

    def __slot_data_collecting_state_change(self):
        if self.button_display.isChecked():
            self.__reset_all()
            self.collection_start_time = datetime.now()
            self.indicator_onOrOff.setText("On")
            self.indicator_onOrOff.setStyleSheet("color: green;")
            self.button_display.setStyleSheet("background-color: '#32CD32';")
            self.button_display.setText("Stop Collecting Data")
            self.is_data_collecting.set()
        else:
            self.indicator_onOrOff.setText("Off")
            self.indicator_onOrOff.setStyleSheet("color: red;")
            self.button_display.setText("Start Collecting Data")
            self.button_display.setStyleSheet("background-color:red;")
            self.is_data_collecting.clear()
            self.popup_dataSaveLocation("MultiDataGraph",
                                        self.collection_start_time)

    def __reset_all(self):
        data.reset_hard()
        for graph in self.graph_objects.values():
            graph.plotWidget.clear()
            graph.update_xy_sensors()
        self.__create_grid_plot_layout()

    def __update_graphs(self):
        for key in self.graph_objects.keys():
            self.graph_objects[key].update_graph()

    def __update_time_elapsed(self):
        """
        This function updates the timer that is displayed in the layout that
        indicates how long a test has been running for.

        :return: None
        """
        try:
            seconds_elapsed = DataAcquisition.data.get_value(
                "time_internal_seconds",
                DataAcquisition.data.get_most_recent_index())
            seconds_elapsed_int = int(seconds_elapsed)
            hours_elapsed = int(seconds_elapsed_int / 3600)
            minutes_elapsed = int(
                (seconds_elapsed_int - hours_elapsed * 3600) / 60)
            seconds_elapsed = seconds_elapsed % 60
            format_time = "{hours:02d}:{minutes:02d}:{seconds:05.2f}"
            str_time = format_time.format(hours=hours_elapsed,
                                          minutes=minutes_elapsed,
                                          seconds=seconds_elapsed)
            self.label_timeElapsed.setText(str_time)
        except TypeError:
            pass

    def __update_connected_sensors(self):
        """
        Will update the sensor checkboxes if new sensors are added.
        :return: None
        """
        self.connected_sensors = data.get_sensors(is_plottable=True,
                                                  is_connected=True)

    def update_active(self):
        """
        This function will update only if the Data Collection tab is the
        current tab. This function will get called at whatever frequency
        self.update_freq is set at. It is called via the update_all function
        from the MainWindow.

        :return: None
        """
        if self.is_data_collecting.is_set():
            self.__update_graphs()
            self.__update_time_elapsed()

    def update_passive(self):
        self.__update_connected_sensors()
        self.label_active_sensor_count.setText(str(len(self.connected_sensors)))

    def __addMDG(self):
        """
        Adds one more independent multi data graph to the scene
        """
        # increasing the MDG count text on GUI
        newMDGNumber = int(self.mdgNumber.text()) + 1
        self.mdgNumber.setText(str(newMDGNumber))

        # creating new MDG
        current_MDG_count = len(self.graph_objects)
        self.__create_graph(current_MDG_count)

        self.is_data_collecting.set()

    def __removeMDG(self):
        """
        Removes the most recently added multi data graph from the scene
        """
        # decreasing the MDG count text on GUI
        newMDGNumber = int(self.mdgNumber.text()) - 1
        if newMDGNumber < 0:
            return
        self.mdgNumber.setText(str(newMDGNumber))

        # deleting most recently added MDG
        latest_mdg_key = len(self.graph_objects) - 1
        self.gridPlotLayout.removeWidget(self.graph_objects[latest_mdg_key])
        self.graph_objects[latest_mdg_key].hide()
        del self.graph_objects[latest_mdg_key]
        self.__create_grid_plot_layout()

        if newMDGNumber == 0:
            self.is_data_collecting.clear()

    def __connect_slots_and_signals(self):
        self.button_display.clicked.connect(
            self.__slot_data_collecting_state_change)

        # for key in self.currentKeys:
        #     self.checkbox_objects[key].clicked.connect(self.create_grid_plot_layout)
        #     self.checkbox_objects[key].clicked.connect(self.save_settings)

        self.comboBox_graphDimension.currentTextChanged.connect(
            self.__create_grid_plot_layout)
        self.comboBox_graphDimension.currentTextChanged.connect(
            self.__save_settings)

        self.plusMDGButton.clicked.connect(self.__addMDG)
        self.minusMDGButton.clicked.connect(self.__removeMDG)

    def __save_settings(self):
        """
        This function will save the settings for a given scene to a config
        file so that they can be loaded in again the next time that the scene
        is opened (even if the entire GUI is restarted).

        :return: None
        """
        self.configFile.setValue('graph_dimension',
                                 self.comboBox_graphDimension.currentText())
        self.configFile.setValue('scrollArea_graphs_height',
                                 self.scrollArea_graphs.height())

        logger.debug("Data Collection config files saved")
        # self.debug_settings()

    def __load_settings(self):
        """
        This function loads in the previously saved settings.

        :return: None
        """
        self.comboBox_graphDimension.setCurrentText(
            self.configFile.value('graph_dimension'))
        logger.debug("Data Collection config files loaded")
        # self.debug_settings()

    def __debug_settings(self):
        """
        This method allows you to view the contents of what is currently
        stored in settings :return:
        """
        for key in self.configFile.allKeys():
            print(key + ":\t\t" + str(self.configFile.value(key)))

    # --- imported methods --- #
    from Utilities.DataExport.dataSaveLocation import popup_dataSaveLocation

    # --- Overridden event methods --- #
    def closeEvent(self, event=None):
        self.__save_settings()
