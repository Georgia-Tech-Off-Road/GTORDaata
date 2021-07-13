from PyQt5 import QtWidgets, uic, QtCore, QtGui
import os
from Scenes import BaseScene


uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'testScene.ui'))  # loads the .ui file from QT Desginer

class Widget_Test(BaseScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.hide()

    def update(self):
        pass
