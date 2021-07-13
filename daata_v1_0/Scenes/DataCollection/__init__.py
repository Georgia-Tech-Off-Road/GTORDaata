from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QPalette
import os

import pyqtgraph as pg
from functools import partial
import time
import DataAcquisition
from DataAcquisition import data
from Utilities.CustomWidgets.Plotting import CustomPlotWidget, GridPlotLayout
from Scenes import BaseScene
import logging

## Default plot configuration for pyqtgraph
pg.setConfigOption('background', 'w')   # white
pg.setConfigOption('foreground', 'k')   # black


uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'data_collection.ui'))  # loads the .ui file from QT Desginer

logger = logging.getLogger("DataCollection")
debugCounter = 0;

#Todo List      ####################################
## add refresh button in menu to scan for hardware changes when a new sensor is plugged in, to add a checkbox and graph for it
## add warning dialog if trying to start recording object while teensy is not plugged in (checked with object.is_connected)

class DataCollection(BaseScene, uiFile):
    def __init__(self, thread, is_data_collecting):
        super().__init__()
        self.setupUi(self)
        self.hide()
        self.updateFreq = 30   # how fast the graphs update in Hz


        self.data = DataAcquisition.data
        self.dict_sensors = {}  # instantiates sensor dictionary
        self.currentKeys = list()
        for key in self.data.get_sensors(is_plottable=True):
            self.dict_sensors[key] = dict()
            self.currentKeys.append(key)

        self.gridPlotLayout = GridPlotLayout(self.scrollAreaWidgetContents)
        self.gridPlotLayout.setObjectName("gridPlotLayout")
        self.scrollAreaWidgetContents.setLayout(self.gridPlotLayout)

        self.createSensorCheckboxes()
        self.createGraphDimensionComboBox()
        self.createGraphs()

        from MainWindow import is_data_collecting
        self.is_data_collecting = is_data_collecting

        self.connectSlotsAndSignals()
        self.configFile = QSettings('DAATA', 'data_collection')
        self.loadSettings()





    ## imported methods
    from Utilities.DataExport.dataSaveLocation import popup_dataSaveLocation
    from Utilities.Popups.popups import popup_stopDataConfirmation
    from Utilities.DataExport.exportMAT import saveMAT



    ## functions that are frequently called if the tab is visible
    def update(self):
        # update only
        # if the Data Collection tab is the current tab
        # or if the Scenes tab is the current tab

        if self.is_data_collecting.is_set():
            if self.button_display.isChecked():
                self.updateGraphs()
                self.updateTimeElapsed()
                # logger.debug('updating ' + self.objectName() + "...")



    ## functions that are occasionally called if the tab is visible
    def updateOccasional(self):
        self.updateSensorCheckboxes()

        #### temporary implementation of global recording button update
        if self.is_data_collecting.is_set():
            self.indicator_onOrOff.setText("On")
            self.indicator_onOrOff.setStyleSheet("color: green;")
            self.button_display.setText("Stop Collecting Data")
            self.button_display.setChecked(True)
        else:

            self.indicator_onOrOff.setText("Off")
            self.indicator_onOrOff.setStyleSheet("color: red;")
            self.button_display.setText("Start Collecting Data")
            self.button_display.setChecked(False)

    def connectSlotsAndSignals(self):
        self.button_display.clicked.connect(self.slotChangeDisplayingState)

        for key in self.currentKeys:
            self.dict_sensors[key]['checkbox'].clicked.connect(self.createGridPlotLayout)
            self.dict_sensors[key]['checkbox'].clicked.connect(self.saveSettings)

        self.selectAll_checkbox.stateChanged.connect(self.slotCheckboxSelectAll)

        self.comboBox_graphDimension.currentTextChanged.connect(self.createGridPlotLayout)
        self.comboBox_graphDimension.currentTextChanged.connect(self.saveSettings)

        ## connections to GridPlotLayout
        for key in self.dict_sensors.keys():
            widget = self.dict_sensors[key]['graph_widget']
            settings = widget.button_settings.clicked.connect(partial(self.dict_sensors[key]['graph_widget'].open_SettingsWindow))

    # Create checkboxes based on a list of strings
    #TODO make this update with Homepage if a new sensor gets connected ##################################################################
    def createSensorCheckboxes(self):
        self.selectAll_checkbox = QtWidgets.QCheckBox("Select All", self.scrollAreaWidgetContents_2, objectName="selectAll_checkbox")
        self.selectAll_checkbox.setToolTip(self.selectAll_checkbox.objectName())
        self.gridLayout_2.addWidget(self.selectAll_checkbox)

        ## create a checkbox for each sensor in dictionary in self.scrollAreaWidgetContents_2
        for key in self.currentKeys:
            self.dict_sensors[key]['checkbox'] = QtWidgets.QCheckBox(self.data.get_display_name(key), self.scrollAreaWidgetContents_2, objectName=key)
            self.gridLayout_2.addWidget(self.dict_sensors[key]['checkbox'])

        # Create a vertical spacer that forces checkboxes to the top
        spacerItem1 = QtWidgets.QSpacerItem(20, 1000000, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1)

    def createGraphDimensionComboBox(self):
        maxRows = 4
        maxCols = 3

        for row in range(1,maxRows+1):
            for col in range(1,maxCols+1):
                self.comboBox_graphDimension.addItem("{0}x{1}".format(row,col))

    def createGridPlotLayout(self):
        # self.gridPlotLayout = GridPlotLayout(self.scrollAreaWidgetContents)
        # self.gridPlotLayout.setObjectName("gridPlotLayout")
        # self.scrollAreaWidgetContents.setLayout(self.gridPlotLayout)

        currDim = self.comboBox_graphDimension.currentText().split('x')
        maxRows = int(currDim[0])
        maxCols = int(currDim[1])

        row = 0
        col = 0

        leftMar, topMar, rightMar, botMar = self.gridPlotLayout.getContentsMargins()
        hSpace = self.gridPlotLayout.horizontalSpacing()
        vSpace = self.gridPlotLayout.verticalSpacing()
        graphHeight = (self.scrollArea_graphs.height()-topMar-botMar-vSpace*(maxRows-1)) / maxRows

        # for data in self.dict_sensors.keys():
        #     if self.dict_sensors[data]['graph_widget'].isVisible():
        #         try:
        #             self.gridPlotLayout.removeWidget(self.dict_sensors[data]['graph_widget'])
        #             self.dict_sensors[data]['graph_widget'].hide()
        #         except:
        #             print(data + " is " + self.dict_sensors[data]['graph_widget'].isVisible())

        # TODO: find the lowest col and row that is empty to start adding widgets
        print("max rows = {}, max cols = {}".format(maxRows,maxCols))
        for temp_row in range(0, maxRows - 1):
            for temp_col in range(0,maxCols-1):
                print("checking position {}, {}".format(temp_row,temp_col))
                if self.gridPlotLayout.widgetAtPosition(temp_row, temp_col) == None:
                    col = temp_col
                    row = temp_row
                    print("\t empty spot".format(row, col))
                    break
                else:
                    print("\t object {} found ".format(self.gridPlotLayout.widgetAtPosition(temp_row, temp_col)))

            if self.gridPlotLayout.widgetAtPosition(temp_row, temp_col) == None:
                continue

        print("starting at {}, {}".format(row,col))


        for key in self.dict_sensors.keys():
            if self.dict_sensors[key]['checkbox'].isChecked() and not self.dict_sensors[key]['graph_widget'].isVisible():
                # self.dict_sensors[data]['graph_widget'] = CustomPlotWidget(data, parent=self.scrollAreaWidgetContents,
                #                                                       graph_width_seconds=10)
                # self.dict_sensors[data]['graph_widget'].setObjectName(data)

                # print(str(row) + "  " + str(col) + "   " + data)
                self.dict_sensors[key]['graph_widget'].set_height(graphHeight)
                self.gridPlotLayout.addWidget((self.dict_sensors[key]['graph_widget']), row, col, 1, 1)
                self.dict_sensors[key]['graph_widget'].show()
                # print("item at ({},{}) is {}".format(row,col,self.gridPlotLayout.widgetAtPosition(row,col)))

                col += 1
                if col == maxCols:
                    col = 1
                    row += 1
            else:
                self.dict_sensors[key]['graph_widget'].hide()
                pass

        # self.gridPlotLayout.moveWidgetDown(self.dict_sensors['bl_lds']['graph_widget'])
        # self.scrollAreaWidgetContents.setLayout(self.gridPlotLayout)

        self.spacerItem_gridPlotLayout = QtWidgets.QSpacerItem(20, 1000000, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridPlotLayout.addItem(self.spacerItem_gridPlotLayout)

    def createGraphs(self):
        for key in self.currentKeys:
            self.dict_sensors[key]['graph_widget'] = CustomPlotWidget(key, parent=self.scrollAreaWidgetContents, layout=self.gridPlotLayout, graph_width_seconds = 8)
            self.dict_sensors[key]['graph_widget'].setObjectName(key)
            self.dict_sensors[key]['graph_widget'].hide()

    def slotChangeDisplayingState(self):
        if self.button_display.isChecked():
            self.indicator_onOrOff.setText("On")
            self.indicator_onOrOff.setStyleSheet("color: green;")
            self.button_display.setText("Stop Collecting Data")
            self.is_data_collecting.set()
        else:
            self.indicator_onOrOff.setText("Off")
            self.indicator_onOrOff.setStyleSheet("color: red;")
            self.button_display.setText("Start Collecting Data")
            self.is_data_collecting.clear()
            self.popup_dataSaveLocation()
            # if self.popup_stopDataConfirmation() == QtWidgets.QDialog.Accepted:
            #     self.button_display.setText("Start Collecting Data")
            #     self.is_data_collecting.clear()
            #     self.popup_dataSaveLocation()

    def slotCheckboxSelectAll(self):
        if self.selectAll_checkbox.isChecked():
            for key in self.currentKeys:
                self.dict_sensors[key]['checkbox'].setChecked(True)
                # self.dict_sensors[data]['graph_widget'].show()
                # self.activeSensorCount = len(self.dict_sensors)
        else:
            for key in self.currentKeys:
                self.dict_sensors[key]['checkbox'].setChecked(False)
                # self.dict_sensors[data]['graph_widget'].hide()
            # self.activeSensorCount = 0
        # self.label_activeSensorCount.setText('(' + str(self.activeSensorCount) + '/' + str(len(self.dict_sensors)) + ')')
        self.updateSensorCount()
        self.createGridPlotLayout()

    def updateSensorCount(self):
        self.activeSensorCount = 0
        for key in self.dict_sensors.keys():
            if self.dict_sensors[key]['checkbox'].isVisible():
                if self.dict_sensors[key]['checkbox'].isChecked():
                    self.activeSensorCount = self.activeSensorCount + 1
        self.label_activeSensorCount.setText('(' + str(self.activeSensorCount) + '/' + str(len(self.dict_sensors)) + ')')

    ## make a checkbox for any newly connected sensors
    def updateSensorCheckboxes(self):
        connected_sensors = data.get_sensors(is_plottable = True, is_connected=True)
        for key in self.currentKeys:
            if key in connected_sensors:
                if self.dict_sensors[key]['checkbox'] is None:
                    self.dict_sensors[key]['checkbox'] = QtWidgets.QCheckBox(self.data.get_display_name(key), self.scrollAreaWidgetContents_2, objectName=key)
                else:
                    pass
            else:
                try:
                    self.scrollAreaWidgetContents_2.removeWidget(self.dict_sensors[key]['checkbox'])
                except:
                    pass

    def updateGraphs(self):
        for key in self.currentKeys:
            if self.dict_sensors[key]['graph_widget'].isVisible():
                self.dict_sensors[key]['graph_widget'].update_graph()

    ## change the text label for time elapsed for current run
    def updateTimeElapsed(self):
        try:
            sec = DataAcquisition.data.get_value("time_internal_seconds", DataAcquisition.data.get_most_recent_index())
            sty_res = time.gmtime(sec)
            res = time.strftime("%H:%M:%S",sty_res)
            self.label_timeElapsed.setText(res)
        except TypeError:
            pass

    ## save current configuration/settings
    def saveSettings(self):
        self.configFile.setValue('graph_dimension', self.comboBox_graphDimension.currentText())
        self.configFile.setValue('scrollArea_graphs_height', self.scrollArea_graphs.height())

        enabledSensors = []
        for key in self.dict_sensors.keys():
            if self.dict_sensors[key]['checkbox'].isChecked():
                enabledSensors.append(key)
        self.configFile.setValue('enabledSensors', enabledSensors)

        # logger.debug("Data Collection config files saved")
        # self.debug_settings()

    ## load the saved configuration/settings
    def loadSettings(self):
        try:
            activeSensorCount = 0
            for key in self.configFile.value('enabledSensors'):
                print(key)
                self.dict_sensors[key]['checkbox'].setChecked(True)
                activeSensorCount = activeSensorCount + 1
                self.label_activeSensorCount.setText(
                    '(' + str(activeSensorCount) + '/' + str(len(self.dict_sensors)) + ')')
        except TypeError or KeyError:
            logger.error("Possibly invalid data in config. May need to clear config file using self.configFile.clear()")
            pass

        self.comboBox_graphDimension.setCurrentText(self.configFile.value('graph_dimension'))
        # self.slot_graphDimension()
        self.createGridPlotLayout()
        # logger.debug("Data Collection config files loaded")
        # self.debug_settings()

    ## print what configuration/settings are saved
    def debugSettings(self):
        for key in self.configFile.allKeys():
            print(key + ":\t\t" + str(self.configFile.value(key)))

    ##################################
    #### Overridden event methods ####
    def closeEvent(self):
        self.saveSettings()
        self.window().setWindowTitle('closed tab')

    ## allow color scheme of class to be changed by CSS stylesheets
    def paintEvent(self, pe):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        p = QtGui.QPainter(self)
        s = self.style()
        s.drawPrimitive(QtGui.QStyle.PE_Widget, opt, p, self)

