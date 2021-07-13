from PyQt5 import QtWidgets, uic, QtCore, QtGui
import os
from DataAcquisition import data
from Scenes import BaseScene
import logging

logger = logging.getLogger("Homepage")

uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'homepage.ui'))  # loads the .ui file from QT Desginer

class Homepage(BaseScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.hide()
        self.dict_sensor_status = {}
        self.connected_sensors = data.get_sensors(is_connected=True)

        self.createSensorStatusCheckboxes()
        self.createConnectionStatusCheckboxes()
        # self.export_data()


    ## imported methods
    from Utilities.CustomWidgets.indicatorWidget import QIndicator
    from Utilities.DataExport import GTORNetwork


    ## functions that are frequently called if the tab is visible
    def update(self):
        pass

    ## functions that are occasionally called if the tab is visible
    def updateOccasional(self):
        self.updateSensorStatus()
        self.updateConnectionStatus()

    def exportData(self):
        dir_ = QtGui.QFileDialog.getExistingDirectory(None, 'Select GTOR Network Drive', os.path.expanduser('~'), QtGui.QFileDialog.ShowDirsOnly)       #select a folder in the C drive
        print(dir_)
        # file = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', "data_collection.mat")        # returns a QUrl object of what User wishes to save file as
        # f = open(file[0], 'w')
        # f.write("blahablahjaha")
        # f.close()
        # print(file)
        pass

    def createSensorStatusCheckboxes(self):
        all_sensors = data.get_sensors()
        for sensor in all_sensors:
            self.dict_sensor_status[sensor] = {}
            self.dict_sensor_status[sensor]['indicator'] = self.QIndicator(data.get_display_name(sensor), objectName=sensor)
            self.verticalLayout_sensorStatus.addWidget(self.dict_sensor_status[sensor]['indicator'])



        # Create a vertical spacer that forces checkboxes to the top
        spacerItem1 = QtWidgets.QSpacerItem(20, 1000000, QtWidgets.QSizePolicy.Minimum,
                                            QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_sensorStatus.addItem(spacerItem1)

    def createConnectionStatusCheckboxes(self):
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

    def updateSensorStatus(self):
        connected_sensors = data.get_sensors(is_connected=True)
        for sensor in self.dict_sensor_status.keys():
            if sensor in connected_sensors:
                self.dict_sensor_status[sensor]['indicator'].setChecked(True)
            else:
                self.dict_sensor_status[sensor]['indicator'].setChecked(False)

    def updateConnectionStatus(self):
        # check if GTOR network drive is connected
        network_drive = self.GTORNetwork.get_GTORNetworkDrive()
        if network_drive:
            self.ind_connectionStatus.setText("Network Drive Connected" + " (" + network_drive + ")")
            self.ind_connectionStatus.setCheckState(True)
        else:
            self.ind_connectionStatus.setText("Network Drive Disconnected")
            self.ind_connectionStatus.setCheckState(False)


    ##################################
    #### Overridden event methods ####

    ## allow color scheme of class to be changed by CSS stylesheets
    def paintEvent(self, pe):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()
        s.drawPrimitive(QtGui.QStyle.PE_Widget, opt, p, self)
