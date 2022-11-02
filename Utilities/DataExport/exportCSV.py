from DataAcquisition import data
import csv
import logging
import os

logger = logging.getLogger("DataExport")


def saveCSV(filename, directory):
    logger.info("Constructing CSV file...")
    # with open(filename, 'w', newline='') as csvfile:

    # TODO add smarter functionality to automatically make it a csv file
    if filename == "":
        return

    csvfile = open(os.path.join(directory, filename + ".csv"), 'w')
    writer = csv.writer(csvfile, dialect='excel', lineterminator='\n')

    # connected_sensors = data.get_sensors(is_connected=True)
    sensorsList = data.get_sensors(is_connected=True, is_derived=False)

    lastIndex = data.get_most_recent_index()
    sensorData = list()

    for index, sensor in enumerate(sensorsList):
        row = [sensor] + data.get_values(sensor, lastIndex, lastIndex + 1)
        if sensor == 'time_internal_seconds':
            sensorData.insert(0, row)
        elif sensor != 'command_auxdaq_sdwrite':
            # ignore empty ['command_auxdaq_sdwrite'] sensor data
            sensorData.append(row)

    # rows -> columns
    rows = zip(*sensorData)
    for row in rows:
        writer.writerow(row)

    # for sensor in sensorsList:
    #
    #
    # while (index <=lastIndex):
    #     print(index)
    #     rowData = list()
    #     rowData.append(data.get_value('time',index))
    #     for sensor in sensorsList:
    #         rowData.append(data.get_value(sensor,index))
    #     print(data.get_value('time',index))
    #     writer.writerow(rowData)
    #     index += 1

    csvfile.close()
    size = os.path.getsize(f"{directory}/{filename}.csv")
    logger.info(f"CSV file of {round(size / 1048576, 2)} MB constructed "
                f"successfully")


if __name__ == "__main__":
    pass
