import httplib2
from googleapiclient.http import MediaFileUpload

import Utilities.DataExport.dataSaveLocation
from Utilities.DataExport.Google import Create_Service
import os
import logging
import datetime
import json
from pathlib import Path

logger = logging.getLogger("Utilities")
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
ROOT_FOLDER_ID = "1OaMbG-wAqC6_Ad8u5FiNS9L8z2W7eB2i"  # "GTORDaata Graph Files"
DRIVE_ID = "0AFmSv7widPF9Uk9PVA"  # GTOR_DAQ_DATA shared drive
DEFAULT_DIRECTORY = str(Path.home()) + '\\AppData\\Local\\GTOffRoad\\'
# Limit: https://developers.google.com/drive/api/v3/properties
PROPERTIES_LIMIT = 30  # public
APP_PROPERTIES_LIMIT = 30  # private outside of this application

"""
Uses the Google Drive API to upload all the files in this directory into a 
specific Google Drive folder on an account that has sufficient permissions 
enabled.
To enable those permissions, see: https://learndataanalysis.org/google-
drive-api-in-python-getting-started-lesson-1/.
Citation: https://youtu.be/cCKPjW5JwKo, retrieved 09/30/2021
"""
def upload_all_to_drive(directory: str, secret_client_file: str):
    CLIENT_SECRET_FILE = secret_client_file
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    drive_service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION,
                                   SCOPES)

    # fileA = ""

    files_to_upload = os.listdir(directory)
    if len(files_to_upload) > 0:
        for filename in files_to_upload:
            filepath = directory + filename
            validate_and_upload(drive_service, filepath)
            # if filename[-4:] != "json":
            #     fileA = filename

    # print(fileA)
    # list_of_files = find_file_in_drive(drive_service,
    #                                    filename=fileA,
    #                                    custom_properties={"sensor-test_sensor_0":"True"})
    # print("Found = ", end="")
    # if len(list_of_files) > 0:
    #     print(len(list_of_files))
    #     props = list_of_files[0].get('properties')
    #     appProps = list_of_files[0].get('appProperties')
    # else:
    #     print("No files to print")



def validate_and_upload(drive_service, filepath: str):
    filepath_list = filepath.split("\\")
    filename = filepath_list[len(filepath_list) - 1]

    if not validate_filename_format(filename):
        logger.error("File " + filename
                     + " to upload to Google Drive of non-legal format, should "
                       "be in format '2021-10-20-13-01-59.csv'")
        return

    day_folder_id = get_Day_folder_id(drive_service, filename)
    if day_folder_id is None:
        logger.error("Error in acquiring Day Test folder ID")
        return

    # Mime_type for CSV and MATLAB files, see
    # https://learndataanalysis.org/commonly-used-mime-types/ or
    # https://www.mpi.nl/corpus/html/lamus2/apa.html
    # for other file types.
    CSV_MIME_TYPE = 'test/csv'
    MAT_MIME_TYPE = 'text/x-matlab'

    if filename[-4:] == ".csv":
        with open(DEFAULT_DIRECTORY + filename[:-4] + '.json') as json_file:
            mydata = json.load(json_file)
        fileid = upload(drive_service, filepath, CSV_MIME_TYPE, day_folder_id,
                        custom_properties=mydata)
        if fileid is not None:
            remove_files(filepath)
            return fileid
    elif filename[-4:] == ".mat":
        fileid = upload(drive_service, filepath, MAT_MIME_TYPE, day_folder_id,
                        custom_properties=None)
        if fileid is not None:
            remove_files(filepath)
            return fileid
    else:
        logger.info("File " + filename + " will not be uploaded.")
        return


"""
Validating filename is of format YYYY-MM-DD-HH:MM:SS e.g. 
"2021-10-20-13:01:59.csv" or "2021-10-20-13:01:59"
Citation: https://stackoverflow.com/questions/16870663/
how-do-i-validate-a-date-string-format-in-python/16870699
"""
def validate_filename_format(filename: str) -> bool:
    try:
        datetime.datetime.strptime(filename[:10], '%Y-%m-%d')
    except ValueError:
        return False
    return True


