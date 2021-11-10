from PyQt5 import QtWidgets, QtGui, uic, QtCore
import os 



class TagDialogueGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'saveTagsDialog.ui'),self)
        self.show()
        self.Add_Fields.clicked.connect(self.addField)

    def addField(self):
        newLabel = QtWidgets.QLineEdit()
        newData = QtWidgets.QLineEdit()
        newLabel.setPlaceholderText("Tag Name")
        newData.setPlaceholderText("Tag Data")
        self.CustomFields.addRow(newLabel, newData)





app = QtWidgets.QApplication([])
window = TagDialogueGUI()
app.exec_()