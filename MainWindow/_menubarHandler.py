## This file handles all menubar methods in DAATA

from PyQt5 import QtWidgets


def populate_menu(self):
    create_addLayoutMenu(self)
    create_fileMenu(self)
    create_comMenu(self)

def create_addLayoutMenu(self):
    ## Make an action to create a tab for each imported widget
    for key in self.dict_scenes.keys():
        self.dict_scenes[key]['menu_action'] = QtWidgets.QAction(self)
        self.dict_scenes[key]['menu_action'].setCheckable(False)
        self.dict_scenes[key]['menu_action'].setToolTip('Open a new tab for ' + key)
        self.dict_scenes[key]['menu_action'].setText(key)
        self.menuAdd_Layout.addAction(self.dict_scenes[key]['menu_action'])


def create_fileMenu(self):
    ## Create an action for Preferences
    self.action_Preferences = QtWidgets.QAction(self)
    self.action_Preferences.setCheckable(False)
    self.action_Preferences.setToolTip("Edit application config_MainWindow")
    self.action_Preferences.setText("Preferences")
    self.menuFile.addAction(self.action_Preferences)

def create_comMenu(self):
    ## Create an action for COM port
    for key in self.dict_ports.keys():
        self.dict_ports[key] = QtWidgets.QAction(self)
        self.dict_ports[key].setCheckable(True)
        self.dict_ports[key].setText(key)
        self.menuCOM_Port.addAction(self.dict_ports[key])



# class MenuAction:
#     ## Make an action to create a tab for each imported widget
#     for key in self.dict_scenes.keys():
#         self.dict_scenes[key]['menu_action'] = QtWidgets.QAction(self)
#         self.dict_scenes[key]['menu_action'].setCheckable(False)
#         self.dict_scenes[key]['menu_action'].setToolTip('Open a new tab for ' + key)
#         self.dict_scenes[key]['menu_action'].setText(key)
#         self.menuWidget.addAction(self.dict_scenes[key]['menu_action'])
#
#     ## Make an action in the File menu to display current parent and children tree
#     self.action_parentChildren = QtWidgets.QAction(self)
#     self.action_parentChildren.setToolTip(
#         'Display a tree of all parent objects and their respective children for the current UI gridPlotLayout')
#     self.action_parentChildren.setText('Display parent/children tree')
#     self.menuFile.addAction(self.action_parentChildren)
