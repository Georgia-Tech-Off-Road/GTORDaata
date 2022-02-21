from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSettings
from Scenes import DAATAScene
from Utilities.CustomWidgets.Plotting import CustomPlotWidget, GridPlotLayout
from datetime import datetime
from functools import partial
from typing import Dict, List
import logging
import os
import pandas
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
    def __init__(self,
                 initial_data_filepath: str = r"C:\Users\afari\Dropbox (GaTech)\My PC (DESKTOP-22CBLLG)\Downloads\2022-02-20_16-27-02 MultiDataGraph.csv"):
        super().__init__()
        self.setupUi(self)
        self.hide()

        # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)
        self.update_period = 3

        self.graph_objects: Dict[int, CustomPlotWidget] = dict()
        self.y_sensors: List[str] = []

        self.line_graph = "line_graph"
        self.scatter_plot = "scatter_plot"

        self.gridPlotLayout = GridPlotLayout(self.scrollAreaWidgetContents)
        self.gridPlotLayout.setObjectName("gridPlotLayout")
        self.scrollAreaWidgetContents.setLayout(self.gridPlotLayout)
        self.collection_start_time: datetime = datetime.min

        self.__create_graph_dimension_combo_box()
        self.__initialize_graphs(initial_data_filepath)

        self.__connect_slots_and_signals()
        self.configFile = QSettings('DAATA', 'MultiDataGraphPreview')
        self.configFile.clear()
        self.__load_settings()

    def __initialize_graphs(self, initial_data_filepath: str) -> bool:
        csv_data = pandas.read_csv(initial_data_filepath)
        init_x_sensor_name: str = csv_data.columns.values[0]
        init_y_sensor_names: List[str] = csv_data.columns.values[1:]
        self.__addMDG(init_x_sensor_name, init_y_sensor_names)

        x_sensor_array: List[float] = getattr(csv_data,
                                              init_x_sensor_name).values
        y_sensor_arrays: List[List[float]] = [getattr(csv_data, y_sensor).values
                                              for y_sensor in
                                              init_y_sensor_names]
        self.graph_objects[0].initialize_MDG_values(x_sensor_array,
                                                    y_sensor_arrays)
        self.__create_grid_plot_layout()
        return False

    def __create_graph_dimension_combo_box(self):
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
            except Exception:
                print(f"{key} is {self.graph_objects[key].isVisible()}")

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

    def __create_graph(self, key: int, x_sensor: str = "",
                       y_sensors: List[str] = None):
        self.graph_objects.pop(key, None)
        self.graph_objects[key] = CustomPlotWidget(key,
                                                   parent=self.scrollAreaWidgetContents,
                                                   layout=self.gridPlotLayout,
                                                   graph_width_seconds=8,
                                                   enable_multi_plot=True,
                                                   plot_type=self.line_graph,
                                                   mdg_x_sensor=x_sensor,
                                                   mdg_y_sensors=y_sensors)
        # activate settings button
        widget = self.graph_objects[key]
        settings = widget.button_settings.clicked.connect(
            partial(self.graph_objects[key].open_SettingsWindow))

        self.graph_objects[key].show()
        self.__create_grid_plot_layout()

    def update_active(self):
        pass

    def update_passive(self):
        pass

    def __addMDG(self, x_sensor: str = "", y_sensors: List[str] = None):
        """
        Adds one more independent multi data graph to the scene
        """
        # increasing the MDG count text on GUI
        newMDGNumber = int(self.mdgNumber.text()) + 1
        self.mdgNumber.setText(str(newMDGNumber))

        # creating new MDG
        current_MDG_count = len(self.graph_objects)
        self.__create_graph(current_MDG_count, x_sensor, y_sensors)

    def __removeMDG(self):
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
        self.__create_grid_plot_layout()

    def __connect_slots_and_signals(self):
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
        self.window().setWindowTitle('closed tab')
