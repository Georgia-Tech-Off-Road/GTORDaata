from PyQt5 import QtWidgets, QtGui, uic, QtCore
from datetime import datetime
import httplib2
import logging
import os
import webbrowser

# from Utilities.DataExport.GTORNetwork import get_GTORNetworkDrive#, generate_data_save_location
from DataAcquisition import data
from Utilities.DataExport.UploadTagDialogue import TagDialogueGUI
from Utilities.DataExport.exportCSV import saveCSV
from Utilities.DataExport.exportMAT import saveMAT
from Utilities.GoogleDriveHandler import GoogleDriveHandler
from Utilities.Popups.generic_popup import GenericPopup

''' "saveLocationDialog" configFile settings


'''

logger = logging.getLogger("DataCollection")
# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'saveLocationDialog.ui'))
DEFAULT_UPLOAD_DIRECTORY = GoogleDriveHandler.DEFAULT_UPLOAD_DIRECTORY


class popup_dataSaveLocation(QtWidgets.QDialog, uiFile):
    def __init__(self, scene_name, collection_start_time=None):
        super().__init__()
        self.scene_name = scene_name
        self.setupUi(self)
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint)  # hide the question mark in title bar
        self.configFile = QtCore.QSettings('DAATA', 'saveLocationDialog')
        self.loadSettings()
        self.collection_start_time = collection_start_time \
            if collection_start_time is not None else datetime.min
        # the time at the instant the Save Data button is clicked
        self.collection_stop_time = datetime.now()

        self.toggle_frames()
        self.connectSlotsSignals()
        returnValue = self.exec()

    def loadSettings(self):
        self.progressBar_GD.hide()

        self.checkBox_local.setChecked(
            self.configFile.value("checkBox_local") == 'true')
        self.checkBox_networkDrive.setChecked(
            self.configFile.value("checkBox_ND") == 'true')
        self.checkBox_SDCard.setChecked(
            self.configFile.value("checkBox_SD") == 'true')
        self.checkBox_GDrive.setChecked(
            self.configFile.value("checkBox_GD") == 'true')
        self.checkBox_GDrive.setChecked(
            self.configFile.value("checkBox_GD") == 'true')
        self.lineEdit_secGD.setText(self.configFile.value("lineEdit_secGD"))

        # prevent typing invalid characters for test_date and foldername
        regex = QtCore.QRegExp("[a-z-A-Z_0-9]+")
        validator = QtGui.QRegExpValidator(regex)

        self.lineEdit_filenameLocal.setText("")
        self.lineEdit_filenameLocal.setValidator(validator)
        self.lineEdit_folderLocal.setText(
            self.configFile.value("default_localDirectory"))
        self.lineEdit_folderLocal.setValidator(validator)

        self.lineEdit_filenameND.setText("")
        self.lineEdit_filenameND.setValidator(validator)
        # self.lineEdit_folderND.setText(generate_data_save_location())
        self.lineEdit_folderND.setValidator(validator)

        self.lineEdit_filenameSD.setText("")
        self.lineEdit_filenameSD.setValidator(validator)
        self.lineEdit_folderSD.setText(
            self.configFile.value("default_SDFolder"))
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
        """
        Saves the recorded data to the chosen places.

        In the case of Google Drive, an active connection is needed, along with
        an authentication file (instructions included). If the Google Drive
        option is selected but there is no Internet connection, an offline
        backup will be saved to be uploaded at the next uploading session.
        :return: None
        """
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
                logger.info(
                    "Local test_date is empty. File will not be created.")

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
            secret_client_file = self.lineEdit_secGD.text()
            missing_oauth = False
            save_offline = False
            if not os.path.exists(secret_client_file):
                missing_oauth = True
                save_offline = _MissingOAuthFile().save_offline

            default_scene_name = self.scene_name
            sensorsList = data.get_sensors(is_connected=True, is_derived=False)

            tagGUI = TagDialogueGUI(self.collection_start_time,
                                    self.collection_stop_time,
                                    default_scene_name,
                                    sensorsList, save_offline)
            if tagGUI.save_button_clicked:
                # if smooth exit from tagGUI
                new_filename = tagGUI.get_filename()

                if not os.path.exists(DEFAULT_UPLOAD_DIRECTORY):
                    logger.info(
                        "Default path " + DEFAULT_UPLOAD_DIRECTORY
                        + " not found. Making the directory...")
                    os.makedirs(DEFAULT_UPLOAD_DIRECTORY)

                if missing_oauth:
                    if save_offline:
                        saveCSV(new_filename, DEFAULT_UPLOAD_DIRECTORY)
                        saveMAT(new_filename, DEFAULT_UPLOAD_DIRECTORY)
                        GenericPopup("Local copy saved")
                    self.__close_save_settings()
                    return

                saveCSV(new_filename, DEFAULT_UPLOAD_DIRECTORY)
                saveMAT(new_filename, DEFAULT_UPLOAD_DIRECTORY)

                try:
                    drive_handler = GoogleDriveHandler(secret_client_file)
                    self.progressBar_GD.show()
                    drive_handler.upload_all_to_drive(self.progressBar_GD)
                    self.configFile.setValue("lineEdit_secGD",
                                             secret_client_file)
                    GenericPopup("Upload successful",
                                 "Files were successfully uploaded to "
                                 "Google Drive")
                except GoogleDriveHandler.NoInternetError:
                    return
            else:
                GenericPopup("Save Canceled",
                             "Files were not uploaded to Google Drive")
                return
        self.__close_save_settings()

    def __close_save_settings(self):
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
        # select a folder in the C drive
        dir = QtGui.QFileDialog.getExistingDirectory(None, 'Save Data Location',
                                                     os.path.expanduser('~'))
        self.lineEdit_folderND.setText(dir)

    def change_localDir(self):
        # select a folder in the C drive
        dir = QtGui.QFileDialog.getExistingDirectory(None, 'Save Data Location',
                                                     os.path.expanduser('~'))
        self.lineEdit_folderLocal.setText(dir)

    def openSecGDInfo(self):
        """
        Opens the information file "How to: Google Drive Secret Client File"
        on the Google Drive. The file instructs the user how to download
        their own personal Google Drive secret client file needed to upload
        things to Google Drive.
        """
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

    @staticmethod
    def no_internet():
        logger.error("Cannot open info file. Possible internet problems.")
        GenericPopup("No Internet")


# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'missing_oAuth.ui'))


class _MissingOAuthFile(QtWidgets.QDialog, uiFile):
    def __init__(self):
        super().__init__()
        self.save_offline = False

        self.setupUi(self)
        self.__connectSlotsSignals()
        self.exec()

    def __connectSlotsSignals(self):
        self.cancel_button.clicked.connect(self.cancel_save)
        self.yes_button.clicked.connect(self.ok_save)

    def ok_save(self):
        self.save_offline = True
        self.close()

    def cancel_save(self):
        self.close()

    def closeEvent(self, event=None):
        if event is not None:
            event.accept()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = popup_dataSaveLocation()
    sys.exit(app.exec_())
