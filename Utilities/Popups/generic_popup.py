import logging
from PyQt5 import QtWidgets, uic
import os

logger = logging.getLogger("NoInternet")
# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'generic_popup.ui'))


class GenericPopup(QtWidgets.QDialog, uiFile):
    def __init__(self, heading1: str, heading2: str = ""):
        super().__init__()
        self.setupUi(self)
        self.update_message(heading1, heading2)
        self.connectSlotsSignals()
        self.exec()

    def update_message(self, heading1: str, heading2: str):
        self.heading1_text.setText(heading1)
        self.heading2_text.setText(heading2)

    def connectSlotsSignals(self):
        self.ok_button.clicked.connect(self.close_popup)

    def close_popup(self):
        self.close()
