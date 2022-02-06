from DataAcquisition import data
import logging
import os
import scipy.io as sio

logger = logging.getLogger("DataExport")

def saveMAT(filename, directory):
    logger.info("Constructing MAT file...")
    if filename == "":
        return
    if ".mat" not in filename:
        filename = filename + ".mat"

    dataDict = dict()
    dataDict['collected_data'] = dict()

    # connected_sensors = data.get_sensors(is_connected=True)
    sensorsList = data.get_sensors(is_connected=True, is_derived=False)
    lastIndex = data.get_most_recent_index()

    for sensor in sensorsList:
        dataDict['collected_data'][sensor] = data.get_values(sensor, lastIndex, lastIndex+1)

    sio.savemat(os.path.join(directory, filename), dataDict, appendmat=True, oned_as="column")

    logger.info("MAT file constructed successfully")


if __name__ == "__main__":
    pass