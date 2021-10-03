import csv
import os
from DataAcquisition import data


def saveCSV(self, filename, directory, g_drive_folder_id="",
            GD_oAuth_client_file=""):
    # with open(filename, 'w', newline='') as csvfile:

    #TODO add smarter functionality to automatically make it a csv file
    if filename == "":
        return

    csvfile = open(os.path.join(directory, filename + ".csv"), 'w')
    writer = csv.writer(csvfile, dialect='excel', lineterminator='\n')

    # connected_sensors = data.get_sensors(is_connected=True)
    sensorsList = data.get_sensors(is_connected=True, is_derived=False)

    lastIndex = data.get_most_recent_index()
    sensorData = list()

    for index, sensor in enumerate(sensorsList):
        row = [sensor] + data.get_values(sensor, lastIndex, lastIndex+1)
        if sensor == 'time_internal_seconds':
            sensorData.insert(0, row)
        else:
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

    if g_drive_folder_id != "":
        upload_to_g_drive(filename, g_drive_folder_id, directory, GD_oAuth_client_file)


def upload_to_g_drive(filename, g_drive_folder_id, directory,
                      GD_oAuth_client_file):
    # Uses the Google Drive API to upload files onto a specific Google Drive
    # folder on an account that has sufficient permissions enabled.
    # To enable those permissions, see: https://learndataanalysis.org/google-
    # drive-api-in-python-getting-started-lesson-1/.
    # Citation: https://youtu.be/cCKPjW5JwKo, retrieved 09/30/2021
    from googleapiclient.http import MediaFileUpload
    from Utilities.DataExport.Google import Create_Service

    CLIENT_SECRET_FILE = GD_oAuth_client_file
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    # See citation what the Google Drive folder_id is
    folder_id = g_drive_folder_id

    # full_file_name e.g.: a.csv
    full_file_name = filename + '.csv'
    file_names = [full_file_name]

    # This mime_type is only for CSV files, see
    # https://learndataanalysis.org/commonly-used-mime-types/
    # for other file types.
    mime_types = ['test/csv']

    for file_name, mime_type in zip(file_names, mime_types):
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        full_filepath = directory + file_name

        media = MediaFileUpload(
            full_filepath,
            mimetype=mime_type)

        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

    pass


if __name__ == "__main__":
    pass
