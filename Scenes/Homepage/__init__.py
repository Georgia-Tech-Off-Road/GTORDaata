from PyQt5 import QtWidgets, uic, QtCore, QtGui
import os
from DataAcquisition import data
from Scenes import DAATAScene
import logging

logger = logging.getLogger("Homepage")

uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'homepage.ui'))  # loads the .ui file from QT Desginer

class Homepage(DAATAScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.hide()
        self.dict_sensorStatus = {}
        self.connected_sensors = data.get_sensors(is_connected=True)

        self.create_sensorStatusCheckboxes()
        self.create_connectionStatusCheckboxes()
        # self.export_data()

        self.update_period = 100    # gridPlotLayout checks for new sensors every x*10 ms (so 1000ms)

    def export_data(self):
        dir_ = QtGui.QFileDialog.getExistingDirectory(None, 'Select GTOR Network Drive', os.path.expanduser('~'), QtGui.QFileDialog.ShowDirsOnly)       #select a folder in the C drive
        print(dir_)
        # file = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', "data_collection.mat")        # returns a QUrl object of what User wishes to save file as
        # f = open(file[0], 'w')
        # f.write("blahablahjaha")
        # f.close()
        # print(file)
        pass

    def create_sensorStatusCheckboxes(self):
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

    def update_sensorStatus(self):
        connected_sensors = data.get_sensors(is_connected=True)
        for sensor in self.dict_sensorStatus.keys():
            if sensor in connected_sensors:
                self.dict_sensorStatus[sensor]['indicator'].setChecked(True)
            else:
                self.dict_sensorStatus[sensor]['indicator'].setChecked(False)

    def create_connectionStatusCheckboxes(self):
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

    def update_connectionStatus(self):
        # check if GTOR network drive is connected
        network_drive = self.GTORNetwork.get_GTORNetworkDrive()
        if network_drive:
            self.ind_connectionStatus.setText("Network Drive Connected" + " (" + network_drive + ")")
            self.ind_connectionStatus.setCheckState(True)
        else:
            self.ind_connectionStatus.setText("Network Drive Disconnected")
            self.ind_connectionStatus.setCheckState(False)

    def update_active(self):
        self.update_sensorStatus()
        self.update_connectionStatus()

    def update_passive(self):
        pass

    # --- imported methods --- #
    from Utilities.CustomWidgets.indicatorWidget import QIndicator
    from Utilities.DataExport import GTORNetwork

## The line QtGui.QStyleOption() will throw an error
    # --- Overridden event methods --- #
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