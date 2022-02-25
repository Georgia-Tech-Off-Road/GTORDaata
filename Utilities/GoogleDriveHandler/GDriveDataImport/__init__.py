from DataAcquisition import data
from PyQt5 import QtWidgets, uic, QtCore
from Utilities import general_constants
from Utilities.GoogleDriveHandler import GoogleDriveHandler, DriveSearchQuery
from Utilities.GoogleDriveHandler.GDriveDataImport import add_qDialogs
from Utilities.Popups.generic_popup import GenericPopup
from functools import partial
import logging
import os
from typing import Tuple

logger = logging.getLogger("ImportGoogleDrive")
# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'import_google_drive_popup.ui'))


class GDriveDataImport(QtWidgets.QDialog, uiFile):
    DURATION_OPTIONS = general_constants.DURATION_OPTIONS
    TEST_DATE_OPTIONS = general_constants.TEST_DATE_PERIOD_OPTIONS
    DISPLAYABLE_SCENES = general_constants.DISPLAYABLE_IMPORTED_SCENES

    def __init__(self, dict_scenes: dict):
        super().__init__()
        self.setupUi(self)
        self.dict_scenes_copy = dict_scenes
        self.checkbox_sensors = dict()
        self.custom_properties = dict()
        self.__selected_filepath: str = ""
        self.__file_metadata: dict = dict()
        self.configFile = QtCore.QSettings('DAATA', 'GDriveDataImport')

        self.__setup()
        self.exec()

    def __setup(self):
        GoogleDriveHandler.initialize_download_upload_directories()
        self.progressBar.hide()
        self.__populate_fields()
        self.adv_options_widget.hide()
        self.__connectSlotsSignals()

    def __populate_fields(self):
        self.scene_input.addItem("All")
        for scene in self.dict_scenes_copy.keys():
            scene_hidden = self.dict_scenes_copy[scene].get("disabled")
            if not scene_hidden:
                self.scene_input.addItem(scene)

        self.sensorsList = data.get_sensors(is_derived=False)
        self.checkbox_sensors = dict()
        for sensor in self.sensorsList:
            sensor_id_name = f"{data.get_id(sensor)}: " \
                             f"{data.get_display_name(sensor)}"
            self.checkbox_sensors[sensor] = \
                QtWidgets.QCheckBox(sensor_id_name,
                                    self.scrollAreaWidgetContents_2,
                                    objectName=sensor)
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
        self.clearButton.clicked.connect(self.__clear_all)

    def __hide_show_adv_options(self):
        if self.adv_options_widget.isVisible():
            self.adv_options_widget.hide()
        else:
            self.adv_options_widget.show()

    def __clear_all(self):
        self.upload_date_input.setCurrentIndex(0)
        self.scene_input.setCurrentIndex(0)
        for sensor in self.checkbox_sensors:
            self.checkbox_sensors[sensor].setChecked(False)

        self.file_name_input.setPlainText("")
        self.year_input.setPlainText("")
        self.month_input.setPlainText("")
        self.day_input.setPlainText("")
        self.progressBar.setValue(0)
        self.progressBar.hide()

        self.duration_input.setCurrentIndex(0)
        self.__remove_all_custom_props()
        self.__clear_found_files()
        self.search_older_dates.setChecked(False)

    def __display_data(self):
        self.gridLayout_2.addWidget(QtWidgets.QLabel("Loading..."))
        sec_file = general_constants.GDRIVE_OAUTH2_SECRET

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
            GenericPopup("Type Error", "Date inputs should be integers")
            self.__clear_found_files()
            return

        custom_prop_query = dict()

        for custom_prop_key in self.custom_properties.keys():
            custom_prop_query[custom_prop_key.toPlainText()] = \
                self.custom_properties[custom_prop_key].toPlainText()
        custom_prop_query.pop("", None)

        for sensor in self.sensorsList:
            if self.checkbox_sensors[sensor].isChecked():
                custom_prop_query[f"sensor-{sensor}"] = "True"

        scene_query = str(self.scene_input.currentText())
        if scene_query != "All":
            try:
                custom_prop_query["scene"] = \
                    self.dict_scenes_copy[scene_query]["formal_name"]
            except KeyError:
                custom_prop_query["scene"] = scene_query

        # derived search queries
        test_date_query = str(self.upload_date_input.currentText())
        duration_query = str(self.duration_input.currentText())

        if self.search_older_dates.isChecked():
            page_limit = 100
        else:
            page_limit = 1

        search_q = DriveSearchQuery(
            page_limit=page_limit,
            filename=file_name_query,
            only_csv_mat=True,
            year=year_query,
            month=month_query,
            day=day_query,
            custom_properties=custom_prop_query,
            test_date_period=test_date_query,
            duration=duration_query)

        try:
            drive_handler = GoogleDriveHandler(sec_file)
        except GoogleDriveHandler.MissingOAuthFileError:
            self.__clear_found_files()
            GenericPopup("Missing oAuth file",
                         f"oAuth file not detected in {sec_file}. <br /> "
                         f"<a href='https://drive.google.com/file/d/117yhiyV2BAZNxityj4la6J50FECaEPJB/view?usp=sharing'>"
                         f"Download here</a>.")
            return
        except GoogleDriveHandler.NoInternetError:
            self.__clear_found_files()
            GenericPopup("No Internet")
            return
        # except GoogleDriveHandler.NoAccessError:
        #     self.__clear_found_files()
        #     GenericPopup("No Access", "You need to request access to the GTOR "
        #                               "shared Google Drive")
        #     return
        except ValueError:
            self.__clear_found_files()
            logger.error("Error in creating Google Drive Handler")
            return

        found_files = drive_handler.find_file_in_drive(search_q)

        self.__clear_found_files()

        if len(found_files) == 0:
            self.gridLayout_2.addWidget(QtWidgets.QLabel("No files found"))
            return

        # adds the buttons to the layout in grid format
        for i, found_file in enumerate(found_files):
            found_file_button = QtWidgets.QPushButton(found_file.get("name"))
            found_file_button.clicked.connect(
                partial(self.__download_and_display, drive_handler, found_file))
            self.gridLayout_2.addWidget(found_file_button, i, 0)

            found_file_metadata_btn = QtWidgets.QPushButton("ⓘ")
            found_file_metadata_btn.setMaximumWidth(50)
            found_file_metadata_btn.clicked.connect(
                partial(add_qDialogs.FileMetadata,
                        found_file.get("name"), str(found_file)))
            self.gridLayout_2.addWidget(found_file_metadata_btn, i, 1)

    def __download_and_display(self, drive_handler: GoogleDriveHandler,
                               file_metadata: dict):
        self.__selected_filepath = ""
        self.__file_metadata = dict()
        self.progressBar.show()

        if file_metadata.get("name")[-4:] != ".csv":
            reason = "The selected file cannot be displayed (not a .csv). " \
                     "Proceed to download anyways?"
            self.__download_unsupported_file(drive_handler, file_metadata,
                                             reason, self.progressBar)
            self.progressBar.hide()
            return

        try:
            file_scene = file_metadata.get("properties").get("scene")
        except AttributeError:
            reason = "The selected file cannot be displayed (unknown scene). " \
                     "Proceed to download anyways?"
            self.__download_unsupported_file(drive_handler, file_metadata,
                                             reason,
                                             self.progressBar)
            self.progressBar.hide()
            return

        if file_scene not in self.DISPLAYABLE_SCENES:
            reason = "The selected file cannot be displayed (scene not " \
                     "supported). Proceed to download anyways?"
            self.__download_unsupported_file(drive_handler, file_metadata,
                                             reason, self.progressBar)
            self.progressBar.hide()
        else:
            self.__file_metadata = file_metadata
            # self.__selected_filepath used in MainWindow to plot the file data
            self.__selected_filepath = \
                drive_handler.download_and_close(file_metadata, self,
                                                 self.progressBar)

    def __clear_found_files(self):
        # clear all previous buttons and widgets from the Results layout
        for i in reversed(range(self.gridLayout_2.count())):
            self.gridLayout_2.itemAt(i).widget().setParent(None)

    def __addCustomPropsField(self):
        key = QtWidgets.QPlainTextEdit()
        key.setPlaceholderText("Tag Key")
        value = QtWidgets.QPlainTextEdit()
        value.setPlaceholderText("Tag Value")
        self.custom_properties[key] = value
        self.adv_options_layout.addRow(key, value)

    def __remove_all_custom_props(self):
        for custom_prop in self.custom_properties:
            self.adv_options_layout.removeRow(custom_prop)
        self.custom_properties.clear()

    def close_popup(self):
        self.close()

    @staticmethod
    def __download_unsupported_file(drive_handler: GoogleDriveHandler,
                                    file_metadata: dict, reason: str,
                                    progressBar=None) -> bool:
        save_offline = \
            add_qDialogs.ConfirmDownloadNonSupported(reason).save_offline
        if save_offline:
            filepath = drive_handler.download(file=file_metadata,
                                              progressBar=progressBar)
            if filepath:
                GenericPopup("File downloaded", filepath)
                return True
        return True

    @property
    def selected_filepath_and_metadata(self) -> Tuple[str, dict]:
        return self.__selected_filepath, self.__file_metadata
