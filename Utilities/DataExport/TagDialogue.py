from PyQt5 import QtWidgets, uic
from Utilities.GoogleDriveHandler import gdrive_constants
from Utilities.Popups.generic_popup import GenericPopup
from datetime import datetime, timedelta
import json
import os
import re


# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'saveTagsDialog.ui'))


class TagDialogueGUI(QtWidgets.QDialog, uiFile):
    def __init__(self, collection_start_time: datetime,
                 collection_stop_time: datetime, default_scene_name: str,
                 sensorsList: list):
        super().__init__()
        # uic.loadUi(os.path.join(os.path.dirname(__file__),
        #                         'saveTagsDialog.ui'), self)
        self.setupUi(self)

        self.collection_start_time = collection_start_time
        self.collection_stop_time = collection_stop_time
        self.default_scene_name = default_scene_name
        self.default_sensorsList = sensorsList

        self.fieldRow = 1
        self.custom_props = []
        self.dec_row_buttons = []
        self.pushTags = dict()
        self.new_filename = None
        self.saved_json_dump = False

        self.__connectSlotsSignals()
        self.setup()
        self.exec()

    def __connectSlotsSignals(self):
        self.Add_Fields.clicked.connect(self.__addField)
        self.RefreshButton.clicked.connect(self.default)
        self.DoneButton.clicked.connect(self.__save_changes)

    def __validate_inputs(self) -> tuple:
        # validating filename using regex by src
        # https://stackoverflow.com/a/11794507/11031425
        filename_regex = gdrive_constants.FILENAME_REGEX
        if len(re.findall(filename_regex, self.Name.text())) != 1:
            GenericPopup("Wrong Filename Format",
                         "Only use A-Z, 0-9, ., SPACE, and _")
            return tuple()

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
            new_start_time = datetime.strptime(
                f"{self.Date.text()} {self.Time.text()}", "%m/%d/%Y %H:%M:%S")
        except ValueError:
            GenericPopup("Wrong Date or Time Format",
                         "Date should look like 12/27/2021 and Time should "
                         "look like 23:59:59.99")
            return tuple()

        return new_start_time, new_length

    def __save_changes(self):
        validated_inputs = self.__validate_inputs()
        if not validated_inputs:
            raise ValueError("Input validation on file upload failed")

        new_start_time, new_length = validated_inputs
        custom_props = {
            "__Filename": self.Name.text(),
            "__Sensors": [s.strip() for s in self.SensorList.text().split(",")],
            "test_length": str(new_length),
            "collection_start_time": str(new_start_time),
            "collection_stop_time": str(new_start_time + new_length),
            "notes": self.Notes.toPlainText()[:119]
        }

        for tagData in self.custom_props:
            if tagData[0].text() and tagData[1].text():
                # Google Drive's max char limit for each custom properties = 124
                value_limit = 124 - len(tagData[0].text())
                value_trimmed = tagData[1].text()[:value_limit]
                custom_props[tagData[0].text()] = value_trimmed
        self.pushTags = custom_props

        # TODO FARIS validate this function
        self.__dump_custom_properties(custom_props)
        self.saved_json_dump = True

        self.close_popup()

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
        newLabel.setPlaceholderText("Tag Name")
        newData.setPlaceholderText("Tag Data")
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

    def get_filename(self) -> str:
        return self.new_filename

    def closeEvent(self, event):
        """
        Overrides the default close action on clicking the 'X' close button.
        src: https://stackoverflow.com/a/12366684/11031425.
        """
        if not self.saved_json_dump:
            self.default()
            self.__save_changes()
        event.accept()

    def setup(self):
        self.default()

    def default(self):
        formatted_start_time = \
            self.collection_start_time.strftime(gdrive_constants.TIME_FORMAT)
        default_GDFilename = f"{formatted_start_time} {self.default_scene_name}"
        self.Name.setText(default_GDFilename)
        self.Date.setText(self.collection_start_time.strftime("%m/%d/%Y"))

        default_length = (self.collection_stop_time
                          - self.collection_start_time).total_seconds()
        hour = int(default_length // 3600)
        minute = int(default_length // 60 % 60)
        second = float(default_length % 60)
        self.Length.setText(f"{hour}:{minute}:{second}")

        self.Time.setText(self.collection_start_time.strftime("%H:%M:%S"))
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

        :param filename: the name of the file to be uploaded, e.g. test1.csv
        :param sensorsList: list of all connected, non-derived sensors
        :return: None
        """
        # Limits: https://developers.google.com/drive/api/v3/properties
        PROPERTIES_LIMIT = 30  # public
        APP_PROPERTIES_LIMIT = 30  # private outside this application

        # True if some properties are removed; max is 60 keys
        custom_properties["some_properties_removed"] = "False"
        custom_properties["scene"] = self.default_scene_name

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

        # Verifies each property is max 124 char. Disabled for performance.
        # __verify_custom_prop_len(custom_properties)
        self.new_filename = custom_properties["__Filename"]

        del custom_properties["__Sensors"]
        del custom_properties["__Filename"]

        with open(gdrive_constants.DEFAULT_UPLOAD_DIRECTORY
                  + self.new_filename + ".json", "w") \
                as outfile:
            json.dump(custom_properties, outfile)

    def close_popup(self):
        self.close()


# app = QtWidgets.QApplication([])
# window = TagDialogueGUI()
# app.exec_()
# tags = window.pushTags
