from PyQt5 import QtWidgets, uic, QtCore
from Utilities.GoogleDriveHandler import GoogleDriveHandler
import logging
import os

logger = logging.getLogger("MainWindow")
# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'upload_drive_files.ui'))


class UploadDriveFiles(QtWidgets.QDialog, uiFile):
    # TODO FARIS complete
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__connectSlotsSignals()
        self.configFile = QtCore.QSettings('DAATA', 'UploadDriveFiles')
        self.oAuth_file_entry.setValue(self.configFile.value("sec_file"))
        self.progressBar.hide()
        self.exec()

    def __connectSlotsSignals(self):
        self.upload_all_button.clicked.connect(self.__upload_drive_files)

    def __upload_drive_files(self):
        sec_file = self.oAuth_file_entry.toPlainText()
        self.configFile.setValue("sec_file", sec_file)
        try:
            DRIVE_SERVICE = GoogleDriveHandler(sec_file)
        except ValueError:
            logger.error("Error in creating Google Drive Handler")
            return
        DRIVE_SERVICE.upload_all_to_drive(self.progressBar)

    def close_popup(self):
        self.close()
