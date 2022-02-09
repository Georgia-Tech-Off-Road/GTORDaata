import logging
from logging import StreamHandler, Formatter, Logger, getLogger
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

logging_objects = {
    "BlinkLEDTest": DEBUG,
    "DataAcquisition": INFO,
    "DataCollection": DEBUG,
    "DataExport": DEBUG,
    "EngineDyno": DEBUG,
    "GDriveDataExport": DEBUG,
    "GDriveDataImport": DEBUG,
    "GTORNetwork": CRITICAL,
    "GoogleDriveHandler": DEBUG,
    "Homepage": INFO,
    "Logging": DEBUG,
    "MainWindow": DEBUG,
    "Plotting": INFO,
}

# Console output handler
ch = StreamHandler()
ch.setLevel(logging.DEBUG)

# Formatter for the console output handler
formatter = Formatter(
    '%(asctime)s - %(name)-20s - %(filename)-20s - %(levelname)-10s - %(message)s')
ch.setFormatter(formatter)

# Create all the logging objects and add the stream handler to them
for name, level in logging_objects.items():
    logger = getLogger(name)
    logger.setLevel(level)
    logger.addHandler(ch)

logger = getLogger("Logging")
logger.info("Logger has been created")
