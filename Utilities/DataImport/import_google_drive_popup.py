import logging
from PyQt5 import QtWidgets, uic
import os

logger = logging.getLogger("ImportGoogleDrive")
# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'import_google_drive_popup.ui'))


class import_google_drive_popup(QtWidgets.QDialog, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.custom_props_input.hide()
        self.connectSlotsSignals()
        self.exec()

    def connectSlotsSignals(self):
        self.accepted.connect(self.display_data)
        self.rejected.connect(self.close_popup)
        # self.adv_options_button.clicked.connect(self.hide_show_adv_options)


    def hide_show_adv_options(self):
        self.adv_options_widget.show()


    def display_data(self):
        self.close_popup()

    def close_popup(self):
        self.close()




