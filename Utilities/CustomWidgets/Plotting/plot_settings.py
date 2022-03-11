from DataAcquisition import data
from PyQt5 import QtCore, QtWidgets, uic
from Utilities.Popups.generic_popup import GenericPopup
from Utilities.general_constants import TIME_OPTION
from dataclasses import dataclass
from functools import partial
from typing import List, Dict
import os

# loads the .ui file from QT Designer
uiSettingsDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                                  'plotSettings.ui'))


class PlotSettingsDialog(QtWidgets.QDialog, uiSettingsDialog):
    def __init__(self, parent, embedLayout, sensor_name,
                 is_read_only: bool = False):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.embedLayout = embedLayout
        self.sensor_name = sensor_name
        self.window().setWindowTitle(
            data.get_display_name(sensor_name) + " Plot Settings")
        self.connectSlotsSignals()
        self.reposition()
        self.__setup(is_read_only)

        self.configFile = QtCore.QSettings('DAATA_plot', self.sensor_name)
        self.loadSettings()
        self.parent.setStyleSheet(self.parent.stylesheetHighlight)
        returnValue = self.exec()

    def __setup(self, is_read_only: bool = False):
        if is_read_only:
            self.lineEdit_graph_width_seconds.hide()
            self.label_secondsDisplayed.hide()

    def loadSettings(self):
        self.lineEdit_graph_width_seconds.setText(
            str(self.parent.seconds_in_view))
        self.lineEdit_yMin.setText(self.configFile.value("yMin"))
        self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def applySettings(self):
        self.saveSettings()
        self.parent.set_yMinMax(self.configFile.value("yMin"),
                                self.configFile.value("yMax"))
        self.parent.set_graphWidth(self.configFile.value("seconds_in_view"))
        self.lineEdit_yMin.setText(self.configFile.value("yMin"))
        self.lineEdit_yMax.setText(self.configFile.value("yMax"))
        self.close()

    def saveSettings(self):
        def is_float_or_auto(string) -> bool:
            try:
                float(string)
                return True
            except ValueError:
                return string == "auto"

        input_width_seconds = self.lineEdit_graph_width_seconds.text()
        input_yMin = self.lineEdit_yMin.text()
        input_yMax = self.lineEdit_yMax.text()

        if not (is_float_or_auto(input_width_seconds) and
                is_float_or_auto(input_yMin) and
                is_float_or_auto(input_yMax)):
            GenericPopup("Value inputs must be floats or 'auto'")
            return

        self.configFile.setValue("seconds_in_view", input_width_seconds)
        self.configFile.setValue("yMin", input_yMin)
        self.configFile.setValue("yMax", input_yMax)

    # direction can be 'up','left','right','down'
    def sendMoveSignal(self, direction):
        self.embedLayout.moveWidget(self.parent, direction)

    def reposition(self, **kwargs):
        xOverride = kwargs.get("xOverride", 0)
        yOverride = kwargs.get("yOverride", 0)

        if xOverride == 0:
            x = self.embedLayout.parent().mapToGlobal(QtCore.QPoint(0,
                                                                    0)).x() + self.embedLayout.parent().width() + 20
            # x = self.parent.mapToGlobal(QtCore.QPoint(0, 0)).x() + self.embedLayout.width()

        else:
            x = xOverride

        if yOverride == 0:
            y = self.embedLayout.parent().mapToGlobal(QtCore.QPoint(0,
                                                                    0)).y() + self.embedLayout.parent().height() / 3
        else:
            y = yOverride

        self.move(x, y)

    def resetYMax(self):
        self.parent.enable_autoRange(True)
        self.lineEdit_yMax.setText("auto")
        self.configFile.setValue("yMax", self.lineEdit_yMax.text())
        self.parent.set_yMinMax(self.configFile.value("yMin"),
                                self.configFile.value("yMax"))

        # self.lineEdit_yMin.setText(self.configFile.value("yMin"))

    def resetYMin(self):
        self.parent.enable_autoRange(True)
        self.lineEdit_yMin.setText("auto")
        self.configFile.setValue("yMin", self.lineEdit_yMin.text())
        self.parent.set_yMinMax(self.configFile.value("yMin"),
                                self.configFile.value("yMax"))

        # self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def connectSlotsSignals(self):
        self.pushButton_apply.clicked.connect(self.applySettings)
        self.button_moveDown.clicked.connect(
            partial(self.sendMoveSignal, 'down'))
        self.button_moveLeft.clicked.connect(
            partial(self.sendMoveSignal, 'left'))
        self.button_moveRight.clicked.connect(
            partial(self.sendMoveSignal, 'right'))
        self.button_moveUp.clicked.connect(partial(self.sendMoveSignal, 'up'))

        self.button_resetYMax.clicked.connect(self.resetYMax)
        self.button_resetYMin.clicked.connect(self.resetYMin)

    def closeEvent(self, e):
        self.parent.setStyleSheet(self.parent.stylesheetDefault)
        del self


