from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSettings
from Scenes import DAATAScene
from Scenes.MultiDataGraph.MDG_init_props import MDGInitProps
from Utilities.CustomWidgets.Plotting import CustomPlotWidget, GridPlotLayout
from datetime import datetime, time as datetime_time
from functools import partial
from numpy import ndarray
from typing import Dict, List
import logging
import os
import pandas
import pyqtgraph as pg
from Utilities.GoogleDriveHandler import GoogleDriveHandler

# Default plot configuration for pyqtgraph
from Utilities.Popups.generic_popup import GenericPopup

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
    def __init__(self, initial_data_filepath: str, file_metadata: dict = None):
        super().__init__()

        if not initial_data_filepath \
                or not os.path.isfile(initial_data_filepath):
            GenericPopup("Data CSV file does not exist",
                         "Unable to initialize graphs due to missing file.")
            self.close()
            return
        if initial_data_filepath[-4:] != ".csv":
            GenericPopup("Data file not of CSV type",
                         "Only .csv files supported")
            self.close()
            return

        self.setupUi(self)
        self.hide()

        # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)
        self.update_period = 3

        self.graph_objects: Dict[int, CustomPlotWidget] = dict()
        self.READ_ONLY_INIT_VALUES: Dict[str, ndarray] = dict()
        self.init_x_sensor_name: str = ""
        self.init_y_sensor_names: List[str] = []

        self.gridPlotLayout = GridPlotLayout(self.scrollAreaWidgetContents)
        self.gridPlotLayout.setObjectName("gridPlotLayout")
        self.scrollAreaWidgetContents.setLayout(self.gridPlotLayout)
        self.collection_start_time: datetime = datetime.min

        self.__create_graph_dimension_combo_box()
        self.__initialize_scene(initial_data_filepath, file_metadata)

        self.__connect_slots_and_signals()
        self.configFile = QSettings('DAATA', 'MultiDataGraphPreview')
        self.configFile.clear()
        self.__load_settings()

    def __initialize_scene(self, initial_data_filepath: str,
                           file_metadata: dict = None) -> bool:
        csv_data: pandas.DataFrame = pandas.read_csv(initial_data_filepath)
        self.init_x_sensor_name: str = csv_data.columns.values[0]
        self.init_y_sensor_names: List[str] = list(csv_data.columns.values[1:])
        self.READ_ONLY_INIT_VALUES = {
            sensor: getattr(csv_data, sensor).values for sensor in
            csv_data.columns.values
        }

        date_str = GoogleDriveHandler.get_start_date_str(file_metadata)
        if not date_str:
            date_str = "<i>No date available</i>"
        if "time_internal_seconds" in csv_data.columns.values:
            test_duration = csv_data.time_internal_seconds.values[-1]
            if test_duration > 86400:
                self.label_timeElapsed.setText(f"{date_str}<br>> 1 day")
            else:
                test_duration = datetime_time(
                    hour=int(test_duration % 86400 // 3600),
                    minute=int(test_duration % 3600 // 60),
                    second=int(test_duration % 60 // 1),
                    microsecond=int(test_duration % 1 * 1e6))
                self.label_timeElapsed.setText(
                    test_duration.strftime(f"{date_str}<br>%H h %M m %S.%f s"))
        else:
            self.label_timeElapsed.setText("No duration detected")

        self.__addMDG(False)
        self.graph_objects[0].initialize_MDG_values()
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

    def __create_graph(self, key: int, x_sensor: str, y_sensors: List[str]):
        self.graph_objects.pop(key, None)
        MDG_init_props = MDGInitProps(x_sensor=x_sensor,
                                      y_sensors=y_sensors,
                                      read_only=True,
                                      initial_data_values=self.READ_ONLY_INIT_VALUES)
        self.graph_objects[key] = CustomPlotWidget(key,
                                                   parent=self.scrollAreaWidgetContents,
                                                   layout=self.gridPlotLayout,
                                                   graph_width_seconds=8,
                                                   MDG_init_props=MDG_init_props)
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

    def __addMDG(self, empty: bool = True):
        """
        Adds one more independent multi data graph to the scene
        """
        # increasing the MDG count text on GUI
        newMDGNumber = int(self.mdgNumber.text()) + 1
        self.mdgNumber.setText(str(newMDGNumber))

        # creating new MDG
        current_MDG_count = len(self.graph_objects)
        self.__create_graph(current_MDG_count, self.init_x_sensor_name,
                            self.init_y_sensor_names if not empty else [])

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
        latest_mdg_key = len(self.graph_objects) - 1
        self.gridPlotLayout.removeWidget(self.graph_objects[latest_mdg_key])
        self.graph_objects[latest_mdg_key].hide()
        del self.graph_objects[latest_mdg_key]
        self.__create_grid_plot_layout()

    def __connect_slots_and_signals(self):
        # for key in self.currentKeys:
        #     self.checkbox_objects[key].clicked.connect(self.create_grid_plot_layout)
        #     self.checkbox_objects[key].clicked.connect(self.save_settings)

        self.comboBox_graphDimension.currentTextChanged.connect(
            self.__create_grid_plot_layout)
        self.comboBox_graphDimension.currentTextChanged.connect(
            self.__save_settings)

        # leave the lambda; remove it and it will break
        self.plusMDGButton.clicked.connect(lambda: self.__addMDG())
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
                    f'({active_sensor_count}/{len(self.graph_objects)})')
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

    # --- Overridden event methods --- #
    def closeEvent(self, event=None):
        self.__save_settings()
