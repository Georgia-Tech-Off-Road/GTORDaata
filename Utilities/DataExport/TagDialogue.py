from PyQt5 import QtWidgets, QtGui, uic, QtCore
import os 
from datetime import datetime

from DataAcquisition import data


class TagDialogueGUI(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'saveTagsDialog.ui'),self)
        self.connections()
        self.fieldRow = 1
        self.customfields = []
        self.pushTags = dict()
        self.setup()
        self.show()
        self.setup()
        
        

    def connections(self):
        self.Add_Fields.clicked.connect(self.addField)
        self.RefreshButton.clicked.connect(self.default)
        self.DoneButton.clicked.connect(self.done)
    
    def done(self):
        tags = {
            "Sensors" : self.SensorList.text(),
            "Length" : self.Length.text(),
            "Date" : self.Date.text(),
            "Notes" : self.Notes.toPlainText()
        }
        
        for tagData in self.customfields: 
            if tagData[0].text() and tagData[1].text():
                tags[tagData[0].text()] = tagData[1].text()
        self.pushTags = tags
        self.close()
        return tags
            
    def addField(self):
        newLabel = QtWidgets.QLineEdit()
        newData = QtWidgets.QLineEdit()
        newButton = QtWidgets.QPushButton('X')
        newButton.setStyleSheet('QPushButton{ Color: red; font-weight: bold }')
        newButton.setMaximumSize(28,28)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(newData)
        hbox.addWidget(newButton)
        newLabel.setPlaceholderText("Tag Name")
        newData.setPlaceholderText("Tag Data")
        self.CustomFields.insertRow(self.fieldRow, newLabel, hbox)
        pair = newLabel, newData
        self.customfields.append(pair)
        self.fieldRow = self.fieldRow + 1
        newButton.clicked.connect(lambda: self.customfields.remove((newLabel,newData)))
        newButton.clicked.connect(self.decRow)
        newButton.clicked.connect(lambda : self.CustomFields.removeRow(newLabel))
        
    
    
    def decRow(self):
        self.fieldRow = self.fieldRow - 1
        
        
        
    def setup(self):
        self.default()
    
    def default(self):
        sensorNames = data.get_sensors(is_derived = None, is_connected = True)
        defSensors = ""
        for names in sensorNames:
            if defSensors != "":
                defSensors = defSensors + " " + names
            else: 
                defSensors = names
        today = datetime.today()
        date = today.strftime("%m/%d/%Y %H:%M")
        fileName = "Offroad_Test_"+ date[0:10].replace('/','.')
        self.Name.setText(fileName)
        self.Date.setText(date)
        self.SensorList.setText(defSensors)
        
                    
    
                
        
            
        
        
        
        





app = QtWidgets.QApplication([])
window = TagDialogueGUI()
app.exec_()
tags = window.pushTags