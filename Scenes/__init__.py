from PyQt5 import QtWidgets
from abc import ABCMeta, abstractmethod


class DAATAScene(QtWidgets.QWidget):
    def __init__(self, **kwargs):
        super().__init__()
        __metaclass__ = ABCMeta

        self.update_period = 100        # refresh 1 time a second

    @abstractmethod
    def update_active(self):
        raise NotImplementedError






