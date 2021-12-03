from DataAcquisition import data
from PyQt5 import QtWidgets, uic, QtCore
from Utilities.GoogleDriveHandler import GoogleDriveHandler, DriveSearchQuery
import Utilities.Popups.generic_popup as generic_popup
import logging
import os

logger = logging.getLogger("ImportGoogleDrive")
# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'import_google_drive_popup.ui'))


class DataImport(QtWidgets.QDialog, uiFile):
    DURATION_OPTIONS = GoogleDriveHandler.DURATION_OPTIONS
    TEST_DATE_OPTIONS = GoogleDriveHandler.TEST_DATE_PERIOD_OPTIONS

    def __init__(self, scenes):
        super().__init__()
        self.setupUi(self)
        self.scenes = scenes
        self.checkbox_sensors = dict()
        self.custom_properties = dict()
        self.configFile = QtCore.QSettings('DAATA', 'DataImport')

        self.__populate_fields()
        self.adv_options_widget.hide()
        self.__connectSlotsSignals()
        self.exec()

    def __populate_fields(self):
        self.sec_file.setPlainText(self.configFile.value("sec_file"))

        self.scene_input.addItem("All")
        for scene in self.scenes:
            self.scene_input.addItem(scene)
        sensorsList = data.get_sensors(is_derived=False)
        for sensor in sensorsList:
            self.checkbox_sensors[sensor] = \
                QtWidgets.QCheckBox(sensor, self.widget_2, objectName=sensor)
            self.checkbox_sensors[sensor].setToolTip(sensor)
            self.gridLayout.addWidget(self.checkbox_sensors[sensor])
            self.checkbox_sensors[sensor].show()

        for duration in self.DURATION_OPTIONS:
            self.duration_input.addItem(duration)

        for upload_date in self.TEST_DATE_OPTIONS:
            self.upload_date_input.addItem(upload_date)

    def __connectSlotsSignals(self):
        self.see_results_btn.clicked.connect(self.__display_data)
        self.close_btn.clicked.connect(self.close_popup)
        self.adv_options_button.clicked.connect(self.__hide_show_adv_options)
        self.add_field_button.clicked.connect(self.__addCustomPropsField)

    def __hide_show_adv_options(self):
        if self.adv_options_widget.isVisible():
            self.adv_options_widget.hide()
        else:
            self.adv_options_widget.show()

    def __display_data(self):
        sec_file = self.sec_file.toPlainText()
        self.configFile.setValue("sec_file", sec_file)

        # generate search queries
        file_name_query = self.file_name_input.toPlainText()
        file_name_query = file_name_query if file_name_query is not "" else None

        year_query = self.year_input.toPlainText() \
            if self.year_input.toPlainText() != "" else None
        month_query = self.month_input.toPlainText() \
            if self.month_input.toPlainText() != "" else None
        day_query = self.day_input.toPlainText() \
            if self.day_input.toPlainText() != "" else None

        if (year_query is None or year_query.isdigit()) \
                and (month_query is None or month_query.isdigit()) \
                and (day_query is None or day_query.isdigit()):
            # integer input validation passed
            pass
        else:
            generic_popup.GenericPopup("Type Error",
                                       "Date inputs should be integers")
            return
        custom_prop_query = dict()
        scene_query = str(self.scene_input.currentText())
        for custom_prop_key in self.custom_properties.keys():
            custom_prop_query[custom_prop_key.toPlainText()] = \
                self.custom_properties[custom_prop_key].toPlainText()
        custom_prop_query.pop("", None)

        if scene_query != "All":
            custom_prop_query["scene"] = scene_query

        # derived search queries
        test_date_query = str(self.upload_date_input.currentText())
        duration_query = str(self.duration_input.currentText())

        search_q = DriveSearchQuery(
            filename=file_name_query,
            exclude_folders=True,
            year=year_query,
            month=month_query,
            day=day_query,
            custom_properties=custom_prop_query,
            test_date_period=test_date_query,
            duration=duration_query)

        try:
            DRIVE_SERVICE = GoogleDriveHandler(sec_file)
        except ValueError:
            logger.error("Error in creating Google Drive Handler")
            return

        found_files = DRIVE_SERVICE.find_file_in_drive(search_q)

        # TODO DELETE
        print(len(found_files))
        print(found_files)

        found_files_buttons = dict()

        # for i, found_file in enumerate(found_files):
        #     found_file_button = QtWidgets.QPushButton(found_file.get("name"))
        #     found_files_buttons[found_file.get("id")] = found_file_button
        #     self.gridLayout_2.addWidget(found_file_button, i, 0)

    def __addCustomPropsField(self):
        key = QtWidgets.QPlainTextEdit()
        value = QtWidgets.QPlainTextEdit()
        self.custom_properties[key] = value
        self.adv_options_layout.addRow(key, value)

    def close_popup(self):
        self.close()

# if __name__ == "__main__":
#     app = QtWidgets.QApplication([])
#     window = DataImport(["DataAcqu"])
#     app.exec_()
