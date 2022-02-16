from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QPalette
import os

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

# load the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'shock_dyno.ui'))

logger = logging.getLogger("ShockDyno")


class ShockDyno(DAATAScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.hide()

        self.motor_state = 0

        self.update_period = 3  # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)

        self.graph_objects = dict()
        self.current_keys = ["force_shockdyno_lbs", "lds_shockdyno_mm"]
        self.collection_start_time: datetime = datetime.min
        self.create_graphs()

        from MainWindow import is_data_collecting
        self.is_data_collecting = is_data_collecting

        self.is_sensors_attached = False
        self.load_cell_taring = False

        self.connect_slots_and_signals()
        self.configFile = QSettings('DAATA', 'data_collection')
        # self.configFile.clear()
        # self.load_settings()

    def create_graphs(self):
        """
        This should make 2 graphs
        :return: None
        """
        pass
        row = 0
        col = 0
        for key in self.current_keys:
            self.graph_objects[key] = CustomPlotWidget(key, parent=self.graph_frame, layout=self.graph_layout, graph_width_seconds=8)
            self.graph_objects[key].setObjectName(key)
            self.graph_layout.addWidget(self.graph_objects[key], row, col, 1, 1)
            self.graph_objects[key].show()
            col = not col
            if not col:
                row = 1

    def slot_data_collecting_state_change(self):
        if self.button_display.isChecked():
            if self.collection_start_time == datetime.min:
                self.collection_start_time = datetime.now()
            self.indicator_onOrOff.setText("On")
            self.indicator_onOrOff.setStyleSheet("color: green;")
            self.button_display.setText("Stop Collecting Data")
            self.is_data_collecting.set()
        else:
            self.indicator_onOrOff.setText("Off")
            self.indicator_onOrOff.setStyleSheet("color: red;")
            self.button_display.setText("Start Collecting Data")
            self.is_data_collecting.clear()
            self.popup_dataSaveLocation("ShockDynoTest",
                                        self.collection_start_time)

    def slot_tare_load_cell(self):
        logger.info("Taring load cell")
        data.set_current_value("command_tare_load_cell", 1)
        self.load_cell_taring = True

    def slot_display_motor_speed(self, motor_speed):
        self.motorspeed_lcd.display(motor_speed)

    def slot_set_motor_speed(self):
        logger.info("Setting motor speed")
        motor_speed = self.horizontalSlider.value()
        data.set_current_value("command_motor_speed", motor_speed)

    def slot_toggle_motor(self):
        logger.info("Toggling motor")
        #data.set_current_value("command_motor_enable", not self.motor_state)
        self.motor_state = not self.motor_state

    def slot_set_load_cell_scale(self):
        logger.info("Changing load cell scale")
        data.set_sensor_scale("force_shockdyno_lbs", self.load_cell_scale.value())

    def update_graphs(self):
        for key in self.current_keys:
            self.graph_objects[key].update_graph()

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

    def update_active(self):
        """
        This function will update only if the Data Collection tab is the current tab. This function will get called
        at whatever frequency self.update_freq is set at. It is called via the update_all function from the
        MainWindow.

        :return: None
        """

        if self.force_lcd.isEnabled():
            self.force_lcd.display(data.get_current_value("force_shockdyno_lbs"))
        if self.position_lcd.isEnabled():
            self.position_lcd.display(data.get_current_value("lds_shockdyno_mm"))

        if self.is_data_collecting.is_set():
            if self.button_display.isChecked():
                self.update_graphs()
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
        # Enable or disable the lcd displays based on what sensors are connected
        if data.get_is_connected("lds_shockdyno_mm"):
            self.position_lcd.setEnabled(True)
        else:
            self.position_lcd.setEnabled(False)
            
        if data.get_is_connected("force_shockdyno_lbs"):
            self.force_lcd.setEnabled(True)
        else:
            self.force_lcd.setEnabled(False)

        if data.get_is_connected("command_motor_speed"):
            self.motorspeed_lcd.setEnabled(True)
        else:
            self.motorspeed_lcd.setEnabled(False)

        # Attach or detach the load cell tare sensor based on if the tab is active
        if self.isVisible():
            if not self.is_sensors_attached:
                data_import.attach_output_sensor(data.get_id("command_tare_load_cell"))
                data_import.attach_output_sensor(data.get_id("command_motor_speed"))
                self.is_sensors_attached = True
        else:
            if self.is_sensors_attached:
                data_import.detach_output_sensor(data.get_id("command_tare_load_cell"))
                data_import.attach_output_sensor(data.get_id("command_motor_speed"))
                self.is_sensors_attached = False

        if self.load_cell_taring:
            self.load_cell_taring = False
        else:
            data.set_current_value("command_tare_load_cell", 0)

        data.set_current_value("command_motor_speed", self.motor_state)

    def connect_slots_and_signals(self):
        self.button_display.clicked.connect(self.slot_data_collecting_state_change)

        self.load_cell_tare.clicked.connect(self.slot_tare_load_cell)
        self.load_cell_scale.valueChanged.connect(self.slot_set_load_cell_scale)

        self.horizontalSlider.valueChanged.connect(self.slot_display_motor_speed)
        self.kill_motor.clicked.connect(self.slot_toggle_motor) #toggle motor on and off
        self.send_speed.clicked.connect(self.slot_set_motor_speed) #set speed to value from slider
        self.sweep.clicked.connect(self.slot_sweep)


        # connections to GridPlotLayout
        # for key in self.graph_objects.keys():
        #     widget = self.graph_objects[key]
        #     settings = widget.button_settings.clicked.connect(partial(self.graph_objects[key].open_SettingsWindow))

    def slot_sweep(self):
        for i in range(100):
            print(i)
            #self.lcdNumber.display(i)
            #logger.info("Setting motor speed")
            #data.set_current_value("command_motor_speed", i)
            #time.sleep(2)


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

    '''
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
    '''
