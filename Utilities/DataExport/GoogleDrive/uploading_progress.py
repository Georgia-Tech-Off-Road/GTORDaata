import logging
from PyQt5 import QtWidgets, uic
import os

logger = logging.getLogger("UploadingProgress")
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'uploading_progress.ui'))  # loads the .ui file from QT Designer

class uploading_progress(QtWidgets.QDialog, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connectSlotsSignals()
        self.exec()
