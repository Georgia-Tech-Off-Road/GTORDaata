from DataAcquisition import data
from PyQt5 import QtWidgets, uic
# from PyQt5.QtCore import QSettings
from Scenes import DAATAScene
from Utilities.CustomWidgets.Plotting import CustomPlotWidget, GridPlotLayout
from Utilities.Popups.generic_popup import GenericPopup
from datetime import time as datetime_time
from functools import partial
import logging
import os
import pandas
import pyqtgraph as pg

# Default plot configuration for pyqtgraph
pg.setConfigOption('background', 'w')   # white
pg.setConfigOption('foreground', 'k')   # black

# load the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'data_collection_preview.ui'))
logger = logging.getLogger("DataCollectionPreview")


class DataCollectionPreview(DAATAScene, uiFile):
    def __init__(self, initial_data_filepath: str = None):
        super().__init__()
        self.aborted = False

        # initial_data_filepath = "C:\\Users\\afari\\AppData\\Local\\GTOffRoad\\Downloads\\a.csv"
        if not initial_data_filepath \
                or not os.path.exists(initial_data_filepath):
            GenericPopup("Data CSV file does not exist",
                         "Unable to initialize graphs due to missing file.")
            self.aborted = True
            self.close()
            return
        if initial_data_filepath[-4:] != ".csv":
            GenericPopup("Data file not of CSV type",
                         "Only .csv files supported")
            self.aborted = True
            self.close()
            return
        self.setupUi(self)
        self.hide()

        # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)
        self.update_period = 3

        self.graph_objects = dict()
        self.checkbox_objects = dict()
        with open(initial_data_filepath) as f:
            first_line = f.readline()
            self.currentKeys = first_line[:-1].split(",")[1:]

        self.gridPlotLayout = GridPlotLayout(self.scrollAreaWidgetContents)
        self.gridPlotLayout.setObjectName("gridPlotLayout")
        self.scrollAreaWidgetContents.setLayout(self.gridPlotLayout)

        self.collection_start_time = None
        self.__create_sensor_checkboxes()
        self.__create_graph_dimension_combo_box()
        self.__create_graphs()
        self.__create_grid_plot_layout()

        from MainWindow import is_data_collecting
        self.is_data_collecting = is_data_collecting

        self.__connect_slots_and_signals()
        # self.configFile = QSettings('DAATA', 'data_collection')
        # self.configFile.clear()
        # self.__load_settings()

        self.__initialize_graphs(initial_data_filepath)
        self.show()

    def update_passive(self):
        pass

    def update_active(self):
        pass

    def __initialize_graphs(self, initial_data_filepath: str):
        csv_data = pandas.read_csv(initial_data_filepath)
        time_array = csv_data.time_internal_seconds.values

        for sensor in csv_data.columns.values[1:]:
            self.checkbox_objects[sensor].setChecked(True)
            csv_data = pandas.read_csv(initial_data_filepath)
            sensor_array = getattr(csv_data, sensor).values
            self.graph_objects[sensor].initialize_values(
                time_array, sensor_array)
        self.__create_grid_plot_layout()

        test_duration = csv_data.time_internal_seconds.values[-1]
        if test_duration > 86400:
            self.label_timeElapsed.setText("> 1 day")
        else:
            test_duration = datetime_time(
                hour=int(test_duration % 86400 // 3600),
                minute=int(test_duration % 3600 // 60),
                second=int(test_duration % 60 // 1),
                microsecond=int(test_duration % 1 * 1e6))
            self.label_timeElapsed.setText(
                test_duration.strftime("%H:%M:%S.%f"))

    def __create_sensor_checkboxes(self):
        # Create a checkbox for each sensor in dictionary in
        # self.scrollAreaWidgetContents_2
        for key in self.currentKeys:
            self.checkbox_objects[key] = QtWidgets.QCheckBox(
                data.get_display_name(key), self.scrollAreaWidgetContents_2,
                objectName=key)
            self.gridLayout_2.addWidget(self.checkbox_objects[key])

        # Create a vertical spacer that forces checkboxes to the top
        spacerItem1 = QtWidgets.QSpacerItem(20, 1000000,
                                            QtWidgets.QSizePolicy.Minimum,
                                            QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1)

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

        leftMar, topMar, rightMar, botMar = self.gridPlotLayout\
            .getContentsMargins()
        hSpace = self.gridPlotLayout.horizontalSpacing()
        vSpace = self.gridPlotLayout.verticalSpacing()
        graphHeight = (self.scrollArea_graphs.height()
                       - topMar - botMar - vSpace * (max_rows - 1)) / max_rows

        if graphHeight < 20:
            # arbitrary height as produced in Faris's desktop
            graphHeight = 654.0

        for key in self.graph_objects.keys():
            if self.graph_objects[key].isVisible():
                try:
                    self.gridPlotLayout.removeWidget(self.graph_objects[key])
                    self.graph_objects[key].hide()
                except Exception:
                    print(key + " is " + self.graph_objects[key].isVisible())

        for key in self.checkbox_objects.keys():
            if self.checkbox_objects[key].isChecked():
                if col == max_cols:
                    col = 0
                    row += 1
                self.graph_objects[key].set_height(graphHeight)
                self.gridPlotLayout.addWidget((self.graph_objects[key]), row,
                                              col, 1, 1)
                self.graph_objects[key].show()

                col += 1

        self.spacerItem_gridPlotLayout = QtWidgets.QSpacerItem(
            20, 1000000, QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding)
        self.gridPlotLayout.addItem(self.spacerItem_gridPlotLayout)
        self.__update_sensor_count()

    def __create_graphs(self):
        for key in self.currentKeys:
            self.graph_objects[key] = CustomPlotWidget(
                key, parent=self.scrollAreaWidgetContents,
                layout=self.gridPlotLayout, graph_width_seconds=8)
            self.graph_objects[key].setObjectName(key)
            self.graph_objects[key].hide()

    def __update_sensor_count(self):
        self.active_sensor_count = sum(
            self.checkbox_objects[k].isChecked() for k in self.checkbox_objects)
        self.label_active_sensor_count.setText(
            f"({self.active_sensor_count}/{len(self.graph_objects)})")

    def __connect_slots_and_signals(self):
        for key in self.currentKeys:
            self.checkbox_objects[key].clicked.connect(
                self.__create_grid_plot_layout)

        self.comboBox_graphDimension.currentTextChanged.connect(
            self.__create_grid_plot_layout)

        ## connections to GridPlotLayout
        for key in self.graph_objects.keys():
            widget = self.graph_objects[key]
            settings = widget.button_settings.clicked.connect(partial(
                self.graph_objects[key].open_SettingsWindow))

    # --- Overridden event methods --- #
    def closeEvent(self, event=None):
        if event is not None:
            event.accept()


    # Archived code

    # def __save_settings(self):
    #     """
    #     This function will save the settings for a given scene to a config
    #     file so that they can be loaded in again the next time that the scene
    #     is opened (even if the entire GUI is restarted).
    #
    #     :return: None
    #     """
    #     self.configFile.setValue('graph_dimension',
    #                              self.comboBox_graphDimension.currentText())
    #     self.configFile.setValue('scrollArea_graphs_height',
    #                              self.scrollArea_graphs.height())
    #
    #     enabledSensors = []
    #     for key in self.graph_objects.keys():
    #         if self.checkbox_objects[key].isChecked():
    #             enabledSensors.append(key)
    #     self.configFile.setValue('enabledSensors', enabledSensors)
    #
    #     logger.debug("Data Collection config files saved")
    #     # self.debug_settings()
    #
    # def __load_settings(self):
    #     """
    #     This function loads in the previously saved settings.
    #
    #     :return: None
    #     """
    #     try:
    #         active_sensor_count = 0
    #         for key in self.configFile.value('enabledSensors'):
    #             print(key)
    #             self.checkbox_objects[key].setChecked(True)
    #             self.graph_objects[key].show()
    #             active_sensor_count = active_sensor_count + 1
    #             self.label_active_sensor_count.setText(
    #                 '(' + str(active_sensor_count) + '/' + str(len(self.graph_objects)) + ')')
    #     except TypeError or KeyError:
    #         logger.error("Possibly invalid key in config. May need to clear "
    #                      "config file using self.configFile.clear()")
    #         pass
    #
    #     self.comboBox_graphDimension.setCurrentText(self.configFile.value('graph_dimension'))
    #     # self.slot_graphDimension()
    #     self.__create_grid_plot_layout()
    #     logger.debug("Data Collection config files loaded")
    #     # self.debug_settings()
    #
    # def __debug_settings(self):
    #     """
    #     This method allows you to view the contents of what is currently
    #     stored in settings :return:
    #     """
    #     for key in self.configFile.allKeys():
    #         print(key + ":\t\t" + str(self.configFile.value(key)))
