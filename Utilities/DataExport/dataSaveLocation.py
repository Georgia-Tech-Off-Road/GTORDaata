import httplib2
from PyQt5 import QtWidgets, QtGui, uic, QtCore
import os
import json
import logging
from Utilities.DataExport.GTORNetwork import get_GTORNetworkDrive#, generate_data_save_location
import webbrowser
from pathlib import Path
from datetime import datetime

''' "saveLocationDialog" configFile settings


'''

logger = logging.getLogger("DataCollection")
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'saveLocationDialog.ui'))  # loads the .ui file from QT Designer
DEFAULT_DIRECTORY = str(Path.home()) + '\\AppData\\Local\\GTOffRoad\\'

class popup_dataSaveLocation(QtWidgets.QDialog, uiFile):
    def __init__(self, scene_name):
        super().__init__()
        self.scene_name = scene_name
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)     # hide the question mark in title bar
        self.configFile = QtCore.QSettings('DAATA', 'saveLocationDialog')
        self.loadSettings()

        self.toggle_frames()
        self.connectSlotsSignals()
        returnValue = self.exec()

    ## imported methods
    from Utilities.DataExport.exportCSV import saveCSV
    from Utilities.DataExport.exportMAT import saveMAT
    from Utilities.DataExport.exportGDrive import upload_all_to_drive

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

            self.saveCSV(local_filename, local_folder)
            self.saveMAT(local_filename, local_folder)

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
            time_now = datetime.now()
            time_now = time_now.strftime("%Y-%m-%d-%H-%M-%S")
            GDFilename = time_now
            # metadata = {
            #     "scene_name": self.scene_name,
            # }

            """
            Creates and saves the CSV and MAT files to the default
            path. This will create two identical sets of files with
            different names if the entered filename is not equal to
            the default name 
            """
            self.saveCSV(GDFilename, DEFAULT_DIRECTORY)
            self.saveMAT(GDFilename, DEFAULT_DIRECTORY)
            appProperties = dict()
            # appProperties["scene"] =

            secret_client_file = self.lineEdit_secGD.text()
            if os.path.exists(secret_client_file):
                self.upload_all_to_drive(DEFAULT_DIRECTORY, secret_client_file)
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


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = popup_dataSaveLocation()
    sys.exit(app.exec_())
