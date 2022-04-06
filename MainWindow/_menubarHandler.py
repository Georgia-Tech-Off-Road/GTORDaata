## This file handles all menubar methods in DAATA

from PyQt5 import QtWidgets


def populate_menu(self):
    create_addLayoutMenu(self)
    create_fileMenu(self)
    update_comMenu(self)
    create_google_drive_menu(self)


def create_addLayoutMenu(self):
    ## Make an action to create a tab for each imported widget
    for key in self.dict_scenes.keys():
        self.dict_scenes[key].menu_action = QtWidgets.QAction(self)
        self.dict_scenes[key].menu_action.setCheckable(False)
        self.dict_scenes[key].menu_action.setToolTip(
            'Open a new tab for ' + key)
        self.dict_scenes[key].menu_action.setText(key)
        if self.dict_scenes[key].is_preview_scene:
            self.dict_scenes[key].menu_action.setVisible(False)
        self.menuAdd_Layout.addAction(self.dict_scenes[key].menu_action)


def create_fileMenu(self):
    # Create an action for Preferences
    self.action_Preferences = QtWidgets.QAction(self)
    self.action_Preferences.setCheckable(False)
    self.action_Preferences.setToolTip("Edit application config_MainWindow")
    self.action_Preferences.setText("Preferences")
    self.menuFile.addAction(self.action_Preferences)


def update_comMenu(self):
    # Clear the list of COM ports
    self.menuCOM_Port.clear()
    # Create an action for each available COM port
    for key in self.dict_ports.keys():
        self.dict_ports[key] = QtWidgets.QAction(self)
        self.dict_ports[key].setCheckable(True)
        self.dict_ports[key].setText(key)
        self.menuCOM_Port.addAction(self.dict_ports[key])


def create_google_drive_menu(self):
    # Add import from Google Drive button
    self.import_from_gDrive_widget = QtWidgets.QAction(self)
    self.import_from_gDrive_widget.setCheckable(False)
    self.import_from_gDrive_widget.setToolTip("Import from Google Drive")
    self.import_from_gDrive_widget.setText("Import from Google Drive")
    self.google_drive_menu.addAction(self.import_from_gDrive_widget)

    # Add upload all to Google Drive button
    self.upload_remaining_gDrive_widget = QtWidgets.QAction(self)
    self.upload_remaining_gDrive_widget.setCheckable(False)
    self.upload_remaining_gDrive_widget.setToolTip(
        "Upload remaining files to Google Drive")
    self.upload_remaining_gDrive_widget.setText("Upload all remaining files")
    self.google_drive_menu.addAction(self.upload_remaining_gDrive_widget)

    # Add upload manual to Google Drive button
    self.manual_upload_gDrive_widget = QtWidgets.QAction(self)
    self.manual_upload_gDrive_widget.setCheckable(False)
    self.manual_upload_gDrive_widget.setToolTip(
        "Upload one file manually to Google Drive")
    self.manual_upload_gDrive_widget.setText("Upload a file manually")
    self.google_drive_menu.addAction(self.manual_upload_gDrive_widget)

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
