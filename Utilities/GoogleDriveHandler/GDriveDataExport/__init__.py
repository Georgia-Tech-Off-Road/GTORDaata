from PyQt5 import QtWidgets, QtCore, uic
from Utilities.DataExport.dataFileExplorer import open_data_file
from Utilities.DataExport.exportCSV import saveCSV
from Utilities.DataExport.exportMAT import saveMAT
from Utilities.GoogleDriveHandler import gdrive_constants, GoogleDriveHandler
from Utilities.GoogleDriveHandler.GDriveDataExport.missing_oAuth import MissingOAuthFile
from Utilities.Popups.generic_popup import GenericPopup
from datetime import datetime, timedelta, date as dt_date, time as dt_time
import json
import logging
import os
import re
import shutil

# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'saveUploadTagsDialog.ui'))
logger = logging.getLogger("GDriveDataExport")


class CreateUploadJSON(QtWidgets.QDialog, uiFile):
    def __init__(self, collection_start_time: datetime = None,
                 def_test_duration: timedelta = None,
                 default_scene_name: str = "",
                 sensorsList: list = None):
        super().__init__()
        # uic.loadUi(os.path.join(os.path.dirname(__file__),
        #                         'saveUploadTagsDialog.ui'), self)
        self.setupUi(self)
        self.configFile = QtCore.QSettings('DAATA', 'CreateUploadJSON')

        if not (collection_start_time and def_test_duration and
                default_scene_name and sensorsList):
            self.MANUAL_UPLOAD = True
        else:
            self.MANUAL_UPLOAD = False

        self.collection_start_time = collection_start_time \
            if collection_start_time else datetime.min
        self.def_test_duration = def_test_duration \
            if def_test_duration else timedelta(seconds=0)
        self.default_scene_name = default_scene_name
        self.default_sensorsList = sensorsList if sensorsList else []

        self.HUMAN_DATE_FORMAT = "%m/%d/%Y"
        self.HUMAN_TIME_FORMAT = "%H:%M:%S.%f"

        self.fieldRow = 1
        self.custom_props = []
        self.dec_row_buttons = []
        self.__new_filename_without_extension: str = ""
        self.__complete_save_and_exit = False
        self.__save_local_only = False

        self.__connectSlotsSignals()
        self.__setup()
        self.exec()

    def __connectSlotsSignals(self):
        def show_hide_tags():
            if self.Tags.isVisible():
                self.Tags.hide()
            else:
                self.Tags.show()

        def show_hide_oAuthFileEntry_info():
            if self.save_offline_only_option.isChecked():
                self.__save_local_only = True
                self.oAuthFileEntry_info.hide()
                self.oAuth_label.hide()
            else:
                self.__save_local_only = False
                self.oAuthFileEntry_info.show()
                self.oAuth_label.show()

        self.Add_Fields.clicked.connect(self.__addField)
        self.DefaultButton.clicked.connect(self.__default)
        self.DoneButton.clicked.connect(self.__save_changes)
        self.showTags.clicked.connect(show_hide_tags)
        self.save_offline_only_option.stateChanged.connect(
            show_hide_oAuthFileEntry_info)
        self.openSecGDInfoBtn.clicked.connect(GoogleDriveHandler.openSecGDInfo)
        self.select_upload_file.clicked.connect(self.__find_uploading_file)
        self.select_sec_file.clicked.connect(self.__find_sec_file)

    def __find_uploading_file(self):
        uploading_file_selected = open_data_file(".csv .mat")
        if uploading_file_selected:
            self.file_location.setText(uploading_file_selected)

    def __find_sec_file(self):
        sec_file_selected = open_data_file(".json")
        if sec_file_selected:
            self.oAuth_entry.setText(sec_file_selected)

    def __validate_inputs(self) -> tuple:
        def valid_windows_filename(filename: str) -> bool:
            filename_regex = gdrive_constants.FILENAME_REGEX
            if len(re.findall(filename_regex, filename)) != 1:
                # validating filename using regex by src
                # https://stackoverflow.com/a/11794507/11031425
                GenericPopup("Wrong Filename Format",
                             "Only use A-Z, 0-9, ., SPACE, and _")
                return False
            else:
                return True

        if self.MANUAL_UPLOAD:
            abnormal_file_location = self.file_location.text()
            if not (abnormal_file_location and
                    os.path.isfile(abnormal_file_location)):
                GenericPopup(f"File {abnormal_file_location} does not "
                             f"exist")
                return tuple()
            elif not (abnormal_file_location[-3:] == "csv" or
                      abnormal_file_location[-3:] == "mat"):
                GenericPopup(f"File not of type csv or mat")
                return tuple()
            new_extensionless_filename = \
                os.path.basename(abnormal_file_location)[:-4]
            if not valid_windows_filename(self.Name.text()):
                return tuple()
        else:
            if not valid_windows_filename(self.Name.text()):
                return tuple()
            new_extensionless_filename = self.Name.text()

        # validating test length
        new_length = self.Length.text().split(":")
        try:
            if len(new_length) != 3:
                raise ValueError("Wrong Length Format")
            hour = int(new_length[0])
            minute = int(new_length[1])
            second = float(new_length[2])
        except ValueError:
            GenericPopup("Wrong Length Format",
                         "Length should look like 23:59:59.99")
            return tuple()
        total_seconds = hour * 3600 + minute * 60 + second
        new_length = timedelta(seconds=total_seconds)

        # validating test start time
        try:
            # add microseconds if not included
            if "." not in self.Time.text():
                self.Time.setText(f"{self.Time.text()}.00")
            input_date: dt_date = datetime.strptime(
                self.Date.text(), self.HUMAN_DATE_FORMAT).date()
            input_time: dt_time = datetime.strptime(
                self.Time.text(), self.HUMAN_TIME_FORMAT).time()
            new_start_time: datetime = datetime.combine(input_date, input_time)
        except ValueError:
            GenericPopup("Wrong Date or Time Format",
                         "Date should look like 12/27/2021 and Time should "
                         "look like 23:59:59.99")
            return tuple()

        self.__new_filename_without_extension = new_extensionless_filename
        return new_start_time, new_length

    def __save_changes(self) -> bool:
        self.progress_widget.show()

        validated_inputs = self.__validate_inputs()
        if not validated_inputs:
            logger.debug("Input validation on file upload failed")
            self.progress_widget.hide()
            return False

        new_start_time, new_length = validated_inputs
        new_stop_time = new_start_time + new_length

        custom_props = {
            "__Sensors": [s.strip() for s in self.SensorList.text().split(",")],
            "test_length": str(new_length),
            "collection_start_time": self.__datetime_to_utc_str(new_start_time),
            "collection_stop_time": self.__datetime_to_utc_str(new_stop_time),
            "notes": self.Notes.toPlainText()[:119]
        }

        for tagData in self.custom_props:
            if tagData[0].text() and tagData[1].text():
                # Google Drive's max char limit for each custom properties = 124
                value_limit = 124 - len(tagData[0].text())
                value_trimmed = tagData[1].text()[:value_limit]
                custom_props[tagData[0].text()] = value_trimmed

        self.__oAuth_file_input: str = self.oAuth_entry.text()

        if self.__save_local_only:
            filepaths = self.__save_locally(custom_props)
            if filepaths:
                GenericPopup("Local copy saved", f"{filepaths}")
            self.close()
            return True
        else:
            if self.__oAuth_file_input and os.path.isfile(
                    self.__oAuth_file_input):
                if not self.__save_locally(custom_props):
                    self.progress_widget.hide()
                    return False
                self.__complete_save_and_exit = True
                if self.__commence_upload():
                    self.configFile.setValue("sec_file",
                                             self.__oAuth_file_input)
                    self.close()
                    return True
            else:
                self.__save_local_only = \
                    MissingOAuthFile().save_offline_selected
                if self.__save_local_only:
                    self.__save_locally(custom_props)
                    self.close()
                    return True
        # don't close if something fails
        self.progress_widget.hide()
        return False

    def __save_locally(self, custom_props: dict) -> str:
        if self.MANUAL_UPLOAD:
            shutil.copy2(self.file_location.text(),
                         gdrive_constants.DEFAULT_UPLOAD_DIRECTORY)
            extension = self.file_location.text()[-3:]
            filepaths = f"{gdrive_constants.DEFAULT_UPLOAD_DIRECTORY}" \
                        f"{self.__new_filename_without_extension}.{extension}"
        else:
            saveCSV(self.__new_filename_without_extension,
                    gdrive_constants.DEFAULT_UPLOAD_DIRECTORY)
            saveMAT(self.__new_filename_without_extension,
                    gdrive_constants.DEFAULT_UPLOAD_DIRECTORY)
            filepaths = f"{gdrive_constants.DEFAULT_UPLOAD_DIRECTORY}" \
                        f"{self.__new_filename_without_extension}.csv" \
                        f"\n&\n" \
                        f"{gdrive_constants.DEFAULT_UPLOAD_DIRECTORY}" \
                        f"{self.__new_filename_without_extension}.mat"
        self.__dump_custom_properties(custom_props)
        self.__complete_save_and_exit = True
        return filepaths

    def __commence_upload(self) -> bool:
        if self.__complete_save_and_exit:
            try:
                drive_handler = GoogleDriveHandler(self.oAuth_file_input)
            except GoogleDriveHandler.NoInternetError:
                GenericPopup("No Internet",
                             "All files have been saved offline and will be "
                             "uploaded at the next upload instance")
                return True
            # except GoogleDriveHandler.NoAccessError:
            #     self.__clear_found_files()
            #     GenericPopup("No Access to the shared GTOR Google Drive",
            #                  "All files have been saved offline and will be "
            #                  "uploaded at the next upload instance")
            #     return False
            except Exception as e:
                GenericPopup("Upload Failed", str(e))
                return False
            if drive_handler.upload_all_to_drive(self.uploadProgressBar):
                GenericPopup("All files uploaded", drive_handler.warning_msg)
                self.close()
                return True
        return False

    def __addField(self):
        newLabel = QtWidgets.QLineEdit()
        newData = QtWidgets.QLineEdit()
        newButton = QtWidgets.QPushButton('X')
        newButton.setStyleSheet('QPushButton{ Color: red; font-weight: bold }')
        newButton.setMaximumSize(28, 28)
        self.dec_row_buttons.append(newButton)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(newData)
        hbox.addWidget(newButton)
        newLabel.setPlaceholderText("Tag Key")
        newData.setPlaceholderText("Tag Value (Key + Value max 124 char)")
        self.CustomFields.insertRow(self.fieldRow, newLabel, hbox)
        pair = newLabel, newData
        self.custom_props.append(pair)
        self.fieldRow = self.fieldRow + 1
        newButton.clicked.connect(
            lambda: self.custom_props.remove((newLabel, newData)))
        newButton.clicked.connect(lambda: self.__decRow(newButton))
        newButton.clicked.connect(lambda: self.CustomFields.removeRow(newLabel))

    def __decRow(self, newButton: QtWidgets.QPushButton):
        self.fieldRow = self.fieldRow - 1
        self.dec_row_buttons.remove(newButton)

    def closeEvent(self, event):
        """
        Overrides the default close action on clicking the 'X' close button.
        src: https://stackoverflow.com/a/12366684/11031425.
        """
        event.accept()

    def __setup(self):
        GoogleDriveHandler.initialize_download_upload_directories()

        self.oAuth_entry.setText(self.configFile.value("sec_file"))
        self.scene_input.setText(self.default_scene_name)
        self.progress_widget.hide()

        self.Tags.hide()
        if self.MANUAL_UPLOAD:
            # if after data collection, not through manual upload
            self.Name.hide()
            self.label_UploadName.hide()
        else:
            # meaning no file metadata was given, implying manual upload instead
            # of straight uploading from GUI after data collection
            self.file_widget.hide()
            self.filepath_label.hide()

        self.__default()

    def __default(self):
        formatted_start_time = \
            self.collection_start_time.strftime(
                gdrive_constants.FILENAME_TIME_FORMAT)
        default_GDFilename = f"{formatted_start_time} {self.default_scene_name}"
        self.Name.setText(default_GDFilename)
        self.Date.setText(self.collection_start_time.strftime(
            self.HUMAN_DATE_FORMAT))

        def_test_dur_sec = self.def_test_duration.total_seconds()
        hour = int(def_test_dur_sec % 86400 // 3600)
        minute = int(def_test_dur_sec % 3600 % 60)
        second = float(def_test_dur_sec % 60)
        self.Length.setText(f"{hour}:{minute}:{second}")

        self.Time.setText(self.collection_start_time.strftime(
            self.HUMAN_TIME_FORMAT))
        self.Notes.setText("")

        self.SensorList.setText(str(", ".join(self.default_sensorsList)))

        for x_button in self.dec_row_buttons.copy():
            x_button.click()
        self.dec_row_buttons.clear()

    def __dump_custom_properties(self, custom_properties: dict):
        """
        Creates a JSON file with all the custom properties of the file (in
        dict format) to be uploaded as custom Google Drive file
        properties or appProperties. This includes the mandatory custom
        properties, e.g., collection_start_time and the sensors in the format
        {"sensor-test_sensor_1": True, "sensor-test_sensor_3"}.

        :param custom_properties: custom properties to be saved in the JSON
        :return: None
        """
        # Limits: https://developers.google.com/drive/api/v3/properties
        PROPERTIES_LIMIT = 30  # public
        APP_PROPERTIES_LIMIT = 30  # private outside this application

        # True if some properties are removed; max is 60 keys
        custom_properties["some_properties_removed"] = "False"
        custom_properties["scene"] = self.scene_input.text()

        # adds all the sensors to the custom_properties dict up to 60 total
        # custom_properties
        sensorsList = custom_properties["__Sensors"]
        sensorsList_limit = len(sensorsList)
        TOTAL_LIMIT = PROPERTIES_LIMIT + APP_PROPERTIES_LIMIT  # 60
        if len(sensorsList) + len(custom_properties) > TOTAL_LIMIT:  # 60
            sensorsList_limit = TOTAL_LIMIT - len(custom_properties)
            custom_properties["some_properties_removed"] = "True"
        for sensor_i in range(sensorsList_limit):
            custom_properties["sensor-" + sensorsList[sensor_i]] = "True"

        del custom_properties["__Sensors"]

        with open(f"{gdrive_constants.DEFAULT_UPLOAD_DIRECTORY}"
                  f"{self.__new_filename_without_extension}.json", "w") \
                as outfile:
            json.dump(custom_properties, outfile)

    @staticmethod
    def __datetime_to_utc_str(dt: datetime) -> str:
        """
        Converts the input local datetime object into UTC time and formats it
        into the ISO datetime format, returning as a string.

        :param dt: input datetime to be converted
        :return: the input datetime in UTC time in ISO string format
        """
        dt_utc = GoogleDriveHandler.local_to_utc(dt)
        return dt_utc.strftime(gdrive_constants.ISO_TIME_FORMAT)

    @property
    def complete_save_and_exit(self):
        # normal and expected close, file should be uploaded later
        return self.__complete_save_and_exit

    @property
    def oAuth_file_input(self):
        return self.__oAuth_file_input

    @property
    def save_local_only(self):
        return self.__save_local_only

# app = QtWidgets.QApplication([])
# window = TagDialogueGUI()
# app.exec_()
# tags = window.pushTags