"""
Finding the correct DayTest folder to put the results into, if none exists, 
create one with the correct hierarchy
Citation: https://developers.google.com/drive/api/v3/search-files#python

:filename: a filename of the format "2021-10-20-13:01:59.csv"

Hierarchy of GDrive:

Root
Year        # 2021
Month       ## 2021-10
Day         ### 2021-10-20
csv file    ##### 2021-10-20-13:01:59.csv
mat file    ##### 2021-10-20-13:01:59.mat
"""
def get_Day_folder_id(drive_service, filename: str):

    year_folder_id = get_Year_folder_id(drive_service, filename)
    month_folder_id = get_Month_folder_id(drive_service, filename,
                                          year_folder_id)

    day = filename[:10]  # e.g. 2021-10-21
    search_file_results = find_file_in_drive(drive_service, day,
                                             FOLDER_MIME_TYPE, 1,
                                             month_folder_id)
    if len(search_file_results) == 0:
        return create_folder_in_drive(drive_service, day, month_folder_id)
    elif len(search_file_results) == 1:
        return search_file_results[0].get('id')
    else:
        logger.error("File hierarchy error in Google Drive. Possibly two "
                     "same folder names")
        return None


def get_Month_folder_id(drive_service, filename: str, year_folder_id: str):
    month = filename[:7]
    search_file_results = find_file_in_drive(drive_service, month,
                                             FOLDER_MIME_TYPE, 1,
                                             year_folder_id)
    if len(search_file_results) == 0:
        return create_folder_in_drive(drive_service, month, year_folder_id)
    elif len(search_file_results) == 1:
        return search_file_results[0].get('id')
    else:
        logger.error("File hierarchy error in Google Drive. Possibly two "
                     "same folder names")
        return None


def get_Year_folder_id(drive_service, filename: str):
    year = filename[:4]
    search_file_results = find_file_in_drive(drive_service, year,
                                             FOLDER_MIME_TYPE, 1,
                                             ROOT_FOLDER_ID)

    if len(search_file_results) == 0:
        return create_folder_in_drive(drive_service, year, ROOT_FOLDER_ID)
    elif len(search_file_results) == 1:
        return search_file_results[0].get('id')
    else:
        logger.error("File hierarchy error in Google Drive. Possibly two "
                     "same folder names")
        return None


def create_folder_in_drive(drive_service, folder_name: str,
                           parent_folder_id: str = 'root'):
    return upload(drive_service, folder_name,
                  FOLDER_MIME_TYPE, parent_folder_id)


"""
Uploads the file or creates a new folder in the specified Google Drive parent 
folder. Returns file or folder ID, or None if an error occurs.
:filepath: filepath where the file resides e.g., 'C:\\Users\\afari\\a.txt', or 
if folder is being created will look like 'myFolder'
"""
def upload(drive_service, filepath: str, mime_type: str,
           parent_folder_id: str = 'root', custom_properties: dict = None):

    if drive_service is None \
            or parent_folder_id is None \
            or mime_type is None \
            or parent_folder_id is None:
        logging.error("One of GDrive upload() parameters is None.")
        return

    # if file being uploaded is a folder, we are not uploading anything but
    # instead creating a brand new folder
    if mime_type == 'application/vnd.google-apps.folder':
        file_metadata = {
            'name': filepath,
            'parents': [parent_folder_id],
            'mimeType': mime_type
        }
        try:
            folder = drive_service.files().create(
                supportsAllDrives=True,
                body=file_metadata, fields='id') \
                .execute()
            logger.info("Folder " + filepath + " successfully created in GDrive.")
            return folder.get('id')
        except httplib2.error.ServerNotFoundError:
            no_internet()
            return None
    else:
        # check if file exists
        if not os.path.exists(filepath):
            logging.error("File " + filepath + " does not exist and thus, "
                                                "cannot be uploaded to Google "
                                                "Drive")
            return None

        # get filename from filepath
        split_filepath = filepath.split("\\")
        filename = split_filepath[len(split_filepath) - 1]

        # if len(custom_properties) > 30, put the first 30 in 'properties' and
        # the next 30 in 'appProperties'. The rest are removed.
        gDrive_properties = dict()
        gDrive_appProperties = dict()

        if custom_properties is not None:
            if len(custom_properties) <= PROPERTIES_LIMIT:  # 30:
                gDrive_properties = custom_properties
            else:
                for key_i, key in enumerate(custom_properties.keys()):
                    if key_i <= PROPERTIES_LIMIT - 1:  # 29
                        gDrive_properties[key] = custom_properties[key]
                    elif key_i <= PROPERTIES_LIMIT + APP_PROPERTIES_LIMIT - 1:
                        # 59
                        gDrive_appProperties[key] = custom_properties[key]

        # upload to GDrive
        file_metadata = {
            'name': filename,
            'parents': [parent_folder_id],
            'properties': gDrive_properties,
            'appProperties': gDrive_appProperties
        }
        media = MediaFileUpload(filepath, mimetype=mime_type)
        try:
            file = drive_service.files().create(
                body=file_metadata,
                supportsAllDrives=True,
                media_body=media,
                fields='id'
            ).execute()
            logger.info("Files successfully saved to Google Drive")
            return file.get('id')
        except httplib2.error.ServerNotFoundError:
            no_internet()
            return None


