from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QPushButton
import os
from Scenes import DAATAScene
import logging

from DataAcquisition import data_import, data

uiFile, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'BlinkLEDTest.ui'))  # loads the .ui file from QT Desginer

logger = logging.getLogger("BlinkLEDTest")


class BlinkLEDTest(DAATAScene, uiFile):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.hide()
        self.update_period = 10  # the tab updates every x*10 ms (ex. 3*10 = every 30 ms)

        self.is_sensors_attached = False

        self.connect_slots_and_signals()

    def update_active(self):
        pass

    def update_passive(self):
        if self.isVisible():
            if not self.is_sensors_attached:
                data_import.attach_output_sensor(data.get_id("command_toggle_teensy_led"))  # Attach the LED command
                self.is_sensors_attached = True
        else:
            if self.is_sensors_attached:
                data_import.detach_output_sensor(data.get_id("command_toggle_teensy_led"))  # Detach the LED command
                self.is_sensors_attached = False

    def slot_toggle_led_state(self):
        led_state = data.get_current_value("command_toggle_teensy_led")
        if led_state is 0:
            led_state = 1
            logger.debug("Toggling LED state to 1")
        else:
            led_state = 0
            logger.debug("Toggling LED state to 0")
        data.set_current_value("command_toggle_teensy_led", led_state)

    def connect_slots_and_signals(self):
        logger.debug("Connecting slots and signals")
        self.led_toggle.clicked.connect(self.slot_toggle_led_state)
        self.led_checkbox.clicked.connect(self.slot_toggle_led_state)



