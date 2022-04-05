from decimal import Decimal
from distutils.command.install_egg_info import to_filename
from sqlite3 import Time
from time import time
from PyQt5 import QtWidgets, uic, QtCore, QtGui
import os
from DataAcquisition import data, data_import
from Scenes import DAATAScene
import logging

logger = logging.getLogger("Homepage")

# loads the .ui file from QT Desginer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'homepage.ui'))

class Homepage(DAATAScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)        
        self.dict_sensorStatus = {}
        self.connected_sensors = data.get_sensors(is_connected=True)

        self.create_sensor_status_checkboxes()
        self.create_connection_status_checkboxes()  

        self.connect_slots_and_signals()   

        # Vars for sd logic
        self.is_sd_toggle = False
        self.last_sd_time = time()

        # gridPlotLayout checks for new sensors every x*10 ms (so 1000ms)
        self.update_period = 100

    def export_data(self):
        """
        Sets save directory as the existing or most recent directory and 
        prints it.
        
        :return: None
        """

        dir_ = QtGui.QFileDialog.getExistingDirectory(None, 'Select GTOR Network Drive', os.path.expanduser('~'), QtGui.QFileDialog.ShowDirsOnly)       #select a folder in the C drive
        print(dir_)

        pass

    def create_sensor_status_checkboxes(self):
        """
        Lists all sensors in the home page with their respective names and ids
        to show whether they are active or not.
        
        :return: None
        """

        all_sensors = data.get_sensors()
        for sensor in all_sensors:
            self.dict_sensorStatus[sensor] = {}
            sensor_title = str(data.get_id(sensor)) \
                            + ": " + data.get_display_name(sensor)
            self.dict_sensorStatus[sensor]['indicator'] \
                = self.QIndicator(sensor_title, objectName=sensor)
            self.verticalLayout_sensorStatus.addWidget(
                self.dict_sensorStatus[sensor]['indicator'])

        # Create a vertical spacer that forces checkboxes to the top
        spacerItem1 = QtWidgets.QSpacerItem(20, 1000000,
                                            QtWidgets.QSizePolicy.Minimum,
                                            QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_sensorStatus.addItem(spacerItem1)

    def update_sensor_status(self):
        """
        Updates sensor indication colors depending on connected sensors.
        
        :return: None
        """

        connected_sensors = data.get_sensors(is_connected=True)
        for sensor in self.dict_sensorStatus.keys():
            if sensor in connected_sensors:
                self.dict_sensorStatus[sensor]['indicator'].setChecked(True)
            else:
                self.dict_sensorStatus[sensor]['indicator'].setChecked(False)

    def create_connection_status_checkboxes(self):
        """
        Creates status indicators for RF Box, SD Card, and Network Drive.
        
        :return: None
        """

        self.ind_RFBox = self.QIndicator("RF Box Disconnected", objectName = "ind_RFBox")
        self.verticalLayout_connectionStatus.addWidget(self.ind_RFBox)

        self.ind_SDCard = self.QIndicator("SD Card Disconnected", objectName = "ind_SDCard")
        self.verticalLayout_connectionStatus.addWidget(self.ind_SDCard)

        self.ind_connectionStatus = self.QIndicator("Network Drive Disconnected", objectName = "ind_connectionStatus")
        self.verticalLayout_connectionStatus.addWidget(self.ind_connectionStatus)


        # Create a vertical spacer that forces checkboxes to the top
        spacerItem1 = QtWidgets.QSpacerItem(20, 1000000, QtWidgets.QSizePolicy.Minimum,
                                            QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_connectionStatus.addItem(spacerItem1)

    def update_connection_status(self):
        """
        Updates non-sensor indicators depending on what's connected.
        
        :return: None
        """

        if data_import.teensy_found:
            # Connected to teensy
            self.connection_Label.setText("Connected")
            if data_import.ack_code == 3:
                # Connected and stable
                self.connection_Label.setStyleSheet("background-color: #0df200; border: 1px solid black; color: white")                
            else:
                # Connected but not stable
                self.connection_Label.setStyleSheet("background-color: #e3c62f; border: 1px solid black; color: white")
        else:
            # We are not connected to teensy
            self.connection_Label.setText("Disconnected")
            self.connection_Label.setStyleSheet("background-color: #d60000; border: 1px solid black; color: white")
           
        # Check if GTOR network drive is connected
        network_drive = self.GTORNetwork.get_GTORNetworkDrive()
        if network_drive:
            self.ind_connectionStatus.setText("Network Drive Connected" + " (" + network_drive + ")")
            self.ind_connectionStatus.setCheckState(True)
        else:
            self.ind_connectionStatus.setText("Network Drive Disconnected")
            self.ind_connectionStatus.setCheckState(False)

        # Check if SD write is enabled
        sd_state = data.get_current_value("flag_auxdaq_sdwrite")
        if sd_state:
            self.ind_SDCard.setChecked(True)
        else:
            self.ind_SDCard.setChecked(False)
    
    def update_sd_card_status(self):  
        """
        Updates SD card write state whenever the button is clicked.
        
        :return: None
        """
              
        self.last_sd_time = time()
        data.set_current_value("command_auxdaq_sdwrite", True)
        self.is_sd_toggle = True

    def update_active(self):
        """
        Updates Homepage elements if it is the currently selected scene.
        Called by MainWindow.__init__.py.
        
        :return: None
        """

        self.update_sensor_status()
        self.update_connection_status()

    def update_passive(self):
        """
        This method is called no matter what scene is selected.
        
        :return: None
        """

        if self.is_sd_toggle:
            time_diff = Decimal(time()) - Decimal(self.last_sd_time)
            if time_diff > 0.25:
                data.set_current_value("command_auxdaq_sdwrite", False)
                self.is_sd_toggle = False
        

    def connect_slots_and_signals(self):
        """
        This function connects all the Qt signals with the slots so that
        elements such as buttons or checkboxes can be tied to specific
        functions.

        :return: None
        """

        self.SDWriteButton.clicked.connect(self.update_sd_card_status)

    # --- imported methods --- #
    from Utilities.CustomWidgets.indicatorWidget import QIndicator
    from Utilities.DataExport import GTORNetwork

    # --- Overridden event methods --- #
    
    def paintEvent(self, pe):
        """
        This method allows the color scheme of the class to be changed by CSS stylesheets.

        :param pe:
        :return: None
        """
        
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()
        s.drawPrimitive(QtGui.QStyle.PE_Widget, opt, p, self)