"""
Returns a list of all the files or folders with the filename and other optional 
parameters in the Google Drive. Limits the search results to the first 
page_limit pages (defaults to first 5 pages).
Citation: https://developers.google.com/drive/api/v3/search-files#python

custom_properties is the custom dictionary of metadata we attached to the Google 
Drive file. If custom_properties is not None, this function returns all files with 
at least one match of the custom_properties. For example, if the only file "ex.csv"
in the Google Drive has custom_properties {"a": "1", "b":"2"} and our input 
custom_properties is {"a": "1", "c": 3}, the file will be returned. If ex.csv 
instead only has custom_properties {"a": "1", "b":"2"}, the file will not be 
returned.
"""
def find_file_in_drive(drive_service, filename: str = None,
                       mime_type: str = None, page_limit: int = 5,
                       parent_id: str = None, custom_properties: dict = None) \
                        -> list:

    list_of_files = []
    query = ""
    if filename is not None:
        if query != "":
            query += " and "
        query += "name='" + filename + "'"
    if mime_type is not None:
        if query != "":
            query += " and "
        query += "mimeType='" + mime_type + "'"
    if parent_id is not None:
        if query != "":
            query += " and "
        query += "'" + parent_id + "' in parents"
    if custom_properties is not None:
        if query != "":
            query += " and "
        query += "(properties has "
        for key in custom_properties:
            query += "{ key='" + key + "' and value='True' }"
            query += " or properties has "
        query = query[:-19]  # to remove the final ' or properties has '
        query += ")"
        print(query)

    # Metadata extracted in finding files.
    # Refer here for full list of target_metadata:
    # https://developers.google.com/drive/api/v3/reference/files
    METADATA_REQUESTED = "id, name, parents, mimeType, createdTime, " \
                         "modifiedTime, description, kind, driveId, " \
                         "properties, appProperties"

    page_token = None
    for i in range(page_limit):
        try:
            response = drive_service.files().list(
                                        q=query,
                                        spaces='drive',
                                        corpora='drive',
                                        driveId=DRIVE_ID,
                                        supportsAllDrives=True,
                                        includeItemsFromAllDrives=True,
                                        fields='nextPageToken, files('
                                               + METADATA_REQUESTED + ')',
                                        pageToken=page_token).execute()
            list_of_files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
        except httplib2.error.ServerNotFoundError:
            no_internet()
        if page_token is None:
            break

    return list_of_files

"""
Returns the filtered list of files whose metadata has all of the input 
target_metadata in the file's Google Drive metadata (properties or 
appProperties) dictionary.

The metadata has to exactly match except for the "sensors" metadata, which is a 
list. If the found_file "sensors" metadata contains any one of the sensors 
listed in the target_metadata, the found_file will be included in the filtered 
list.
"""
# def filter_by_metadata(list_of_files: list, target_metadata: dict) -> list:
#     filtered_list_of_files = []
#     for found_file in list_of_files:
#         file_metadata = found_file.get('properties')
#         if file_metadata is None:
#             continue
#         else:
#             try:
#                 sensors_metadata = "sensors"
#                 for target_metadata_key in target_metadata.keys():
#                     if target_metadata_key == sensors_metadata:
#                         file_sensors = file_metadata[sensors_metadata]
#                         target_sensors = target_metadata[sensors_metadata]
#                         if not sensors_present(file_sensors, target_sensors):
#                             continue
#                     else:
#                         if target_metadata[target_metadata_key] \
#                                 == file_metadata[target_metadata_key]:
#                             filtered_list_of_files.append(found_file)
#             except KeyError:
#                 continue
#     return filtered_list_of_files


"""
Returns True iff any of the file_sensors is contained in the target_sensors
"""
def sensors_present(file_sensors: list, target_sensors: list) -> bool:
    for target_sensor in target_sensors:
        if target_sensor in file_sensors:
            return True
    return False


def no_internet():
    logger.error("Failed to find Google Drive server. "
                 "Possibly due to internet problems.")


def remove_files(filepath):
    try:
        os.remove(filepath)
    except PermissionError:
        logger.warning("Temp files are in use and cannot be deleted.")
