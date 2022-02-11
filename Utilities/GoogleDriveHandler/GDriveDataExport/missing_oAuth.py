from PyQt5 import QtWidgets, uic
from Utilities.GoogleDriveHandler.gdrive_constants import GDRIVE_OAUTH2_SECRET
import os

# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'missing_oAuth.ui'))


class MissingOAuthFile(QtWidgets.QDialog, uiFile):
    def __init__(self):
        super().__init__()
        self.__save_offline = False
        self.setupUi(self)
        self.__setup()
        self.__connectSlotsSignals()
        self.exec()

    def __setup(self):
        self.alt_option.hide()
        alt_option_text = f"You may also download the oAuth file " \
                          f"<a href='https://drive.google.com/file/d/117yhiyV2BAZNxityj4la6J50FECaEPJB/view?usp=sharing'>" \
                          f"here</a> and place it at <br />" \
                          f"{GDRIVE_OAUTH2_SECRET}"
        self.alt_option.setText(alt_option_text)

    def __connectSlotsSignals(self):
        self.cancel_button.clicked.connect(self.__cancel_save)
        self.yes_button.clicked.connect(self.__ok_save)
        self.more_options_btn.clicked.connect(self.__hide_show_alt_options)

    def __hide_show_alt_options(self):
        if self.alt_option.isVisible():
            self.alt_option.hide()
        else:
            self.alt_option.show()

    def __ok_save(self):
        self.__save_offline = True
        self.close()

    def __cancel_save(self):
        self.close()

    @property
    def save_offline_selected(self):
        return self.__save_offline

    def closeEvent(self, event):
        event.accept()


# from PyQt5.QtWidgets import QApplication
# import sys
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     G = MissingOAuthFileError()
#     sys.exit(app.exec_())
