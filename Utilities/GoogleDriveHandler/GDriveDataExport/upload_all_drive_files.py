from PyQt5 import QtWidgets, uic, QtCore
from Utilities.GoogleDriveHandler import GoogleDriveHandler
from Utilities.GoogleDriveHandler import gdrive_constants
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
        self.progressBar.hide()
        self.exec()

    def __connectSlotsSignals(self):
        self.upload_all_button.clicked.connect(self.__upload_drive_files)

    def __upload_drive_files(self):
        self.progressBar.show()
        sec_file = gdrive_constants.GDRIVE_OAUTH2_SECRET
        self.configFile.setValue("sec_file", sec_file)
        try:
            drive_handler = GoogleDriveHandler(sec_file)
        except GoogleDriveHandler.NoInternetError:
            GenericPopup("No Internet")
            self.progressBar.hide()
            return
        except GoogleDriveHandler.MissingOAuthFileError:
            GenericPopup("Missing oAuth file",
                         f"oAuth file not detected in {sec_file}. <br /> "
                         f"<a href='https://drive.google.com/file/d/117yhiyV2BAZNxityj4la6J50FECaEPJB/view?usp=sharing'>"
                         f"Download here</a>.")
            self.progressBar.hide()
            return
        # except GoogleDriveHandler.NoAccessError:
        #     self.__clear_found_files()
        #     GenericPopup("No Access", "You need to request access to the GTOR "
        #                               "shared Google Drive")
        #     return
        except Exception as e:
            logger.error(str(e))
            GenericPopup("Upload Failed", str(e))
            self.progressBar.hide()
            return

        if drive_handler.upload_all_to_drive(self.progressBar):
            GenericPopup("All files uploaded", drive_handler.warning_msg)
            self.close()
        self.progressBar.hide()


