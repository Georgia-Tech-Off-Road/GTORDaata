from PyQt5 import uic, QtWidgets, QtGui, QtCore


from functools import partial
import threading
import logging
import os
import time
import sys
import serial

from Scenes import DAATAScene
from Scenes.Homepage import Homepage
from Scenes.DataCollection import DataCollection
from Scenes.EngineDyno import EngineDyno
from Scenes.Layout_Test import Widget_Test
from Scenes.BlinkLEDTest import BlinkLEDTest
from Scenes.EngineDynoExp import EngineDynoExp


from Utilities.Popups.popups import popup_ParentChildrenTree
from MainWindow._tabHandler import close_tab
import DataAcquisition


from DataAcquisition import is_data_collecting, data_import, stop_thread
from DataAcquisition.DataImport import DataImport
from Utilities.DataImport.import_google_drive_popup import \
    import_google_drive_popup

import re, itertools
import winreg as winreg

logger = logging.getLogger("MainWindow")


Ui_MainWindow, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'MainWindow.ui'))  # loads the .ui file from QT Desginer


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Create the thread and timer objects to manage data communication with microcontrollers
        self.data_sending_thread = QtCore.QTimer()
        self.data_sending_thread.timeout.connect(DataAcquisition.send_data)

        self.data_reading_thread = threading.Thread(target=DataAcquisition.read_data)

        # Attach the internal timer
        data_import.attach_internal_sensor(101)

        # Set up all the elements of the UI
        self.setupUi(self)

        self.dict_scenes = {}  # instantiates dictionary that holds objects for widgets
        self.import_scenes()
        self.dict_ports = {}
        self.import_coms()
        self.create_tab_widget()
        self.populate_menu()
        self.set_app_icon()
        self.load_stylesheet()
        self.create_homepage()

        # self.settings_debug()
        # self.settings_load()

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
                        if (self.update_counter_active % scene.update_period) == 0:
                            scene.update_active()
                    except Exception:
                        pass

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

    def load_stylesheet(self):
        stylesheet = """        
        
        /*  General color scheme  */

        
        /*  MainWindow color scheme  */
        QMainWindow {{
            background: {bgColor};
            }}

        QMainWindow [objectName^="tab_scenes"] {{
            background: {bgColor};
            }}
        QMainWindow QTabWidget {{
            }}
        QStackedWidget {{
            background-color: {bgColor2};
        }}
        QMenuBar {{
            background: white;
            }}
        QMenuBar::item {{
            padding: 4px;
            background: transparent;
            border-right: 1px solid lightGray;

            }}
        QMenuBar::item:selected {{
            background: rgb(237,237,237,100);
            }}
        
        
        
        /*  DataCollection scene color scheme   */
        DataCollection QWidget {{
            background-color: {foreColor};
            }}
        DataCollection QPushButton {{
            background-color: white;
            }}
        DataCollection CustomPlotWidget {{
            border-radius: 7px;
            border: 1px solid gray;
            }}
        
        
        
        /*  Homepage scene color scheme */
        Homepage .QWidget {{
            background-color: {foreColor};
            }}
        Homepage .QFrame {{
            background-color: {foreColor};
            }}
            

            
        """

        stylesheet = stylesheet.format(
            testColor = "pink",
            bgColor = "#dbcc93",
            bgColor2 = "#white",
            foreColor = "#f4f4f4",
            # windowBorder = "#B3A369",
            windowBorder = "white",
            defaultText = "white"
            )
        self.setStyleSheet(stylesheet)

    def import_scenes(self):
        """
        This function used ot add the different scenes to the application.

        :return: None
        """
        self.dict_scenes = {
            'Data Collection': {
                'create_scene': DataCollection
            },

            'Layout Test': {
                'create_scene': Widget_Test
            },

            'Engine Dyno': {
                'create_scene': EngineDyno
            },

            'Blink LED Test': {
                'create_scene': BlinkLEDTest
            },

            'Engine Dyno Exp': {
                'create_scene': EngineDynoExp
            }
        }

    def enumerate_serial_ports(self):
        """ Uses the Win32 registry to return an
            iterator of serial (COM) ports
            existing on this computer.
        """
        path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        except WindowsError:
            raise StopIteration

        for i in itertools.count():
            try:
                val = winreg.EnumValue(key, i)
                yield str(val[1])
            except EnvironmentError:
                break

    def import_coms(self):
        self.dict_ports["Auto"] = None #adds the Auto option no matter what
        for portName in self.enumerate_serial_ports():
            self.dict_ports[portName] = None

    def create_homepage(self):
        """
        This function creates the homepage
        :return:
        """
        self.homepage = Homepage()
        self.homepage.setObjectName("Homepage")
        self.gridLayout_tab_homepage.addWidget(self.homepage)
        # self.tabWidget.setCornerWidget(self.homepage.button, corner = Qt.Corner.TopRightCorner)

    def COMInputMode(self):
        for key in self.dict_ports.keys():
            ## what happens if the user has multiple options selected?
            ## what happens if the user changes their selection?
            if self.dict_ports[key].isChecked():
                self.setInputMode(key)              

    def setInputMode(self, input_mode):
        print("Input Mode:", input_mode)
        data_import.input_mode = input_mode
        if not self.data_reading_thread.is_alive():
            self.data_reading_thread.start()
        if "COM" in data_import.input_mode:
            data_import.connect_serial()
            if not self.data_sending_thread.isActive():
                self.data_sending_thread.start(100)
                print("We did it!")
        else:
            # implement the CSV and BIN Parsers depending on the input mode value
            pass

    def import_from_google_drive(self):
        import_google_drive_popup()

    def connect_signals_and_slots(self):
        """
        This functions connects all the Qt signals with the slots so that elements such as buttons or checkboxes
        can be tied to specific functions.

        :return: None
        """

        for key in self.dict_scenes.keys():
            self.dict_scenes[key]['menu_action'].triggered.connect(partial(self.create_scene_tab, key))

        ## Handles event of a COM port being selected
        for key in self.dict_ports.keys():
            self.dict_ports[key].triggered.connect(lambda: self.COMInputMode())

        ## Functionality for the following menu items
        self.actionFake_Data.triggered.connect(lambda: self.setInputMode("FAKE"))
        self.actionBIN_File.triggered.connect(lambda: self.setInputMode("BIN"))
        self.actionCSV_File.triggered.connect(lambda: self.setInputMode("CSV"))
        self.import_Google_Drive.\
            triggered.connect(lambda: self.import_from_google_drive())

        self.tabWidget.tabBarDoubleClicked.connect(self.rename_tab)
        self.tabWidget.tabCloseRequested.connect(partial(self.close_tab, self))
        self.action_parentChildrenTree.triggered.connect(partial(popup_ParentChildrenTree, self))
        self.action_Preferences.triggered.connect(self.SettingsDialog)

    # --- Imported methods --- #
    from ._tabHandler import create_tab_widget, create_scene_tab, rename_tab, close_tab
    from ._menubarHandler import populate_menu
    from Utilities.Settings.SettingsDialog import SettingsDialog

    # --- Overridden event methods --- #
    def closeEvent(self, event):
        self.data_sending_thread.stop()
        stop_thread.set()
        self.data_reading_thread.join()
        self.timer_active.stop()
        self.timer_passive.stop()
        sys.exit()
        ##  Close Confirmation Window
        # close = QtWidgets.QMessageBox()
        # close.setText("Close DAATA?")
        # close.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        # close = close.exec()
        # if close == QtWidgets.QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()

## The line QtGui.QStyleOption() will throw an error
    '''
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
    '''