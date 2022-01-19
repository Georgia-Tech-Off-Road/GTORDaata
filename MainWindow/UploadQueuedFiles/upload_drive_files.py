from PyQt5 import QtWidgets, uic, QtCore
from Utilities.GoogleDriveHandler import GoogleDriveHandler
import logging
import os

from Utilities.Popups.generic_popup import GenericPopup

logger = logging.getLogger("MainWindow")
# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'upload_drive_files.ui'))


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
        sec_file = self.oAuth_file_entry.toPlainText()
        self.configFile.setValue("sec_file", sec_file)
        try:
            drive_handler = GoogleDriveHandler(sec_file)
        except GoogleDriveHandler.NoInternetError:
            GenericPopup("No Internet")
            return
        except Exception as e:
            print(e)
            GenericPopup("Upload Failed", str(e))
            return

        if drive_handler.upload_all_to_drive(self.progressBar):
            GenericPopup("All files uploaded")
            self.close_popup()

    def close_popup(self):
        self.close()
