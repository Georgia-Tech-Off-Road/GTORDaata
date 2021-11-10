from PyQt5 import QtWidgets, QtGui, uic, QtCore
import os 



class TestGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'saveTagsDialog.ui'),self)
        self.show()
        self.Add_Fields.clicked.connect(self.addField)

    def addField(self):
        newLabel = QtWidgets.QLineEdit()
        newData = QtWidgets.QLineEdit()
        #newLabel.placeholderText = QtWidgets.QString('Tag Label'
        self.CustomFields.addRow(newLabel, newData)





app = QtWidgets.QApplication([])
window = TestGUI()
app.exec_()