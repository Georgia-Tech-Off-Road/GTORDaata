from PyQt5 import QtWidgets, uic
import os

# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'generic_popup.ui'))


class GenericPopup(QtWidgets.QDialog, uiFile):
    def __init__(self, heading1: str, heading2: str = ""):
        super().__init__()
        self.setupUi(self)
        self.__update_message(heading1, heading2)
        self.__connectSlotsSignals()
        self.exec()

    def __update_message(self, heading1: str, heading2: str):
        self.heading1_text.setText(heading1)
        self.heading2_text.setText(heading2)

    def __connectSlotsSignals(self):
        self.ok_button.clicked.connect(self.close)

    def closeEvent(self, event):
        event.accept()


# from PyQt5.QtWidgets import QApplication
# import sys
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     G = GenericPopup("blob", "blob2")
#     sys.exit(app.exec_())
