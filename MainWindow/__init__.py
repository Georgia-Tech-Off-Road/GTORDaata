from PyQt5 import uic, QtWidgets, QtGui, QtCore

from dataclasses import dataclass
from functools import partial
from typing import Dict
import logging
import os
import sys
import threading

from Scenes import DAATAScene
from Scenes.Homepage import Homepage
from Scenes.DataCollection import DataCollection
from Scenes.ShockDyno import ShockDyno
from Scenes.Layout_Test import Widget_Test
from Scenes.BlinkLEDTest import BlinkLEDTest
from Scenes.DataCollection import DataCollection
from Scenes.DataCollectionPreview import DataCollectionPreview
from Scenes.EngineDyno import EngineDyno
from Scenes.EngineDynoPreview import EngineDynoPreview
from Scenes.Homepage import Homepage
from Scenes.Layout_Test import Widget_Test
from Scenes.MultiDataGraph import MultiDataGraph
from Scenes.MultiDataGraphPreview import MultiDataGraphPreview

from MainWindow._tabHandler import close_tab
from Utilities.Popups.popups import popup_ParentChildrenTree
import DataAcquisition

from DataAcquisition import is_data_collecting, data_import, stop_thread
from Utilities.OpenCSVFile import OpenCSVFile
from Utilities.DataExport.dataFileExplorer import open_data_file
from Utilities.GoogleDriveHandler.GDriveDataExport import CreateUploadJSON
from Utilities.GoogleDriveHandler.GDriveDataExport.upload_all_drive_files import \
    UploadDriveFiles
from Utilities.GoogleDriveHandler.GDriveDataImport import \
    GDriveDataImport as GoogleDriveDataImport
from Utilities import general_constants

# import breeze_resources

import itertools
import winreg as winreg

logger = logging.getLogger("MainWindow")

