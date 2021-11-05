import logging
from PyQt5 import QtWidgets, uic
import os

logger = logging.getLogger("NoInternet")
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'no_internet_popup.ui'))  # loads the .ui file from QT Designer

class no_internet_popup(QtWidgets.QDialog, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connectSlotsSignals()
        self.exec()

    def connectSlotsSignals(self):
        self.okButton.clicked.connect(self.close_popup)

    def close_popup(self):
        self.close()
