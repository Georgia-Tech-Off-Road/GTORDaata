import time
import threading
import logging
import sys
from DataAcquisition.Data import Data
from DataAcquisition.DataImport import DataImport

logger = logging.getLogger("DataAcquisition")

data_collection_lock = threading.Lock()  # Creates a lock for data synchronization
is_data_collecting = threading.Event()  # Creates an event to know if the data collection has started
stop_thread = threading.Event()

# This is the main variable that can be accessed from other areas of the code. Use 'DataAcquisition.data'
data = Data(data_collection_lock)

# Initializes SD write value
data.set_current_value("command_auxdaq_sdwrite", False)

# This is the object that controls importing data
data_import = DataImport(data, data_collection_lock, is_data_collecting)


def read_data():
    """
    Looping function for reading data from all input modes. Executed by
    data_reading_thread in MainWindow.__init__.py when a valid mode is selected.

    :return: None
    """

    logger.info("Running read_data")
    data_was_collecting = False

    while True:
        if is_data_collecting.is_set() and not data_was_collecting:
            logger.info("Starting data collection")
            if "COM" in data_import.input_mode:
                data.reset()
            data_was_collecting = True

        if not is_data_collecting.is_set() and data_was_collecting:
            logger.info("Stopping data collection")
            data_was_collecting = False

        if stop_thread.is_set():
            sys.exit()

        if data_import.input_mode == "FAKE":
            data_import.check_connected_fake()
            data_import.read_data_fake()
            time.sleep(0.02)
        elif data_import.input_mode == "BIN" and data_import.data_file is not None:
            try:
                data_import.read_packet()
            except Exception as e:
                logger.error(e)
                logger.debug(logger.findCaller(True))
        elif "COM" in data_import.input_mode:
            try:                
                assert data_import.teensy_found
                assert data_import.check_connected()
                data_import.read_packet()                                            
            except AssertionError:
                data_import.connect_serial()    
            except:
                logger.info("Error in read_packet()")
        else:
            data_import.input_mode = ""
            time.sleep(0.01)
            pass


def send_data():
    """
    Handles the sending of packets to Teensy only when a COM input mode is
    selected. Executed by data_sending_thread in MainWindow.__init__.py.

    :return: None
    """

    if "COM" not in data_import.input_mode:
        pass
    else:
        try:
            if data_import.teensy_found and data_import.check_connected():
                data_import.send_packet()
        except Exception as e:
            logger.error(e)
