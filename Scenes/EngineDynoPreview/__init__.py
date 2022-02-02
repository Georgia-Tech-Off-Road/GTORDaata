from PyQt5 import uic, QtGui
from PyQt5.QtCore import QSettings
from datetime import time as datetime_time, datetime
import os
import pandas

from DataAcquisition import DerivedSensors
from DataAcquisition import data
from Scenes import DAATAScene
from Utilities.CustomWidgets.Plotting import CustomPlotWidget
from Utilities.Popups.generic_popup import GenericPopup
import DataAcquisition
import logging
import pyqtgraph as pg

# Default plot configuration for pyqtgraph
pg.setConfigOption('background', 'w')   # white
pg.setConfigOption('foreground', 'k')   # black

# load the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'engine_dyno_preview.ui'))

logger = logging.getLogger("EngineDynoPreview")


class EngineDynoPreview(DAATAScene, uiFile):
    def __init__(self, initial_data_filepath: str = None):
        super().__init__()
        # self.aborted = False

        initial_data_filepath = "C:\\Users\\afari\\Downloads\\a.csv"
        if not initial_data_filepath \
                or not os.path.exists(initial_data_filepath):
            GenericPopup("Data CSV file does not exist",
                         "Unable to initialize graphs due to missing file.")
            # self.aborted = True
            self.close()
            return
        if initial_data_filepath[-4:] != ".csv":
            GenericPopup("Data file not of CSV type",
                         "Only .csv files supported")
            # self.aborted = True
            self.close()
            return

        self.setupUi(self)
        self.hide()

        self.update_period = 3  # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)

        self.graph_objects = dict()
        # self.current_keys = ["rpm_vs_time", "torque_vs_time", "cvt_ratio_vs_time", "power_vs_rpm"]
        self.current_keys = ["dyno_engine_speed", "dyno_secondary_speed",
                             "force_enginedyno_lbs", "ratio_dyno_cvt"]
        self.collection_start_time: datetime = datetime.min
        self.__create_graphs()

        self.is_sensors_attached = False
        self.load_cell_taring = False

        self.__connect_slots_and_signals()
        self.configFile = QSettings('DAATA', 'data_collection')

        self.__initialize_graphs(initial_data_filepath)
        self.show()
        # self.configFile.clear()
        # self.load_settings()

    def __create_graphs(self):
        """
        This should make 4 graphs
        1. RPM vs. Time scrolling graph, width as 15 seconds
            - Should include both engine rpm and secondary rpm on same graph
        2. Torque vs. Time scrolling graph, width as 15 seconds
            - Should include torque output of engine
        3. CVT Ratio vs. Time scrolling graph, width as 15 seconds
            - Should include CVT ratio
            - Y bounds should be [0, 5]
        4. Power output vs. RPM
            - Y axis is engine power
            - X axis is engine rpm
            - Probably default X bounds to [0, 4000], this will probably change

        :return: None
        """
        pass
        row = 0
        col = 0
        for key in self.current_keys:
            self.graph_objects[key] = \
                CustomPlotWidget(key, parent=self.graph_frame,
                                 layout=self.graph_layout,
                                 graph_width_seconds=8)
            self.graph_objects[key].setObjectName(key)
            self.graph_layout.addWidget(self.graph_objects[key], row, col, 1, 1)
            self.graph_objects[key].show()
            col = not col
            if not col:
                row = 1

    def __initialize_graphs(self, initial_data_filepath: str):
        csv_data = pandas.read_csv(initial_data_filepath)
        time_array = csv_data.time_internal_seconds.values

        for sensor in csv_data.columns.values[1:]:
            if sensor not in self.current_keys:
                continue
            csv_data = pandas.read_csv(initial_data_filepath)
            sensor_array = getattr(csv_data, sensor).values
            self.graph_objects[sensor].initialize_values(
                time_array, sensor_array)

        # plotting ratio_dyno_cvt values

        DEFAULT_INF_VALUE = DerivedSensors.Ratio.DEFAULT_INF_VALUE
        ratio_dyno_cvt_values = [a / b if b != 0 else DEFAULT_INF_VALUE for a, b
                                 in zip(csv_data.dyno_engine_speed.values,
                                        csv_data.dyno_secondary_speed.values)]
        self.graph_objects["ratio_dyno_cvt"].initialize_values(
            time_array, ratio_dyno_cvt_values)

        # last standard values
        last_force_enginedyno_lbs = csv_data.force_enginedyno_lbs.values[-1]
        last_dyno_engine_speed = csv_data.dyno_engine_speed.values[-1]
        last_dyno_secondary_speed = csv_data.dyno_secondary_speed.values[-1]
        last_ratio_dyno_cvt = ratio_dyno_cvt_values[-1]

        # last derived values
        last_dyno_torque_ftlbs = \
            last_force_enginedyno_lbs \
            * DerivedSensors.derived_sensors["dyno_torque_ftlbs"]["transfer_function"]
        power_engine_horsepower_transfer_func = 1 / 5252  # from DerivedSensors
        last_power_engine_horsepower = last_dyno_torque_ftlbs \
                                       * last_dyno_engine_speed \
                                       * power_engine_horsepower_transfer_func

        self.force_lcd.display(last_force_enginedyno_lbs)
        self.engine_speed_lcd.display(last_dyno_engine_speed)
        self.secondary_speed_lcd.display(last_dyno_secondary_speed)

        self.power_lcd.display(last_power_engine_horsepower)
        self.torque_lcd.display(last_dyno_torque_ftlbs)
        self.cvt_ratio_lcd.display(last_ratio_dyno_cvt)

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

    def update_active(self):
        pass

    def update_passive(self):
        pass

    def __connect_slots_and_signals(self):
        pass

    def __save_settings(self):
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
                self.checkbox_objects[key].setChecked(True)
                self.graph_objects[key].show()
                active_sensor_count = active_sensor_count + 1
                self.label_active_sensor_count.setText(
                    '(' + str(active_sensor_count) + '/' + str(len(self.graph_objects)) + ')')
        except TypeError or KeyError:
            logger.error("Possibly invalid key in config. May need to clear config file using self.configFile.clear()")
            pass

        self.comboBox_graphDimension.setCurrentText(self.configFile.value('graph_dimension'))
        # self.slot_graphDimension()
        self.create_grid_plot_layout()
        logger.debug("Data Collection config files loaded")
        # self.debug_settings()

    def __debug_settings(self):
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
    def closeEvent(self, event=None):
        if event:
            event.accept()

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
