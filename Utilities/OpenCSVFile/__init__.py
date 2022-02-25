from PyQt5 import QtWidgets, uic
from Utilities import general_constants
from Utilities.DataExport.dataFileExplorer import open_data_file
from Utilities.Popups.generic_popup import GenericPopup
import os

# loads the .ui file from QT Designer
uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                        'open_csv_file.ui'))


class OpenCSVFile(QtWidgets.QDialog, uiFile):
    def __init__(self, all_scenes):
        super().__init__()
        self.setupUi(self)
        self.__all_scenes = all_scenes
        self.__selected_filepath: str = ""
        self.__selected_scene: str = ""
        self.__setup()
        self.exec()

    def __setup(self):
        self.__populate_scenes()
        self.__connectSlotsSignals()

    def __populate_scenes(self):
        self.scene_selection.addItems([""])
        self.scene_selection.addItems(
            [s for s in self.__all_scenes if
             not self.__all_scenes[s].is_preview_scene])

    def __connectSlotsSignals(self):
        self.display_button.clicked.connect(self.__close_and_display)
        self.cancel_button.clicked.connect(self.close)
        self.find_file_btn.clicked.connect(self.__find_csv_file)

    def __find_csv_file(self):
        self.__selected_filepath = open_data_file(".csv")
        self.filepath.setPlainText(self.__selected_filepath)
        # automatically picks the scene based on file name, if possible
        for scene, scene_info in self.__all_scenes.items():
            if scene_info.formal_name in self.__selected_filepath:
                self.scene_selection.setCurrentText(scene)

    def __close_and_display(self) -> bool:
        scene_selection = self.scene_selection.currentText()
        if not scene_selection:
            GenericPopup("Please select a scene")
            return False
        elif not self.filepath.toPlainText():
            GenericPopup("Please select a file")
            return False
        formal_selected_scene_name = \
            self.__all_scenes[scene_selection].formal_name

        if formal_selected_scene_name \
                not in general_constants.DISPLAYABLE_IMPORTED_SCENES:
            GenericPopup("Scene not supported")
            return False

        self.__selected_filepath = self.filepath.toPlainText()
        self.__selected_scene = formal_selected_scene_name
        self.close()
        return True

    @property
    def selected_filepath_scene(self) -> tuple:
        return self.__selected_filepath, self.__selected_scene

# from PyQt5.QtWidgets import QApplication
# import sys
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     G = GenericPopup("blob", "blob2")
#     sys.exit(app.exec_())
