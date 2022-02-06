from PyQt5 import QtWidgets, uic
import os

# loads the .ui file from QT Designer
uiFileMetadata, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                                'file_metadata.ui'))


class FileMetadata(QtWidgets.QDialog, uiFileMetadata):
    def __init__(self, filename: str, metadata_info: str = ""):
        super().__init__()
        self.setupUi(self)
        self.__update_content(filename, metadata_info)
        self.__connectSlotsSignals()
        self.exec()

    def __update_content(self, filename: str, metadata_info: str):
        self.filename_label.setText(filename)
        self.metadata_textarea.setText(metadata_info)

    def __connectSlotsSignals(self):
        self.ok_button.clicked.connect(self.__close_popup)

    def __close_popup(self):
        self.close()


# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'confirm_download.ui'))


class ConfirmDownloadNonSupported(QtWidgets.QDialog, uiFile):
    def __init__(self, reason: str = ""):
        super().__init__()
        self.save_offline = False

        self.setupUi(self)
        self.__setReason(reason)
        self.__connectSlotsSignals()
        self.exec()

    def __setReason(self, reason: str = ""):
        if reason:
            self.heading2_text.setText(reason)

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
