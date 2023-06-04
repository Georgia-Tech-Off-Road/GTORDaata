from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtCore import QSettings, QTime, QTimer
from PyQt5.QtGui import QPalette
import pyproj
import os
import sys
import io
import folium # pip install folium
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from shapely.geometry import LineString

import pyqtgraph as pg
from functools import partial
import DataAcquisition
from DataAcquisition import data
from DataAcquisition import data_import
from Utilities.CustomWidgets.Plotting import CustomPlotWidget, GridPlotLayout
from Scenes import DAATAScene
import logging
from datetime import datetime

# Default plot configuration for pyqtgraph
pg.setConfigOption('background', 'w')   # white
pg.setConfigOption('foreground', 'k')   # black

transformer = pyproj.Transformer.from_crs(
    {"proj":'geocent', "ellps":'WGS84', "datum":'WGS84'},
    {"proj":'latlong', "ellps":'WGS84', "datum":'WGS84'},
    )

# load the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'map_gps.ui'))

logger = logging.getLogger("MapGPS")


class MapGPS(DAATAScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.hide()

        self.update_period = 3  # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)
        self.lap_count = 0
        self.current_lap_time = QTime.currentTime()
        self.prev_lap_time = QTime.currentTime()
        self.gps_coords_x = []
        self.gps_coords_y = []
        self.last_updated_index = -1
        
        self.recorded_lap_times = []
        self.recorded_lap_finish_times=[]


        self.graph_objects = dict()
        self.collection_start_time = datetime.now()

        from MainWindow import is_data_collecting
        self.is_data_collecting = is_data_collecting

        self.update_map_origin(33.7792984,-84.408036)
        self.update_gps_map()
        self.curr_lap_time_lcd.setDigitCount(11)
        self.curr_lap_time_lcd.display("00:00:00.00")

        self.start_line_xy = ([0,0],[0,0])
        self.start_line_xy_polyline = folium.PolyLine(self.start_line_xy,
                            color='red',
                            weight=15,
                            opacity=0.8)
        self.start_line_xy_polyline.add_to(self.map)
            

        self.is_sensors_attached = False

        self.connect_slots_and_signals()

    def absolute_count_laps():
        pass
    
    def slot_start_line_changed(self):
        self.start_line_xy = LineString([self.p1_lat.text(), self.p1_long.text()],
                                        [self.p2_lat.text(), self.p2_long.text()])

    def update_map_origin(self,map_origin_x,map_origin_y):
        self.map_origin_x = map_origin_x
        self.map_origin_y = map_origin_y

    def update_gps_map(self):
        for i in reversed(range(self.map_layout.count())): 
            self.map_layout.itemAt(i).widget().setParent(None)

        self.map = folium.Map(location=[self.map_origin_x,self.map_origin_y],
                        zoom_start=15)
        recentest_index = data.get_most_recent_index("gps_ecef_x")
        if (self.last_updated_index != recentest_index and (data.get_is_connected("gps_ecef_x"))):
            
            curr_x = data.get_current_value("gps_ecef_x")/100
            curr_y = data.get_current_value("gps_ecef_y")/100
            curr_z = data.get_current_value("gps_ecef_z")/100
            curr_lon, curr_lat, curr_alt = transformer.transform(curr_x,curr_y,curr_z,radians=False)   

            prev_x = data.get_value("gps_ecef_x", recentest_index-1)/100
            prev_y = data.get_value("gps_ecef_y", recentest_index-1)/100
            prev_z = data.get_value("gps_ecef_z", recentest_index-1)/100
            prev_lon, prev_lat, prev_alt = transformer.transform(prev_x,prev_y,prev_z,radians=False)   


            self.lon_lcd.display(curr_lon)
            self.lat_lcd.display(curr_lat)

            # add current car position as green circle
            folium.Circle([curr_lon, curr_lat], color = 'green', weight=20).add_to(self.map)

            # draw most recent path
            gps_diff = [(prev_lon, prev_lat),
                        (curr_lon, curr_lat)]

            folium.PolyLine(gps_diff,
                            color='red',
                            weight=15,
                            opacity=0.8).add_to(self.map)



            # check if starting line was crossed
            if LineString(gps_diff).crosses(LineString(self.start_line_xy)):
                self.recorded_lap_finish_times.append(self.update_current_lap_time)
                self.prev_lap_finish_time = QTime.currentTime()
                self.lap_count = self.lap_count + 1

            self.last_updated_index == DataAcquisition.data.get_most_recent_index()
        
        

        # # save map data to data object
        # data = io.BytesIO()
        # m.save(data, close_file=False)


    

    def slot_data_collecting_state_change(self):
        if self.button_display.isChecked():
            self.start_race()
            if self.collection_start_time == datetime.min:
                self.collection_start_time = datetime.now()
            self.indicator_onOrOff.setText("On")
            self.indicator_onOrOff.setStyleSheet("color: green;")
            self.button_display.setText("Stop Tracking Car")
            self.is_data_collecting.set()
        else:
            self.indicator_onOrOff.setText("Off")
            self.indicator_onOrOff.setStyleSheet("color: red;")
            self.button_display.setText("Begin Tracking Car")
            self.is_data_collecting.clear()
            self.popup_dataSaveLocation("ShockDynoTest",
                                        self.collection_start_time)

    def slot_reset_map_origin(self):
        curr_x = data.get_current_value("gps_ecef_x")/100
        curr_y = data.get_current_value("gps_ecef_y")/100
        curr_z = data.get_current_value("gps_ecef_z")/100            
        curr_lon, curr_lat, curr_alt = transformer.transform(curr_x,curr_y,curr_z,radians=False)   


        self.create_gps_map(curr_lat,curr_lon)


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
            logger.debug(logger.findCaller(True))

    def start_race(self):
        self.prev_lap_time = QTime.currentTime()
        self.lap_count = 0



    def check_laps(self):
        
        self.prev_lap_time = QTime.currentTime()
        self.lap_count = self.lap_count + 1

    def update_current_lap_time(self):
        current_lap_time_ms = self.prev_lap_time.msecsTo(QTime.currentTime())
        seconds_elapsed = current_lap_time_ms / 1000
        seconds_elapsed_int = int(seconds_elapsed)
        hours_elapsed = int(seconds_elapsed_int / 3600)
        minutes_elapsed = int((seconds_elapsed_int - hours_elapsed * 3600) / 60)
        seconds_elapsed = seconds_elapsed % 60
        format_time = "{hours:02d}:{minutes:02d}:{seconds:05.2f}"
        str_time = format_time.format(hours=hours_elapsed, minutes=minutes_elapsed, seconds=seconds_elapsed)
        self.curr_lap_time_lcd.display(str_time)

        self.recorded_lap_times.append(str_time)
        return QTime.currentTime() # lap finish time


    def update_active(self):
        """
        This function will update only if the Data Collection tab is the current tab. This function will get called
        at whatever frequency self.update_freq is set at. It is called via the update_all function from the
        MainWindow.

        :return: None
        """


        # curr_x = data.get_current_value("gps_ecef_x")/100
        # curr_y = data.get_current_value("gps_ecef_x")/100
        # curr_z = data.get_current_value("gps_ecef_x")/100
        # curr_lon, curr_lat, curr_alt = pyproj.transform(ecef, lla, curr_x, curr_y, curr_z, radians=False)
        # print(curr_lon)
        # print(curr_lat)

        if self.button_display.isChecked():
            self.laps_lcd.display(self.lap_count)
            self.update_current_lap_time()

        self.update_gps_map()

        if self.is_data_collecting.is_set():
            if self.button_display.isChecked():
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
        pass

    def connect_slots_and_signals(self):
        self.button_test.clicked.connect(self.check_laps)
        self.button_reset_map_origin.clicked.connect(self.slot_reset_map_origin)
        self.button_display.clicked.connect(self.slot_data_collecting_state_change)

        self.p1_long.textChanged.connect(self.slot_start_line_changed)
        self.p1_lat.textChanged.connect(self.slot_start_line_changed)
        self.p2_long.textChanged.connect(self.slot_start_line_changed)
        self.p2_lat.textChanged.connect(self.slot_start_line_changed)
        # self.load_cell_tare.clicked.connect(self.slot_tare_load_cell)
        # self.load_cell_scale.valueChanged.connect(self.slot_set_load_cell_scale)

        # connections to GridPlotLayout
        # for key in self.graph_objects.keys():
        #     widget = self.graph_objects[key]
        #     settings = widget.button_settings.clicked.connect(partial(self.graph_objects[key].open_SettingsWindow))
        pass

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
                self.checkbox_objects[key].setChecked(True)
                self.graph_objects[key].show()
                active_sensor_count = active_sensor_count + 1
                self.label_active_sensor_count.setText(
                    '(' + str(active_sensor_count) + '/' + str(len(self.graph_objects)) + ')')
        except TypeError or KeyError:
            logger.error("Possibly invalid key in config. May need to clear config file using self.configFile.clear()")
            logger.debug(logger.findCaller(True))

        self.comboBox_graphDimension.setCurrentText(self.configFile.value('graph_dimension'))
        # self.slot_graphDimension()
        self.create_grid_plot_layout()
        logger.debug("Data Collection config files loaded")
        # self.debug_settings()

    def debug_settings(self):
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
    def closeEvent(self):
        self.save_settings()
        self.window().setWindowTitle('closed tab')

    def paintEvent(self, pe):
        """
        This method allows the color scheme of the class to be changed by CSS stylesheets

        :param pe:
        :return: None
        """
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()
        s.drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, p, self)
