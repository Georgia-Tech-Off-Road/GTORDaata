from PyQt5 import QtWidgets, uic, QtCore
from Utilities.GoogleDriveHandler import GoogleDriveHandler
from Utilities.Popups.generic_popup import GenericPopup
import logging
import os

logger = logging.getLogger("MainWindow")
# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'upload_all_drive_files.ui'))


class UploadDriveFiles(QtWidgets.QDialog, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__connectSlotsSignals()
        self.configFile = QtCore.QSettings('DAATA', 'UploadDriveFiles')
        self.oAuth_file_entry.setPlainText(self.configFile.value("sec_file"))
        self.progressBar.hide()
        self.exec()

    def __connectSlotsSignals(self):
        self.upload_all_button.clicked.connect(self.__upload_drive_files)
        self.oAuth_info.clicked.connect(GoogleDriveHandler.openSecGDInfo)

    def __upload_drive_files(self):
        self.progressBar.show()
        sec_file = self.oAuth_file_entry.toPlainText()
        self.configFile.setValue("sec_file", sec_file)
        try:
            drive_handler = GoogleDriveHandler(sec_file)
        except GoogleDriveHandler.NoInternetError:
            GenericPopup("No Internet")
            self.progressBar.hide()
            return
        except GoogleDriveHandler.MissingOAuthFileError:
            GenericPopup("Missing oAuth File",
                         f"oAuth file not detected in path {sec_file} entered")
            self.progressBar.hide()
            return
        except Exception as e:
            print(e)
            GenericPopup("Upload Failed", str(e))
            self.progressBar.hide()
            return

        if drive_handler.upload_all_to_drive(self.progressBar):
            GenericPopup("All files uploaded", drive_handler.warning_msg)
            self.close_popup()
        self.progressBar.hide()

    def close_popup(self):
        self.close()
