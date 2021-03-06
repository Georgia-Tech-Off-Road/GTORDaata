import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import serial
from serial.serialutil import SerialException
import re, itertools
import winreg as winreg


class ListPortsDialog(QDialog):
    def __init__(self, parent=None):
        super(ListPortsDialog, self).__init__(parent)
        self.setWindowTitle('List of serial ports')

        self.chosen_port = ''

        self.ports_list = QListWidget()
        self.tryopen_button = QPushButton('Use this port')
        self.tryopen_button.clicked.connect(self.on_tryopen)
        
        #self.connect(self.tryopen_button, SIGNAL('clicked()'),
            #self.on_tryopen)
        
        layout = QVBoxLayout()
        layout.addWidget(self.ports_list)
        layout.addWidget(self.tryopen_button)
        self.setLayout(layout)

        self.fill_ports_list()

    def on_tryopen(self):
        cur_item = self.ports_list.currentItem()
        if cur_item is not None:
            fullname = self.full_port_name(str(cur_item.text()))
            try:
                ser = serial.Serial(fullname, 38400)
                ser.close()
                QMessageBox.information(self, 'Success',
                    'Opened %s successfully' % cur_item.text())
                self.chosen_port = fullname
            except SerialException as e:
                QMessageBox.critical(self, 'Failure',
                    'Failed to open %s:\n%s' % (
                        cur_item.text(), e))

    def fill_ports_list(self):
        for portname in self.enumerate_serial_ports():
            self.ports_list.addItem(portname)

    def full_port_name(self, portname):
        """ Given a port-name (of the form COM7, 
            COM12, CNCA0, etc.) returns a full 
            name suitable for opening with the 
            Serial class.
        """
        m = re.match('^COM(\d+)$', portname)
        if m and int(m.group(1)) < 10:
            return portname    
        return '\\\\.\\' + portname    
    

    def enumerate_serial_ports(self):
        """ Uses the Win32 registry to return an 
            iterator of serial (COM) ports 
            existing on this computer.
        """
        path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        except WindowsError:
            raise StopIteration

        for i in itertools.count():
            try:
                val = winreg.EnumValue(key, i)
                yield str(val[1])
            except EnvironmentError:
                break



if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ListPortsDialog()
    form.show()
    app.exec_()