from DataAcquisition import data
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSettings
from Scenes import DAATAScene
from Utilities.CustomWidgets.Plotting import CustomPlotWidget, GridPlotLayout
from datetime import datetime
from functools import partial
import DataAcquisition
import logging
import os
import pyqtgraph as pg

# Default plot configuration for pyqtgraph
pg.setConfigOption('background', 'w')  # white
pg.setConfigOption('foreground', 'k')  # black

# load the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'MultiDataGraphPreview.ui'))

logger = logging.getLogger("MultiDataGraph")


# Todo List      ####################################
# add warning dialog if trying to start recording data while teensy is not
# plugged in (checked with data.is_connected)


class MultiDataGraphPreview(DAATAScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.hide()

        # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)
        self.update_period = 3

        self.graph_objects = dict()
        self.connected_sensors = []
        self.update_connected_sensors()
        self.y_sensors = []

        self.line_graph = "line_graph"
        self.scatter_plot = "scatter_plot"

        self.gridPlotLayout = GridPlotLayout(self.scrollAreaWidgetContents)
        self.gridPlotLayout.setObjectName("gridPlotLayout")
        self.scrollAreaWidgetContents.setLayout(self.gridPlotLayout)
        self.collection_start_time: datetime = datetime.min

        self.create_graph_dimension_combo_box()
        self.addMDG()

        from MainWindow import is_data_collecting

        self.connect_slots_and_signals()
        self.configFile = QSettings('DAATA', 'MultiDataGraph')
        self.configFile.clear()
        self.load_settings()

    def create_graph_dimension_combo_box(self):
        """
        This function creates the drop down box that allows changing the
        number of graphs on the screen.

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
            self.gridPlotLayout.addWidget((self.graph_objects[key]), row, col,
                                          1, 1)
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
                                                   enable_multi_plot=True,
                                                   plot_type=self.line_graph)
        # activate settings button
        widget = self.graph_objects[key]
        settings = widget.button_settings.clicked.connect(
            partial(self.graph_objects[key].open_SettingsWindow))

        self.graph_objects[key].show()
        self.create_grid_plot_layout()



    def update_sensor_count(self):
        self.active_sensor_count = 0
        # for key in self.checkbox_objects.keys():
        #     if self.checkbox_objects[key].isVisible():
        #         if self.checkbox_objects[key].isChecked():
        #             self.active_sensor_count = self.active_sensor_count + 1
        self.label_active_sensor_count.setText(
            '(' + str(self.active_sensor_count) + '/' + str(
                len(self.graph_objects)) + ')')

    def update_graphs(self):
        for key in self.graph_objects.keys():
            self.graph_objects[key].update_graph()

    def update_time_elapsed(self):
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

    def update_connected_sensors(self):
        """
        Will update the sensor checkboxes if new sensors are added.
        :return: None
        """
        connected_sensors = data.get_sensors(is_plottable=True,
                                             is_connected=True)
        self.connected_sensors = connected_sensors

    def update_active(self):
        pass

    def update_passive(self):
        pass

    def addMDG(self):
        """
        Adds one more independent multi data graph to the scene
        """
        # increasing the MDG count text on GUI
        newMDGNumber = int(self.mdgNumber.text()) + 1
        self.mdgNumber.setText(str(newMDGNumber))

        # creating new MDG
        current_MDG_count = len(self.graph_objects)
        self.create_graph(current_MDG_count)

    def removeMDG(self):
        """
        Removes the most recently added multi data graph from the scene
        """
        # decreasing the MDG count text on GUI
        newMDGNumber = int(self.mdgNumber.text()) - 1
        if newMDGNumber <= 0:
            return
        self.mdgNumber.setText(str(newMDGNumber))

        # deleting most recently added MDG
        current_MDG_count = len(self.graph_objects)
        del self.graph_objects[current_MDG_count - 1]
        self.create_grid_plot_layout()

    def connect_slots_and_signals(self):
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
                    '(' + str(active_sensor_count) + '/' + str(
                        len(self.graph_objects)) + ')')
        except TypeError or KeyError:
            logger.error(
                "Possibly invalid key in config. May need to clear config "
                "file using self.configFile.clear()")
            pass

        self.comboBox_graphDimension.setCurrentText(
            self.configFile.value('graph_dimension'))
        logger.debug("Data Collection config files loaded")
        # self.debug_settings()

    def debug_settings(self):
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
        self.save_settings()
        self.window().setWindowTitle('closed tab')
