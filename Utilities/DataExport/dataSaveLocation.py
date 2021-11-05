import httplib2
from PyQt5 import QtWidgets, QtGui, uic, QtCore
import os
import logging
import json

import Utilities.DataExport.GoogleDrive.exportGDrive
# from Utilities.DataExport.GTORNetwork import get_GTORNetworkDrive#, generate_data_save_location
import webbrowser
from datetime import datetime
from DataAcquisition import data
from Utilities.DataExport.exportCSV import saveCSV
from Utilities.DataExport.exportMAT import saveMAT
from Utilities.DataExport.GoogleDrive.exportGDrive import upload_all_to_drive
from Utilities.DataExport.GoogleDrive.no_internet_popup import no_internet_popup
''' "saveLocationDialog" configFile settings


'''

logger = logging.getLogger("DataCollection")
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'saveLocationDialog.ui'))  # loads the .ui file from QT Designer
DEFAULT_DIRECTORY = Utilities.DataExport.GoogleDrive.exportGDrive.DEFAULT_DIRECTORY

class popup_dataSaveLocation(QtWidgets.QDialog, uiFile):
    def __init__(self, scene_name, collection_start_time=None):
        super().__init__()
        self.scene_name = scene_name
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)     # hide the question mark in title bar
        self.configFile = QtCore.QSettings('DAATA', 'saveLocationDialog')
        self.loadSettings()
        self.collection_start_time = collection_start_time
        # the time at the instant the Save Data button is clicked
        self.collection_stop_time = datetime.now()

        self.toggle_frames()
        self.connectSlotsSignals()
        returnValue = self.exec()

    def loadSettings(self):
        self.checkBox_local.setChecked(self.configFile.value("checkBox_local") == 'true')
        self.checkBox_networkDrive.setChecked(self.configFile.value("checkBox_ND") == 'true')
        self.checkBox_SDCard.setChecked(self.configFile.value("checkBox_SD") == 'true')
        self.checkBox_GDrive.setChecked(
            self.configFile.value("checkBox_GD") == 'true')
        self.checkBox_GDrive.setChecked(
            self.configFile.value("checkBox_GD") == 'true')
        self.lineEdit_secGD.setText(self.configFile.value("lineEdit_secGD"))

        # prevent typing invalid characters for filename and foldername
        regex = QtCore.QRegExp("[a-z-A-Z_0-9]+")
        validator = QtGui.QRegExpValidator(regex)

        self.lineEdit_filenameLocal.setText("")
        self.lineEdit_filenameLocal.setValidator(validator)
        self.lineEdit_folderLocal.setText(self.configFile.value("default_localDirectory"))
        self.lineEdit_folderLocal.setValidator(validator)

        self.lineEdit_filenameND.setText("")
        self.lineEdit_filenameND.setValidator(validator)
        #self.lineEdit_folderND.setText(generate_data_save_location())
        self.lineEdit_folderND.setValidator(validator)

        self.lineEdit_filenameSD.setText("")
        self.lineEdit_filenameSD.setValidator(validator)
        self.lineEdit_folderSD.setText(self.configFile.value("default_SDFolder"))
        self.lineEdit_folderSD.setValidator(validator)

    def toggle_frames(self):
        if self.checkBox_local.isChecked():
            self.widget_local.show()
        else:
            self.widget_local.hide()

        if self.checkBox_networkDrive.isChecked():
            self.widget_networkDrive.show()
        else:
            self.widget_networkDrive.hide()

        if self.checkBox_SDCard.isChecked():
            self.widget_SDCard.show()
        else:
            self.widget_SDCard.hide()

        if self.checkBox_GDrive.isChecked():
            self.widget_GD.show()
        else:
            self.widget_GD.hide()

    def saveData(self):
        if self.checkBox_local.isChecked():
            local_filename = self.lineEdit_filenameLocal.text()
            local_folder = self.lineEdit_folderLocal.text()

            saveCSV(local_filename, local_folder)
            saveMAT(local_filename, local_folder)

            # save current values as defaults
            self.configFile.setValue("default_localDirectory", local_folder)

        if self.checkBox_networkDrive.isChecked():
            nd_filename = self.lineEdit_filenameND.text()
            nd_folder = self.lineEdit_folderND.text()
            if nd_filename == "":
                logger.info("Local filename is empty. File will not be created."
                            )

            self.saveCSV(nd_filename, nd_folder)
            self.saveMAT(nd_filename, nd_folder)

        if self.checkBox_SDCard.isChecked():
            SDFilename = self.lineEdit_filenameSD.text()
            SDFolder = self.lineEdit_folderSD.text()
            SDPath = os.path.join(SDFolder, SDFilename)
            SDFile = open(SDPath, 'w')
            SDFile.write("this is a test file for saving to the SD Card")
            SDFile.close()

            self.configFile.setValue("default_SDFolder", SDFolder)

        if not os.path.exists(DEFAULT_DIRECTORY):
            logger.info(
                "Default path " + DEFAULT_DIRECTORY + " not found. Making "
                                                      "the directory...")
            os.mkdir(DEFAULT_DIRECTORY)

        if self.checkBox_GDrive.isChecked():
            GDFilename = self.collection_start_time\
                .strftime("%Y-%m-%d-%H-%M-%S")
            # metadata = {
            #     "scene_name": self.scene_name,
            # }

            """
            Creates and saves the CSV and MAT files to the default
            path. This will create two identical sets of files with
            different names if the entered filename is not equal to
            the default name 
            """
            saveCSV(GDFilename, DEFAULT_DIRECTORY)

            saveMAT(GDFilename, DEFAULT_DIRECTORY)

            self.add_custom_properties(GDFilename)

            secret_client_file = self.lineEdit_secGD.text()
            if os.path.exists(secret_client_file):
                upload_all_to_drive(DEFAULT_DIRECTORY, secret_client_file)
                self.configFile.setValue("lineEdit_secGD", secret_client_file)
            else:
                logger.error("Secret client file missing")

        self.configFile.setValue("checkBox_local",
                                 self.checkBox_local.isChecked())
        self.configFile.setValue("checkBox_ND",
                                 self.checkBox_networkDrive.isChecked())
        self.configFile.setValue("checkBox_SD",
                                 self.checkBox_SDCard.isChecked())
        self.configFile.setValue("checkBox_GD",
                                 self.checkBox_GDrive.isChecked())

        self.close()

    def cancelSave(self):
        self.close()

    def change_NDDir(self):
        dir = QtGui.QFileDialog.getExistingDirectory(None, 'Save Data Location', os.path.expanduser('~'))  # select a folder in the C drive
        self.lineEdit_folderND.setText(dir)

    def change_localDir(self):
        dir = QtGui.QFileDialog.getExistingDirectory(None, 'Save Data Location', os.path.expanduser('~'))  # select a folder in the C drive
        self.lineEdit_folderLocal.setText(dir)

    """
    Opens the information file "How to: Google Drive Secret Client File" on the 
    Google Drive. The file instructs the user how to download their own personal 
    Google Drive secret client file needed to upload things to Google Drive.
    """
    def openSecGDInfo(self):
        try:
            webbrowser.open("https://docs.google.com/presentation/d/"
                            "1YInB3CuCPPKrWF0j-Wo1OCaAVuUZlWiRNbc8Bd_sezY/"
                            "edit?usp=sharing")
        except httplib2.error.ServerNotFoundError:
            self.no_internet()
            return None

    def connectSlotsSignals(self):
        self.checkBox_local.clicked.connect(self.toggle_frames)
        self.checkBox_networkDrive.clicked.connect(self.toggle_frames)
        self.checkBox_SDCard.clicked.connect(self.toggle_frames)
        self.checkBox_GDrive.clicked.connect(self.toggle_frames)
        self.pushButton_save.clicked.connect(self.saveData)
        self.pushButton_cancel.clicked.connect(self.cancelSave)
        self.pushButton_browseDir.clicked.connect(self.change_localDir)
        self.pushButton_browseNDDir.clicked.connect(self.change_NDDir)
        self.pushButton_secGDInfo.clicked.connect(self.openSecGDInfo)
        # print(self.label.text())
        # for child in self.findChildren(QtWidgets.QCheckBox):
        #     print(child.objectName())

    def no_internet(self):
        logger.error("Cannot open info file. Possible internet problems.")
        no_internet_popup()

    """
    Creates a JSON metadata file, the contents of which will attach to the 
    uploaded files as custom Google Drive file properties/appProperties 
    or metadata.
    """
    def add_custom_properties(self, filename):
        # Limit: https://developers.google.com/drive/api/v3/properties
        PROPERTIES_LIMIT = 30  # public
        APP_PROPERTIES_LIMIT = 30  # private outside of this application

        custom_properties = dict()
        # True if some properties are removed; max is 60 keys
        custom_properties["some_properties_removed"] = "False"
        custom_properties["scene"] = self.scene_name
        custom_properties["collection_start_time"] \
            = str(self.collection_start_time)
        custom_properties["collection_stop_time"] \
            = str(self.collection_stop_time)
        custom_properties["test_length"] = str(self.collection_stop_time
                                               - self.collection_start_time)
        custom_properties["note"] = "Put a note here!"

        # adds all the sensors to the custom_properties dict up to 60 total
        # custom_properties.
        sensorsList = data.get_sensors(is_connected=True, is_derived=False)
        sensorsList_limit = len(sensorsList)
        TOTAL_LIMIT = PROPERTIES_LIMIT + APP_PROPERTIES_LIMIT  # 60
        if len(sensorsList) + len(custom_properties) > TOTAL_LIMIT:  # 60
            sensorsList_limit = TOTAL_LIMIT - len(custom_properties)
            custom_properties["some_properties_removed"] = "True"
        for sensor_i in range(sensorsList_limit):
            custom_properties["sensor-" + sensorsList[sensor_i]] = "True"

        # Verifies each property is max 124 char. Disabled for performance.
        # verify_custom_prop_len(custom_properties)

        with open(DEFAULT_DIRECTORY + filename + ".json", "w") as outfile:
            json.dump(custom_properties, outfile)

    """
    # Verifies each property is max 124 char long to satisfy GDrive 
    # requirements. Disabled for performance.
    """
    def verify_custom_prop_len(self, custom_properties: dict):
        """
        https://developers.google.com/drive/api/v3/properties
        Maximum of 124 bytes size per property (including both key and value) string
         in UTF-8 encoding. For example, a property with a key that is ten
         characters long can only have 114 characters in the value. A property that
          requires 100 characters for the value can use up to 24 characters for the
          key.
        """
        MAX_BYTES_PER_PROP = 124
        for key in custom_properties.keys():
            if len(key) > MAX_BYTES_PER_PROP:
                del custom_properties[key]
            elif len(key) + len(custom_properties[key]) > MAX_BYTES_PER_PROP:
                value_limit = MAX_BYTES_PER_PROP - len(key)
                custom_properties[key] = custom_properties[key][:value_limit]


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = popup_dataSaveLocation()
    sys.exit(app.exec_())
