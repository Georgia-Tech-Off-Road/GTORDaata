from PyQt5 import QtWidgets, uic
import os

# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'missing_oAuth.ui'))


class MissingOAuthFile(QtWidgets.QDialog, uiFile):
    def __init__(self):
        super().__init__()
        self.__save_offline = False

        self.setupUi(self)
        self.__connectSlotsSignals()
        self.exec()

    def __connectSlotsSignals(self):
        self.cancel_button.clicked.connect(self.__cancel_save)
        self.yes_button.clicked.connect(self.__ok_save)

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
