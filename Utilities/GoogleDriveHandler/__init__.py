from Utilities.GoogleDriveHandler.Google import Create_Service
from Utilities.Popups.generic_popup import GenericPopup
from dataclasses import dataclass
from datetime import datetime, timedelta
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from pathlib import Path
import httplib2
import io
import json
import logging
import os
import requests

logger = logging.getLogger("GoogleDriveHandler")


@dataclass(frozen=True)
class DriveSearchQuery:
    # concrete search queries
    page_limit: int = 1
    file_id: str = None
    filename: str = None
    mime_type: str = None
    only_csv_mat: bool = False
    parent_id: str = None
    custom_properties: dict = None
    year: int = None
    month: int = None
    day: int = None
    # derived search queries
    test_date_period: str = None  # Last hour, Today, This Week, ...
    duration: str = None  # Under 4 minutes, 4-20 minutes, ...


class GoogleDriveHandler:
    # ROOT_FOLDER is "GTORDaata Graph Files"
    _ROOT_FOLDER_ID = "1OaMbG-wAqC6_Ad8u5FiNS9L8z2W7eB2i"
    _DRIVE_ID = "0AFmSv7widPF9Uk9PVA"  # Drive ID of GTOR_DAQ_DATA shared drive
    _DEFAULT_DIRECTORY = str(Path.home()) + '\\AppData\\Local\\GTOffRoad\\'
    DEFAULT_UPLOAD_DIRECTORY = _DEFAULT_DIRECTORY + 'UploadQueue\\'
    DEFAULT_DOWNLOAD_DIRECTORY = _DEFAULT_DIRECTORY + 'Downloads\\'
    DURATION_OPTIONS = ("All", "Under 4 minutes", "4-20 minutes",
                        "Over 20 minutes")
    TEST_DATE_PERIOD_OPTIONS = ("All", "Last hour", "Today", "This week",
                                "This month", "This year")

    def __init__(self, secret_client_file: str):
        # Mime_type for CSV and MATLAB files, see
        # https://learndataanalysis.org/commonly-used-mime-types/ or
        # https://www.mpi.nl/corpus/html/lamus2/apa.html
        # for other file types.
        self.MIME_TYPES = {
            "folder": "application/vnd.google-apps.folder",
            "csv": "test/csv",
            "mat": "text/x-matlab"
        }
        self.current_drive_folder = {"id": "", "name": ""}

        if not os.path.exists(secret_client_file):
            GenericPopup("Missing oAuth File",
                         f"oAuth file not detected in path "
                         f"{secret_client_file} entered")
            raise ValueError("Missing oAuth file")
        if not os.path.exists(self.DEFAULT_UPLOAD_DIRECTORY):
            logger.info(
                "Default path " + self.DEFAULT_UPLOAD_DIRECTORY
                + " not found. Making the directory...")
            os.mkdir(self.DEFAULT_UPLOAD_DIRECTORY)
        if not os.path.exists(self.DEFAULT_DOWNLOAD_DIRECTORY):
            logger.info(
                "Default path " + self.DEFAULT_DOWNLOAD_DIRECTORY
                + " not found. Making the directory...")
            os.mkdir(self.DEFAULT_DOWNLOAD_DIRECTORY)
        self.DRIVE_SERVICE = self.__create_drive_service(secret_client_file)

    def __create_drive_service(self, secret_client_file: str):
        if not os.path.exists(secret_client_file):
            GenericPopup("oAuth file not detected")
            return None

        # checks internet connection
        try:
            requests.head("https://www.google.com/", timeout=1)
        except requests.ConnectionError:
            self.no_internet()
            raise ValueError("No Internet connection")

        CLIENT_SECRET_FILE = secret_client_file
        API_NAME = 'drive'
        API_VERSION = 'v3'
        SCOPES = ['https://www.googleapis.com/auth/drive']

        return Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    def __develop_drive_search_q(self, search_q: DriveSearchQuery) -> str:
        # FUTURE TODO improve performance by filtering by date here instead of
        #  in __filter_by_derived_queries
        query = "trashed=false"
        if search_q.filename is not None:
            if query != "":
                query += " and "
            query += "name contains '" + search_q.filename + "'"
        if search_q.mime_type is not None:
            if query != "":
                query += " and "
            query += "mimeType='" + search_q.mime_type + "'"
        if search_q.only_csv_mat:
            if query != "":
                query += " and "
            query += f"(mimeType='{self.MIME_TYPES['csv']}' " \
                     f"or mimeType='{self.MIME_TYPES['mat']}')"
        if search_q.parent_id is not None:
            if query != "":
                query += " and "
            query += "'" + search_q.parent_id + "' in parents"
        if search_q.custom_properties is not None \
                and len(search_q.custom_properties) > 0:
            if query != "":
                query += " and "
            query += self.__create_custom_properties_query(
                search_q.custom_properties)

        return query

    def find_file_in_drive(self, search_q: DriveSearchQuery) -> list:
        """
        Returns a list of all the files or folders with the test_date and
        other optional parameters in the Google Drive. Limits the search
        results to the first page_limit pages (defaults to first 5 pages).
        Citation: https://developers.google.com/drive/api/v3/search-files
        #python

        custom_properties is the custom dictionary of metadata we attached to
        the Google Drive file. If custom_properties is not None,
        this function returns all files with at least one match of the
        custom_properties. For example, if the only file "ex.csv" in the
        Google Drive has custom_properties {"a": "1", "b":"2"} and our input
        custom_properties is {"a": "1", "c": 3}, the file will be returned.
        If ex.csv instead only has custom_properties {"a": "1", "b":"2"},
        the file will not be returned.
        """

        # Metadata extracted in finding files.
        # Refer here for full list of target_metadata:
        # https://developers.google.com/drive/api/v3/reference/files
        METADATA_REQUESTED = "id, name, parents, mimeType, createdTime, " \
                             "modifiedTime, description, " \
                             "properties, appProperties"

        found_files = []
        drive_search_q = self.__develop_drive_search_q(search_q)

        page_token = None
        for _ in range(search_q.page_limit):
            try:
                response = self.DRIVE_SERVICE.files().list(
                    q=drive_search_q,
                    spaces='drive',
                    corpora='drive',
                    driveId=self._DRIVE_ID,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                    fields='nextPageToken, files('
                           + METADATA_REQUESTED + ')',
                    pageToken=page_token).execute()
                found_files.extend(response.get('files', []))
                page_token = response.get('nextPageToken', None)
            except httplib2.error.ServerNotFoundError:
                self.no_internet()
                break
            if page_token is None:
                break

        return self.__filter_by_derived_queries(search_q, found_files)

    def __filter_by_derived_queries(self, search_q: DriveSearchQuery,
                                    found_files: list):
        if not found_files:
            # if found_files == [] or None.
            # if no files are inputted, return an empty list (obviously)
            return found_files

        if (search_q.year == search_q.month == search_q.day is None
                and search_q.test_date_period == search_q.duration is None):
            # if none of the derived filters are set, return original input
            return found_files

        def valid_year(begin_time: datetime) -> bool:
            return search_q.year is None or \
                   begin_time.year == int(search_q.year)

        def valid_month(begin_time: datetime) -> bool:
            return search_q.month is None or \
                   begin_time.month == int(search_q.month)

        def valid_day(begin_time: datetime) -> bool:
            return search_q.day is None or begin_time.day == int(search_q.day)

        def valid_test_date_period(begin_time: datetime) -> bool:
            if search_q.test_date_period == "All":
                return True
            elif search_q.test_date_period == "Last hour" and \
                    (datetime.now() - begin_time <= timedelta(hours=1)):
                return True
            elif search_q.test_date_period == "Today" and \
                    (datetime.now() - begin_time <= timedelta(days=1)):
                return True
            elif search_q.test_date_period == "This week" and \
                    (datetime.now() - begin_time <= timedelta(days=7)):
                return True
            elif search_q.test_date_period == "This month" and \
                    (begin_time.month == datetime.now().month):
                return True
            elif search_q.test_date_period == "This year" and \
                    (begin_time.year == datetime.now().year):
                return True
            else:
                return False

        def valid_duration(begin_end_times: list) -> bool:
            begin_time = begin_end_times[0]
            end_time = begin_end_times[1]
            if search_q.duration == "All":
                return True
            elif search_q.duration == "Under 4 minutes" and \
                    (end_time - begin_time <= timedelta(minutes=4)):
                return True
            elif search_q.duration == "4-20 minutes":
                duration = end_time - begin_time
                if (timedelta(minutes=4) <=
                        duration <= timedelta(minutes=20)):
                    return True
            elif search_q.duration == "Over 20 minutes" and \
                    (end_time - begin_time > timedelta(days=7)):
                return True
            return False

        filtered_list = []

        for file in found_files:
            begin_end = self.__get_test_begin_end_time(file)
            if not begin_end:  # if begin_end == []
                continue
            if valid_year(begin_end[0]) \
                    and valid_month(begin_end[0]) \
                    and valid_day(begin_end[0]) \
                    and valid_test_date_period(begin_end[0]) \
                    and valid_duration(begin_end):
                filtered_list.append(file)

        return filtered_list

    def validate_and_upload(self, filepath: str):
        # get filename from filepath
        split_filepath = filepath.split("\\")
        filename = split_filepath[len(split_filepath) - 1]

        # extract file metadata from JSON dump
        try:
            with open(self.DEFAULT_UPLOAD_DIRECTORY + filename[:-4]
                      + '.json') as json_file:
                file_metadata = json.load(json_file)
        except FileNotFoundError:
            logger.error("Metadata JSON file missing.")
            return None

        test_date = file_metadata["collection_start_time"]

        # if using previously searched folder, reuse it. Else, find it
        if test_date == self.current_drive_folder["name"]:
            day_folder_id = self.current_drive_folder["id"]
        else:
            day_folder_id = self.__get_Day_folder_id(test_date)
            self.current_drive_folder["id"] = day_folder_id
            self.current_drive_folder["name"] = test_date
        if day_folder_id is None:
            logger.error("Error in acquiring Day folder ID")
            return None

        if filename[-4:] == ".csv":
            file_id = self.upload(filepath, self.MIME_TYPES["csv"],
                                  day_folder_id,
                                  custom_properties=file_metadata)
            if file_id is not None:
                self.remove_file(filepath)
                return file_id
        elif filename[-4:] == ".mat":
            file_id = self.upload(filepath, self.MIME_TYPES["mat"],
                                  day_folder_id,
                                  custom_properties=file_metadata)
            if file_id is not None:
                self.remove_file(filepath)
                return file_id
        else:
            logger.info(f"File {filename} not of a supported type to be "
                        f"uploaded.")
            return None

    def __get_Day_folder_id(self, test_date: str):
        """
        Finding the correct DayTest folder to put the results into, if none
        exists, create one with the correct hierarchy Citation:
        https://developers.google.com/drive/api/v3/search-files#python

        :test_date: a test_date of the format "2021-10-20-13:01:59.csv"

        Hierarchy of GDrive:

        Root
        Year        # 2021
        Month       ## 2021-10
        Day         ### 2021-10-20
        csv file    ##### 2021-10-20-13:01:59.csv
        mat file    ##### 2021-10-20-13:01:59.mat
        """

        year_folder_id = self.__get_Year_folder_id(test_date)
        month_folder_id = self.__get_Month_folder_id(test_date, year_folder_id)

        day = test_date[:10]  # e.g. 2021-10-21
        day_folder = DriveSearchQuery(filename=day,
                                      mime_type=self.MIME_TYPES["folder"],
                                      parent_id=month_folder_id)
        search_file_results = self.find_file_in_drive(day_folder)
        if len(search_file_results) == 0:
            return self.create_folder_in_drive(day, month_folder_id)
        elif len(search_file_results) == 1:
            return search_file_results[0].get('id')
        else:
            return None

    def __get_Month_folder_id(self, test_date: str, year_folder_id: str):
        month = test_date[:7]
        month_folder = DriveSearchQuery(filename=month,
                                        mime_type=self.MIME_TYPES["folder"],
                                        parent_id=year_folder_id)
        search_file_results = self.find_file_in_drive(month_folder)
        if len(search_file_results) == 0:
            return self.create_folder_in_drive(month, year_folder_id)
        elif len(search_file_results) == 1:
            return search_file_results[0].get('id')
        else:
            logger.error("File hierarchy error in Google Drive. Possibly two "
                         "same folder names")
            return None

    def __get_Year_folder_id(self, test_date: str):
        year = test_date[:4]
        year_folder = DriveSearchQuery(filename=year,
                                       mime_type=self.MIME_TYPES["folder"],
                                       parent_id=self._ROOT_FOLDER_ID)
        search_file_results = self.find_file_in_drive(year_folder)

        if len(search_file_results) == 0:
            return self.create_folder_in_drive(year, self._ROOT_FOLDER_ID)
        elif len(search_file_results) == 1:
            return search_file_results[0].get('id')
        else:
            logger.error("File hierarchy error in Google Drive. Possibly two "
                         "same folder names")
            return None

    def create_folder_in_drive(self, folder_name: str,
                               parent_folder_id: str = 'root'):
        return self.upload(folder_name,
                           self.MIME_TYPES["folder"], parent_folder_id)

    def upload(self, filepath: str, mime_type: str,
               parent_folder_id: str = 'root', custom_properties: dict = None):
        """
        Uploads the file or creates a new folder in the specified Google Drive
        parent folder. Returns file or folder ID, or None if an error occurs.
        :filepath: filepath where the file resides e.g.,
        'C:\\Users\\afari\\a.txt', or if folder is being created will look like
        'myFolder'
        """

        if mime_type is None:
            logging.error("Mime type not given.")
            return None

        # if file being uploaded is a folder, we are not uploading anything but
        # instead creating a brand new folder
        if mime_type == self.MIME_TYPES["folder"]:
            file_metadata = {
                'name': filepath,
                'parents': [parent_folder_id],
                'mimeType': mime_type
            }
            try:
                folder = self.DRIVE_SERVICE.files().create(
                    supportsAllDrives=True,
                    body=file_metadata, fields='id') \
                    .execute()
                logger.info(
                    "Folder " + filepath + " successfully created in GDrive.")
                return folder.get('id')
            except httplib2.error.ServerNotFoundError:
                self.no_internet()
                return None
        else:
            # check if file exists
            if not os.path.exists(filepath):
                logging.error(f"File {filepath} does not exist and thus, "
                              f"cannot be uploaded to Google Drive")
                return None

            # get test_date from filepath
            split_filepath = filepath.split("\\")
            filename = split_filepath[len(split_filepath) - 1]

            # if len(custom_properties) > 30, put the first 30 in
            # 'properties' and the next 30 in 'appProperties'. The rest are
            # removed.
            gDrive_properties = dict()
            gDrive_appProperties = dict()

            # Limit: https://developers.google.com/drive/api/v3/properties
            PROPERTIES_LIMIT = 30  # public
            APP_PROPERTIES_LIMIT = 30  # private outside of this application

            if custom_properties is not None:
                if len(custom_properties) <= PROPERTIES_LIMIT:  # 30:
                    gDrive_properties = custom_properties
                else:
                    for i, (key, val) in enumerate(custom_properties.items()):
                        if i <= PROPERTIES_LIMIT - 1:  # 29
                            gDrive_properties[key] = val
                        elif i <= PROPERTIES_LIMIT + APP_PROPERTIES_LIMIT - 1:
                            # 59
                            gDrive_appProperties[key] = val
                        else:
                            # >= 60
                            break

            # upload to GDrive
            file_metadata = {
                'name': filename,
                'parents': [parent_folder_id],
                'properties': gDrive_properties,
                'appProperties': gDrive_appProperties
            }
            media = MediaFileUpload(filepath, mimetype=mime_type)
            try:
                file = self.DRIVE_SERVICE.files().create(
                    body=file_metadata,
                    supportsAllDrives=True,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info("Files successfully saved to Google Drive")
                return file.get('id')
            except httplib2.error.ServerNotFoundError:
                self.no_internet()
                return None

    def download(self, file: dict):
        # src: https://developers.google.com/drive/api/v3/manage-downloads
        request = self.DRIVE_SERVICE.files().get_media(fileId=file.get('id'))
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        # The file has been downloaded into RAM, now save it in a file
        # src: https://stackoverflow.com/a/55989689/11031425
        fh.seek(0)
        with io.open(f"{self.DEFAULT_DOWNLOAD_DIRECTORY}{file.get('name')}",
                     'wb') as f:
            fh.seek(0)
            f.write(fh.read())

    def upload_all_to_drive(self, progressBar_GD=None):
        """
        Uses the Google Drive API to upload all the files in this directory
        into a specific Google Drive folder on an account that has sufficient
        permissions enabled. To enable those permissions,
        see: https://learndataanalysis.org/google-drive-api-in-python-getting
        -started-lesson-1/. Citation: https://youtu.be/cCKPjW5JwKo, retrieved
        09/30/2021
        """

        # test_file = ""

        directory = self.DEFAULT_UPLOAD_DIRECTORY
        try:
            files_to_upload = os.listdir(directory)
        except FileNotFoundError:
            logger.error("Directory not found",
                         f"Please check if {directory} exists")
            return
        if len(files_to_upload) > 0:
            for file_i, filename in enumerate(files_to_upload):
                if filename[-3:] == "csv" or filename[-3:] == "mat":
                    filepath = directory + filename
                    self.validate_and_upload(filepath)
                    # test_file = test_date
                if progressBar_GD is not None:
                    progressBar_GD.setValue(int(
                        (file_i + 1) * 100 / len(files_to_upload)))
            logger.info("Uploading done")
        if progressBar_GD is not None:
            progressBar_GD.hide()

        # TEST MODULE
        # print(test_file)
        # list_of_files = find_file_in_drive(DRIVE_SERVICE,
        #                                    test_date=test_file,
        #                                    custom_properties
        #                                    ={"sensor-test_sensor_0": "True"})
        # print("Found = ", end="")
        # if len(list_of_files) > 0:
        #     print(len(list_of_files))
        #     props = list_of_files[0].get('properties')
        #     appProps = list_of_files[0].get('appProperties')
        # else:
        #     print("No files to print")

    @staticmethod
    def __get_test_begin_end_time(file: dict) -> list:
        begin_end = [-1, -1]
        for i, d in enumerate(
                ["collection_start_time", "collection_stop_time"]):
            try:
                begin_end[i] = datetime.strptime(file.get("properties").get(d),
                                                 "%Y-%m-%d %H:%M:%S.%f")
            except TypeError:
                # data not present in properties but may be present in
                # appProperties
                try:
                    begin_end[i] = datetime.strptime(
                        file.get("properties").get(d), "%Y-%m-%d %H:%M:%S.%f")
                except TypeError:
                    # data not present at all
                    return []
            except AttributeError:
                # parameter properties is missing
                return []
            except ValueError:
                # data not of correct format
                return []
        return begin_end

    @staticmethod
    def __create_custom_properties_query(custom_properties: dict) -> str:
        """
        Creates a query string parameter to be input into the Google Drive
        API to search for a specific file. The query parameter should asks
        Google Drive to return all files with all of the custom_properties
        entered. The custom_properties may exist in the properties or
        appProperties metadata.
        """

        query_list = list()

        query_list.append("(properties has ")
        for key in custom_properties.keys():
            query_list.extend(["{ key='", key, "' and value='",
                               custom_properties[key], "' }"])

            query_list.extend([" or appProperties has "])
            query_list.extend(["{ key='", key, "' and value='",
                               custom_properties[key], "' })"])

            query_list.extend([" and (properties has "])

        query_list.pop()  # to remove the final ' and properties has '

        custom_properties_query = ''.join(query_list)
        return custom_properties_query

    @staticmethod
    def remove_file(filepath: str):
        try:
            # remove the CSV/MAT file
            os.remove(filepath)

            # remove the JSON metadata file if both the CSV and MAT files are
            # gone
            if not os.path.exists(filepath[:-3] + "csv") \
                    and not os.path.exists(filepath[:-3] + "mat"):
                os.remove(filepath[:-3] + "json")
        except PermissionError:
            logger.warning("Temp files are in use and cannot be deleted.")
        except FileNotFoundError:
            logger.error("File to delete not found.")

    @staticmethod
    def no_internet():
        logger.error("Failed to find Google Drive server. "
                     "Possibly due to internet problems.")
        GenericPopup("No Internet",
                     "All files have been saved offline and will be uploaded "
                     "at the next upload instance")
