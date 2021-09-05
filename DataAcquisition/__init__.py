import time
import threading
import logging
import sys
from datetime import datetime
from DataAcquisition.Data import Data
from DataAcquisition.DataImport import DataImport

logger = logging.getLogger("DataAcquisition")

data_collection_lock = threading.Lock()  # Creates a lock for data synchronization
is_data_collecting = threading.Event()  # Creates an event to know if the data collection has started
stop_thread = threading.Event()

# This is the main variable that can be accessed from other areas of the code. Use 'DataAcquisition.data'
data = Data(data_collection_lock)

# This is the object that controls importing data
data_import = DataImport(data, data_collection_lock, is_data_collecting)


def read_data():
    logger.info("Running read_data")
    data_was_collecting = False
    try:
        data_import.teensy_ser.flushInput()
    except AttributeError:
        logger.warning("Unable to flush Serial Buffer. No Serial object connected")
    while True:
        if data_import.input_mode == "Fake":
            data_import.check_connected_fake()
            data_import.read_data_fake()
        else:
            try:
                assert data_import.teensy_found
                try:
                    assert data_import.check_connected()
                    data_import.read_packet()
                except AssertionError:
                    logger.info("Serial port is not open, opening now")
                    try:
                        data_import.teensy_ser.open()
                    except Exception as e:
                        logger.error(e)
            except AssertionError:
                time.sleep(0)

        if is_data_collecting.is_set() and not data_was_collecting:
            logger.info("Starting data collection")
            data.reset()
            data_was_collecting = True

        if not is_data_collecting.is_set() and data_was_collecting:
            logger.info("Stopping data collection")
            data_was_collecting = False

        if stop_thread.is_set():
            sys.exit()

def send_data():
    if "COM" not in data_import.input_mode:
        pass
    else:
        try:
            if data_import.teensy_found and data_import.check_connected():
                data_import.send_packet()
        except Exception as e:
            logger.error(e)
