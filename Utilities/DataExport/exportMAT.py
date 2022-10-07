from DataAcquisition import data
import logging
import numpy
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
        # ignore empty ['command_auxdaq_sdwrite'] sensor data
        if sensor == 'command_auxdaq_sdwrite':
            continue
        dataDict['collected_data'][sensor] = numpy.fromiter(
            data.get_values(sensor, lastIndex, lastIndex + 1), dtype=float)

    sio.savemat(os.path.join(directory, filename), dataDict, appendmat=True,
                oned_as="column")

    size = os.path.getsize(f"{directory}/{filename}")
    logger.info(
        f"MAT file of size {round(size / 1048576, 2)} MB constructed "
        f"successfully")


if __name__ == "__main__":
    pass
