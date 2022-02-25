# This file handles all top-level tabs in DAATA

from PyQt5 import QtWidgets
from functools import partial


# Creates tab widget for apps
def create_tab_widget(self):
    for index in range(self.tabWidget.count()):
        self.tabWidget.removeTab(0)
    self.create_scene_tab(
        'Data Collection')  # sets default tab that pops up in scenes
    self.tabWidget_central.setCurrentIndex(
        self.tabWidget_central.indexOf(
            self.tab_homepage))  # temporary measure to default to homepage on startup
    self.tabWidget.setStyleSheet("""

    """)


tabInstances = 0  # a counter for the number of tabs created in current session


def create_scene_tab(self, key, preview_only: bool = False,
                     initial_data_filepath: str = None,
                     file_metadata: dict = None):
    # from Utilities.Settings import settings_load, settings_save
    global tabInstances

    if preview_only:
        if initial_data_filepath:
            tab = self.dict_scenes[key]['create_scene'](initial_data_filepath,
                                                        file_metadata)
        else:
            return
    else:
        tab = self.dict_scenes[key]['create_scene']()
    tab.setObjectName(key + " (instance " + str(
        tabInstances) + ")")  # set object names for each tab's widget (allows duplicate widgets to have a functional parent/child relationship)
    self.tabWidget.addTab(tab, key)
    self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(tab))
    self.tabWidget_central.setCurrentIndex(
        self.tabWidget_central.indexOf(self.tab_scenes))

    tabInstances += 1


def rename_tab(self, index):
    text, okPressed = QtWidgets.QInputDialog.getText(self, "Rename Tab",
                                                     "New Name:",
                                                     QtWidgets.QLineEdit.Normal,
                                                     "")
    if okPressed and text != '':
        self.tabWidget.setTabText(index, text)


def close_tab(self, parent, index):
    ans = QtWidgets.QMessageBox.warning(parent, "Warning",
                                        "Do you want to close this tab? Any unsaved progress will be lost",
                                        QtWidgets.QMessageBox.Close | QtWidgets.QMessageBox.Cancel)
    # self.setWindowIcon(QtGui.QIcon(os.directory.join(os.directory.dirname(__file__), 'iconWarning.png')))
    if ans == QtWidgets.QMessageBox.Close:
        widget = parent.tabWidget.widget(index)
        if widget is not None:
            widget.deleteLater()
        parent.tabWidget.removeTab(index)

    widget.closeEvent()
