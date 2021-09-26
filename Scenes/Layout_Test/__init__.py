from PyQt5 import QtWidgets, uic, QtCore, QtGui
import os
from Scenes import DAATAScene


uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'testLayout.ui'))  # loads the .ui file from QT Desginer

class Widget_Test(DAATAScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.hide()
        self.update_period = 3  # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)

    def update_active(self):
        pass
