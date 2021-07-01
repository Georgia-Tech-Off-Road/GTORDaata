import time
import threading
import logging
from datetime import datetime
from DataAcquisition.Data import Data
from DataAcquisition.DataImport import DataImport

logger = logging.getLogger("DataAcquisition")

data_collection_lock = threading.Lock()  # Creates a lock for data synchronization
is_data_collecting = threading.Event()  # Creates an event to know if the data collection has started

# This is the main variable that can be accessed from other areas of the code. Use 'DataAcquisition.data'
data = Data(data_collection_lock)

# Set this to true if you want to test the code without having hardware connected
use_fake_inputs = False


def collect_data():
    data_import = DataImport(data, data_collection_lock, is_data_collecting, use_fake_inputs)
    logger.info("Running collect_data")
    data_was_collecting = False
    while True:
        data_import.update()
        time.sleep(.0001)

        if is_data_collecting.is_set() and not data_was_collecting:
            logger.info("Starting data collection")
            data.reset()
            data_was_collecting = True

        if not is_data_collecting.is_set() and data_was_collecting:
            logger.info("Stopping data collection")
            data_was_collecting = False
