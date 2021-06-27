import time
import threading
import logging
from datetime import datetime
from DataAcquisition.Data import Data
from DataAcquisition.DataImport import DataImport

logger = logging.getLogger("DataAcquisition")

data_collection_lock = threading.Lock()  # Creates a lock for data synchronization

# This is the main variable that can be accessed from other areas of the code. Use 'DataAcquisition.data'
data = Data(data_collection_lock)

# Set this to true if you want to test the code without having hardware connected
use_fake_inputs = True


def collect_data():
    from MainWindow import is_data_collecting
    data_import = DataImport(data, data_collection_lock, is_data_collecting, use_fake_inputs)
    logger.info("Running collect_data")
    while True:
        data_was_collecting = False
        time.sleep(.1)

        if is_data_collecting.is_set():
            data.reset()
            data_was_collecting = True
            logger.debug("Starting data collection")
            while is_data_collecting.is_set():
                data_import.update()
                time.sleep(.0001)

        if data_was_collecting:
            logger.info("Stopping data collection")