Ui_MainWindow, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                               'MainWindow.ui'))  # loads the .ui file from QT Desginer


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Create the thread and timer objects to manage data communication with microcontrollers
        self.data_sending_thread = QtCore.QTimer()
        self.data_sending_thread.timeout.connect(DataAcquisition.send_data)

        self.data_reading_thread = threading.Thread(
            target=DataAcquisition.read_data)

        # Attach the internal timer
        data_import.attach_internal_sensor(101)
        data_import.attach_output_sensor(9)        

        # Set up all the elements of the UI
        self.setupUi(self)

        # instantiates dictionary that holds objects for widgets
        self.dict_scenes: Dict[str, _Scene] = {}

        self.import_scenes()
        self.dict_ports = {}
        self.import_coms()
        self.create_tab_widget()
        self.populate_menu()
        self.set_app_icon()
        self.set_stylesheet()
        self.create_homepage()

        # Create the timer objects to manage scene updating.
        self.update_counter_active = 0
        self.timer_active = QtCore.QTimer()
        self.timer_active.timeout.connect(self.update_active)
        self.timer_active.start(10)  # Call update_active every 10 ms (100 Hz)

        self.timer_passive = QtCore.QTimer()
        self.timer_passive.timeout.connect(self.update_passive)

        # Call update_passive every 1000 ms (1 Hz)
        self.timer_passive.start(1000)

        # Lastly, connect all signals and slots
        self.connect_signals_and_slots()

    def update_active(self):
        """
        This function will update every scene at their specified update_period. The update_period is always a multiple of
        10 ms. So an update_period of 3 will update the scene every 3*10=30ms.

        This function will only update the scene if it is visible. It calls the relevant update_active function for
        the visible scene. If the scene doesn't have an update_active function or doesn't specify an update_period,
        it will not get updated.

        :return: None
        """

        self.update_counter_active = self.update_counter_active + 1

        if self.tab_homepage.isVisible():
            if (self.update_counter_active % self.homepage.update_period) == 0:
                self.homepage.update_active()

        if self.tab_scenes.isVisible():
            for scene in self.tabWidget.findChildren(DAATAScene):
                if scene.isVisible():
                    try:
                        if (
                                self.update_counter_active % scene.update_period) == 0:
                            scene.update_active()
                    except Exception as e:
                        logger.error(e)
                        logger.debug(logger.findCaller(True))

    def update_passive(self):
        """
        This function will update all scenes at 1 Hz regardless of if they are active or not. It calls every scene's
        update_passive function. If the scene doesn't have an update_passive function, then it won't get updated.

        :return: None
        """

        self.homepage.update_passive()
        for scene in self.tabWidget.findChildren(DAATAScene):
            scene.update_passive()

    def set_app_icon(self):
        """
        This method sets the app icon on the taskbar and titlebar.

        :return: None
        """

        import ctypes
        myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        path = os.path.join(os.path.dirname(__file__), 'icon_GTORLogo.png')
        self.setWindowIcon(QtGui.QIcon(path))

    def set_stylesheet(self):
        """
        Sets the color styles of the UI elements using the specified colors
        by passing to style function in QTWidgets.pyi.

        :return: None
        """

        stylesheet = """
        /*  MainWindow color scheme  */        
        QMainWindow {{
            background: {bg_color};
            color: {default_text};
            }}

        QMainWindow [objectName^="tab_scenes"] {{
            background: {bg_color};
            color: {default_text};
            }}
        QMainWindow QTabWidget {{
            }}
        QStackedWidget {{
            background-color: {bg_color_2};
            color: {default_text};
        }}
        QMenuBar {{
            background: {bg_color};
            color: {default_text};
            }}
        QMenuBar::item {{
            padding: 4px;
            background: transparent;
            border-right: 1px solid lightGray;
            background-color: {bg_color_2};
            color: {default_text};
            }}
        QMenuBar::item:selected {{
            background: {bg_color};
            color: {default_text};
            }}
        
        
        
        /*  DataCollection scene color scheme   */
        DataCollection QWidget {{
            background-color: {bg_color};
            color: {default_text};
            }}
        DataCollection QPushButton {{
            background-color: {bg_color_2};
            color: {default_text};
            }}
        DataCollection CustomPlotWidget {{
            border-radius: 7px;
            border: 1px solid gray;
            background-color: {bg_color_2};
            color: {default_text};
            }}
        
        
        
        /*  Homepage scene color scheme */
        Homepage QWidget {{
            background-color: {bg_color};
            color: {default_text};
            }}
        Homepage QFrame {{
            background-color: {bg_color};
            color: {default_text};
            }}
        
        """

        stylesheet = stylesheet.format(
            test_color="pink",
            bg_color="#28292b",
            bg_color_2="#A9A9A9",
            fore_color="#f4f4f4",
            window_border="white",
            default_text="white"
        )

        self.setStyleSheet(stylesheet)

    def import_scenes(self):
        """
        Populates scene dictionary with the class names of each scene.

        :return: None
        """

        self.dict_scenes = {
            'Data Collection': _Scene(DataCollection, "DataCollection"),

            'Data Collection Preview':
                _Scene(DataCollectionPreview, "DataCollectionPreview", True),

            'Layout Test': _Scene(Widget_Test, "Layout_Test"),

            'Engine Dyno': _Scene(EngineDyno, "EngineDyno"),

            'Shock Dyno': {
                'create_scene' : ShockDyno
            },

            'Blink LED Test': _Scene(BlinkLEDTest, "BlinkLEDTest"),

            'Multi Data Graph': _Scene(MultiDataGraph, "MultiDataGraph"),

            'Multi Data Graph Preview':
                _Scene(MultiDataGraphPreview, "MultiDataGraphPreview", True),
        }

        return self.dict_scenes

    @staticmethod
    def enumerate_serial_ports():
        """ 
        Uses the Win32 registry to return an iterator of serial (COM) ports
        existing on this computer.

        :return: None
        """

        path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        except WindowsError:
            logger.debug(logger.findCaller(True))
            raise StopIteration

        for i in itertools.count():
            try:
                val = winreg.EnumValue(key, i)
                yield str(val[1])
            except EnvironmentError:
                logger.debug(logger.findCaller(True))
                break

    def import_coms(self):
        """
        Updates port dictionary with the active COM ports found.

        :return: None
        """
        
        # adds the Auto option no matter what
        self.dict_ports["Auto"] = None
        for portName in self.enumerate_serial_ports():
            print(portName)
            self.dict_ports[portName] = None

    def create_homepage(self):
        """
        Creates the homepage seen on start from Homepage.__init__.py and attaches it to a 
        widget to be shown in the MainWindow UI element.

        :return: None
        """
        self.homepage = Homepage()
        self.homepage.setObjectName("Homepage")
        self.gridLayout_tab_homepage.addWidget(self.homepage)

    def com_input_mode(self):
        """
        Sets the input mode to whichever serial port is checked.

        :return: None
        """        

        for key in self.dict_ports.keys():
            if self.dict_ports[key].isChecked():
                self.set_input_mode(key)

    def set_input_mode(self, input_mode):
        """
        Assigns input mode based on button triggers handled in connect_signals_and_slots() from input 
        mode drup down in main window.
        
        return: None
        """

        data_import.teensy_found = False
        data_import.data_file = None

        logger.info("Input Mode: " + str(input_mode))
        data_import.input_mode = input_mode
        if data_import.input_mode == "BIN":
            try:
                directory = open_data_file(".bin")
                if directory != "":
                    is_data_collecting.set()
                    data_import.open_bin_file(directory)
                else:
                    data_import.input_mode = ""
                    logger.info(
                        "You must open a BIN file before changing to BIN input mode")
            except Exception as e:
                logger.error(e)
                logger.debug(logger.findCaller(True))
        # elif data_import.input_mode == "CSV":
        #     try:
        #         directory = open_data_file(".csv")
        #         if directory != "":
        #             is_data_collecting.set()
        #             data_import.import_csv(directory)
        #         else:
        #             logger.info(
        #                 "You must open a CSV file before changing to CSV input mode")
        #     except Exception as e:
        #         logger.error(e)
        #         logger.debug(logger.findCaller(True))
        #     finally:
        #         data_import.input_mode = ""
        if "COM" in data_import.input_mode:            
            data_import.connect_serial()
            if not self.data_sending_thread.isActive():
                self.data_sending_thread.start(100)
                logger.info("We connected to serial!")
        if input_mode != "" and not self.data_reading_thread.is_alive() and input_mode != "Auto":
            self.data_reading_thread.start()

    def __import_from_google_drive(self):
        """
        Opens a 'GDriveDataImport' window asking which file to import from
        Google Drive and display on the graph. Once a file is selected,
        the 'GDriveDataImport' window is closed and a new scene tab is opened
        with the data in that file. Currently, only supports .csv files.

        :return: None
        """
        # filepath is "" if an error occurred
        filepath, file_metadata = GoogleDriveDataImport(self.dict_scenes) \
            .selected_filepath_and_metadata
        if filepath:
            self.__create_preview_scene_tab(filepath, file_metadata)

    @staticmethod
    def __upload_remaining_to_gdrive():
        UploadDriveFiles()

    @staticmethod
    def __manual_upload_to_gdrive():
        CreateUploadJSON()

    # @property
    # def all_scenes(self) -> dict:
    #     return self.dict_scenes

    def __create_preview_scene_tab(self, filepath: str,
                                   file_metadata: dict = None,
                                   selected_scene: str = ""):
        file_formal_scene: str = ""
        if selected_scene:
            file_formal_scene = selected_scene
        elif file_metadata and file_metadata.get("properties"):
            file_formal_scene = file_metadata.get("properties").get("scene")
        if file_formal_scene in general_constants.DISPLAYABLE_IMPORTED_SCENES:
            logger.info(
                f"Displaying imported {file_formal_scene} scene "
                f"of {os.path.basename(filepath)}...")
        else:
            logger.warning(
                f"Scene {file_formal_scene} of {os.path.basename(filepath)} "
                f"not supported")
            return

        if file_formal_scene == "DataCollection":
            self.create_scene_tab("Data Collection Preview", True,
                                  initial_data_filepath=filepath,
                                  file_metadata=file_metadata)
        elif file_formal_scene == "EngineDyno":
            self.create_scene_tab("Engine Dyno Preview", True,
                                  initial_data_filepath=filepath,
                                  file_metadata=file_metadata)
        elif file_formal_scene == "MultiDataGraph":
            self.create_scene_tab("Multi Data Graph Preview", True,
                                  initial_data_filepath=filepath,
                                  file_metadata=file_metadata)

    def __open_csv_file(self):
        selected_filepath, scene = OpenCSVFile(
            self.dict_scenes).selected_filepath_scene
        if selected_filepath and scene:
            self.__create_preview_scene_tab(selected_filepath, None, scene)

    def __toggle_fake_input_option(self):
        if self.actionFake_Data.isChecked():
            self.set_input_mode("FAKE")
            self.actionFake_Data.setDisabled(True)

    def connect_signals_and_slots(self):
        """
        This function connects all the Qt signals with the slots so that
        elements such as buttons or checkboxes can be tied to specific
        functions.

        :return: None
        """

        for key in self.dict_scenes.keys():
            self.dict_scenes[key].menu_action.triggered.connect(
                partial(self.create_scene_tab, key))

        ## Handles event of a COM port being selected
        for key in self.dict_ports.keys():
            self.dict_ports[key].triggered.connect(
                lambda: self.com_input_mode())

        ## Functionality for the following menu items
        self.actionFake_Data.triggered.connect(self.__toggle_fake_input_option)
        self.actionBIN_File.triggered.connect(
            lambda: self.set_input_mode("BIN"))
        self.openCSV_File.triggered.connect(self.__open_csv_file)

        self.import_from_gDrive_widget.triggered.connect(
            self.__import_from_google_drive)
        self.upload_remaining_gDrive_widget.triggered.connect(
            self.__upload_remaining_to_gdrive)
        self.manual_upload_gDrive_widget.triggered.connect(
            self.__manual_upload_to_gdrive)

        self.tabWidget.tabBarDoubleClicked.connect(self.rename_tab)
        self.tabWidget.tabCloseRequested.connect(partial(self.close_tab, self))
        self.action_parentChildrenTree.triggered.connect(
            partial(popup_ParentChildrenTree, self))
        self.action_Preferences.triggered.connect(self.SettingsDialog)

    # --- Imported methods --- #
    from ._tabHandler import create_tab_widget, create_scene_tab, rename_tab, \
        close_tab
    from ._menubarHandler import populate_menu
    from Utilities.Settings.SettingsDialog import SettingsDialog

    # --- Overridden event methods --- #
    def closeEvent(self, event):
        """
        Handles closing all of our threads and timers when the application
        is being closed.

        :return: None
        """

        if data_import.teensy_found:            
            data_import.teensy_ser.close()

        stop_thread.set()
        if self.data_sending_thread.isActive():
            self.data_sending_thread.stop()
        if self.data_reading_thread.isAlive():
            self.data_reading_thread.join()
        self.timer_active.stop()
        self.timer_passive.stop()
        sys.exit()

    def paintEvent(self, pe):
        """
        This method allows the color scheme of the class to be changed by CSS stylesheets

        :param pe:
        :return: None
        """

        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()
        s.drawPrimitive(QtGui.QStyle.PE_Widget, opt, p, self)


@dataclass
class _Scene:
    create_scene: type
    formal_name: str
    is_preview_scene: bool = False
    preview_scene: type = None
    menu_action: QtWidgets.QAction = None
