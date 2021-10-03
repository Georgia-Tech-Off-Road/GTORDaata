from PyQt5 import QtWidgets, QtGui, uic, QtCore
import os
import json
import logging
from Utilities.DataExport.GTORNetwork import get_GTORNetworkDrive#, generate_data_save_location
from pathlib import Path

''' "saveLocationDialog" configFile settings


'''


uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'saveLocationDialog.ui'))  # loads the .ui file from QT Designer
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


    def loadSettings(self):
        self.checkBox_local.setChecked(self.configFile.value("checkBox_local") == 'true')
        self.checkBox_networkDrive.setChecked(self.configFile.value("checkBox_ND") == 'true')
        self.checkBox_SDCard.setChecked(self.configFile.value("checkBox_SD") == 'true')
        self.checkBox_GDrive.setChecked(
            self.configFile.value("checkBox_GD") == 'true')

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

        self.lineEdit_filenameGD.setText("")
        self.lineEdit_filenameGD.setValidator(validator)


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
            self.widget_GDrive.show()
        else:
            self.widget_GDrive.hide()

    def saveData(self):
        if self.checkBox_local.isChecked():
            local_filename = self.lineEdit_filenameLocal.text()
            local_folder = self.lineEdit_folderLocal.text()

            self.saveCSV(local_filename,local_folder)
            self.saveMAT(local_filename,local_folder)

            # save current values as defaults
            self.configFile.setValue("default_localDirectory", local_folder)

        if self.checkBox_networkDrive.isChecked():
            nd_filename = self.lineEdit_filenameND.text()
            nd_folder = self.lineEdit_folderND.text()

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

        if self.checkBox_GDrive.isChecked():
            GDFilename = self.lineEdit_filenameGD.text()
            GD_oAuth_client_file = self.lineEdit_oAuthGD.text()
            GD_url = self.lineEdit_GDriveURL.text()
            GD_temp_folder = self.lineEdit_foldernameGD.text()
            if GD_url[:43] == "https://drive.google.com/drive/u/0/folders/":
                if GDFilename == "" or GD_oAuth_client_file == "" or GD_url == "" or GD_temp_folder == "":
                    logging.error("One or more Google Drive fields empty")
                else:
                    g_drive_folder_id = GD_url[43:]
                    self.saveCSV(GDFilename, GD_temp_folder,
                                 g_drive_folder_id, GD_oAuth_client_file)
                    # TODO SAVE MAT
            else:
                logging.error("Invalid Google Drive URL")

                # self.configFile.setValue("default_GDFolder", GD_temp_folder)

        # default directory for auto appdata saving        
        default_path = str(Path.home()) + '\AppData\Local\GTOffRoad'

        self.saveCSV(self.scene_name, default_path)
        self.saveMAT(self.scene_name, default_path)

        self.configFile.setValue("checkBox_local", self.checkBox_local.isChecked())
        self.configFile.setValue("checkBox_ND", self.checkBox_networkDrive.isChecked())
        self.configFile.setValue("checkBox_SD", self.checkBox_SDCard.isChecked())
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

    def connectSlotsSignals(self):
        self.checkBox_local.clicked.connect(self.toggle_frames)
        self.checkBox_networkDrive.clicked.connect(self.toggle_frames)
        self.checkBox_SDCard.clicked.connect(self.toggle_frames)
        self.checkBox_GDrive.clicked.connect(self.toggle_frames)
        self.pushButton_save.clicked.connect(self.saveData)
        self.pushButton_cancel.clicked.connect(self.cancelSave)
        self.pushButton_browseDir.clicked.connect(self.change_localDir)
        self.pushButton_browseNDDir.clicked.connect(self.change_NDDir)
        # print(self.label.text())
        # for child in self.findChildren(QtWidgets.QCheckBox):
        #     print(child.objectName())


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = popup_dataSaveLocation()
    sys.exit(app.exec_())