# loads the .ui file from QT Designer in case plotting a multi data graph
uiSettingsDialogMDG, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                                     'plotSettingsMultiDataGraph.ui'))


class PlotSettingsDialogMDG(QtWidgets.QDialog, uiSettingsDialogMDG):
    @dataclass(frozen=True)
    class InitMDGSettings:
        x_sensor: str
        y_sensors: List[str]
        is_line_graph: bool

    def __init__(self, parent, embedLayout, x_sensor: str,
                 y_sensors: List[str], is_line_graph: bool, read_only: bool,
                 available_sensors: List[str]):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.embedLayout = embedLayout

        multi_graph_name = parent.objectName()
        self.window().setWindowTitle(multi_graph_name + " Plot Settings")
        self.INIT_MDG_SETTINGS = self.InitMDGSettings(x_sensor, y_sensors[:],
                                                      is_line_graph)
        self.pending_plot_type_is_line = is_line_graph
        self.READ_ONLY = read_only
        self.available_sensors: List[str] = available_sensors

        if self.READ_ONLY:
            if TIME_OPTION in self.available_sensors:
                self.available_sensors.remove(TIME_OPTION)
            self.lineEdit_graph_width_seconds.hide()
            self.label_secondsDisplayed.hide()
        else:
            if self.parent.mdg_is_line_graph:
                self.scatterOrLineBtn.setText("Scatter Plot")
            else:
                self.scatterOrLineBtn.setText("Line Plot")

        # Adds the sensor options for the x- and y-axis.
        # x and y dict() is in form sensor_1:<RadioButton object>.
        # self.checked_x_key  is currently selected x sensor key and
        # self.checked_y_keys are currently selected y sensor keys; updated
        # every time the Apply button is clicked
        self.x_radio_objects: Dict[str, QtWidgets.QRadioButton] = dict()
        self.checked_x_key: str = x_sensor
        self.__addXSensorCheckboxes()

        self.y_checkbox_objects: Dict[str, QtWidgets.QCheckBox] = dict()
        self.checked_y_keys = y_sensors
        self.__addYSensorCheckboxes()

        self.__connectSlotsSignals()
        self.__reposition()

        self.configFile = QtCore.QSettings('DAATA_plot', multi_graph_name)
        self.__loadSettings()
        self.parent.setStyleSheet(self.parent.stylesheetHighlight)

        self.lineEdit_yMin.setText("auto")
        self.lineEdit_yMax.setText("auto")

        returnValue = self.exec()

    def __addXSensorCheckboxes(self):
        """
        Adds all sensor checkboxes for x-axis representing all connected
        sensors; the currently plotted x sensors are selected.
        :return: None
        """
        # adds the time option radio button as one option for x-axis

        self.x_radio_objects[TIME_OPTION] = QtWidgets.QRadioButton(
            TIME_OPTION, self.xSensorContents,
            objectName=TIME_OPTION)
        self.x_radio_objects[TIME_OPTION].setToolTip(
            self.x_radio_objects[TIME_OPTION].objectName())
        self.xGridLayout.addWidget(self.x_radio_objects[TIME_OPTION])

        # creates a radio button for each connected sensors in dictionary in
        # self.xSensorContents; only one sensor can be in the x-axis
        for key in self.available_sensors:
            self.x_radio_objects[key] = QtWidgets.QRadioButton(
                data.get_display_name(key), self.xSensorContents,
                objectName=key)
            self.x_radio_objects[key].setToolTip(
                self.x_radio_objects[key].objectName())
            self.xGridLayout.addWidget(self.x_radio_objects[key])

        self.x_radio_objects[self.checked_x_key].setChecked(True)

    def __addYSensorCheckboxes(self):
        """
        Adds all sensor checkboxes for y-axis representing Time and all
        connected sensors; Time is selected by default.
        :return:
        """
        # creates a checkbox button for each sensor in dictionary in
        # self.ySensorsContents; multiple sensors can be plotted in the y-axis
        # NB: ySensorsContents has 's' after ySensor, but not xSensorContents

        # Create the checkbox for selecting all sensors
        self.select_all_y_checkbox = QtWidgets.QCheckBox(
            "Select All",
            self.ySensorsContents,
            objectName="select_all_y_checkbox")
        self.select_all_y_checkbox.setToolTip(
            self.select_all_y_checkbox.objectName())
        self.yGridLayout.addWidget(self.select_all_y_checkbox)

        for key in self.available_sensors:
            self.y_checkbox_objects[key] = QtWidgets.QCheckBox(
                data.get_display_name(key), self.ySensorsContents,
                objectName=key)
            self.y_checkbox_objects[key].setToolTip(
                self.y_checkbox_objects[key].objectName())
            self.yGridLayout.addWidget(self.y_checkbox_objects[key])

        # checks all the currently plotted y sensors on this graph
        if len(self.checked_y_keys) == len(self.available_sensors):
            # if all connected sensors are checked, set select all checkbox to
            # checked
            self.select_all_y_checkbox.setChecked(True)
        for key in self.checked_y_keys:
            self.y_checkbox_objects[key].setChecked(True)

    def __select_all_btn_change(self):
        if self.select_all_y_checkbox.isChecked():
            for key in self.available_sensors:
                self.y_checkbox_objects[key].setChecked(True)
        else:
            for key in self.available_sensors:
                self.y_checkbox_objects[key].setChecked(False)
        # self.update_xy_sensors()

    def __verify_selected_xy_sensors(self):
        """
        Updates the current stored selection of x and y sensors
        :return: None
        """
        # if TIME_OPTION is selected, then the checked_x_key will be the
        # TIME_OPTION, and we won't check the rest of x sensor options.
        # This is important because TIME_OPTION is not part of connected_sensors
        if self.x_radio_objects[TIME_OPTION].isChecked():
            self.checked_x_key = TIME_OPTION

            # if selected Select All y sensors, all connected sensors will be
            # added to the self.checked_y_keys list
            self.checked_y_keys.clear()
            if self.select_all_y_checkbox.isChecked():
                self.checked_y_keys.extend(self.available_sensors)
            else:
                # adds selected y sensors to the checked_y_keys list, removes
                # unselected sensors
                for key in self.available_sensors:
                    if self.y_checkbox_objects[key].isChecked():
                        self.checked_y_keys.append(key)
        else:
            self.checked_y_keys.clear()
            for key in self.available_sensors:
                # adds selected y sensors to the checked_y_keys list, removes
                # unselected sensors
                if self.y_checkbox_objects[key].isChecked():
                    self.checked_y_keys.append(key)

                # updates the selected x sensor to a variable
                if self.x_radio_objects[key].isChecked():
                    self.checked_x_key = key

    def __loadSettings(self):
        self.lineEdit_graph_width_seconds.setText(str(
            self.configFile.value("seconds_in_view")))
        self.lineEdit_yMin.setText(self.configFile.value("yMin"))
        self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def __applySettings(self):
        self.__saveSettings()
        self.parent.set_yMinMax(self.configFile.value("yMin"),
                                self.configFile.value("yMax"))
        self.parent.set_graphWidth(self.configFile.value("seconds_in_view"))
        self.lineEdit_yMin.setText(self.configFile.value("yMin"))
        self.lineEdit_yMax.setText(self.configFile.value("yMax"))
        self.parent.update_plot_type(self.pending_plot_type_is_line)

        # updates the plot graph based on selections of x and y sensors
        self.__update_this_MDG_settings()

    def __update_this_MDG_settings(self):
        """
        Clears and updates this multi data graph with the newly selected
        x-y sensors and plot type option
        :return:
        """

        def change_detected() -> bool:
            return self.INIT_MDG_SETTINGS.x_sensor != self.checked_x_key or \
                   self.INIT_MDG_SETTINGS.y_sensors != self.checked_y_keys or \
                   self.INIT_MDG_SETTINGS.is_line_graph != self.pending_plot_type_is_line

        self.__verify_selected_xy_sensors()

        if change_detected():
            self.parent.plotWidget.clear()
            self.parent.update_xy_sensors(self.checked_x_key,
                                          self.checked_y_keys)

    def __saveSettings(self):
        def is_float_or_auto(string) -> bool:
            try:
                float(string)
                return True
            except ValueError:
                return string == "auto"

        input_width_seconds = self.lineEdit_graph_width_seconds.text()
        input_yMin = self.lineEdit_yMin.text()
        input_yMax = self.lineEdit_yMax.text()

        if not (is_float_or_auto(input_width_seconds) and
                is_float_or_auto(input_yMin) and
                is_float_or_auto(input_yMax)):
            GenericPopup("Value inputs must be floats or 'auto'")
            return

        self.configFile.setValue("seconds_in_view", input_width_seconds)
        self.configFile.setValue("yMin", input_yMin)
        self.configFile.setValue("yMax", input_yMax)

    def __sendMoveSignal(self, direction):
        # direction can be 'up','left','right','down'
        self.embedLayout.moveWidget(self.parent, direction)

    def __reposition(self, **kwargs):
        xOverride = kwargs.get("xOverride", 0)
        yOverride = kwargs.get("yOverride", 0)

        if xOverride == 0:
            x = self.embedLayout.parent().mapToGlobal(QtCore.QPoint(0,
                                                                    0)).x() + self.embedLayout.parent().width() + 20
            # x = self.parent.mapToGlobal(QtCore.QPoint(0, 0)).x() + self.embedLayout.width()

        else:
            x = xOverride

        if yOverride == 0:
            y = self.embedLayout.parent().mapToGlobal(QtCore.QPoint(0,
                                                                    0)).y() + self.embedLayout.parent().height() / 3
        else:
            y = yOverride

        self.move(x, y)

    def __resetYMax(self):
        self.parent.enable_autoRange(True)
        self.lineEdit_yMax.setText("auto")
        self.configFile.setValue("yMax", self.lineEdit_yMax.text())
        self.parent.set_yMinMax(self.configFile.value("yMin"),
                                self.configFile.value("yMax"))

        # self.lineEdit_yMin.setText(self.configFile.value("yMin"))

    def __resetYMin(self):
        self.parent.enable_autoRange(True)
        self.lineEdit_yMin.setText("auto")
        self.configFile.setValue("yMin", self.lineEdit_yMin.text())
        self.parent.set_yMinMax(self.configFile.value("yMin"),
                                self.configFile.value("yMax"))

        # self.lineEdit_yMax.setText(self.configFile.value("yMax"))

    def __changePlotType(self):
        """
        Changes the plot type from scatter plot to line graph or vice versa and
        updates the MDG
        :return:
        """
        LINE_GRAPH_NAME = "Line Graph"
        SCATTER_GRAPH_NAME = "Scatter Plot"
        if self.scatterOrLineBtn.text() == SCATTER_GRAPH_NAME:
            # change plot type to scatter plot
            self.scatterOrLineBtn.setText(LINE_GRAPH_NAME)
            self.pending_plot_type_is_line = False
        else:
            # change plot type to line graph
            self.scatterOrLineBtn.setText(SCATTER_GRAPH_NAME)
            self.pending_plot_type_is_line = True

    def __connectSlotsSignals(self):
        self.pushButton_apply.clicked.connect(self.__applySettings)
        self.pushButton_ok.clicked.connect(self.__closeSavePlotSettings)
        self.button_moveDown.clicked.connect(
            partial(self.__sendMoveSignal, 'down'))
        self.button_moveLeft.clicked.connect(
            partial(self.__sendMoveSignal, 'left'))
        self.button_moveRight.clicked.connect(
            partial(self.__sendMoveSignal, 'right'))
        self.button_moveUp.clicked.connect(partial(self.__sendMoveSignal, 'up'))
        self.scatterOrLineBtn.clicked.connect(self.__changePlotType)

        self.select_all_y_checkbox.clicked.connect(self.__select_all_btn_change)

        self.button_resetYMax.clicked.connect(self.__resetYMax)
        self.button_resetYMin.clicked.connect(self.__resetYMin)

    def closeEvent(self, e):
        self.parent.setStyleSheet(self.parent.stylesheetDefault)
        del self

    def __closeSavePlotSettings(self):
        self.__applySettings()
        self.close()
