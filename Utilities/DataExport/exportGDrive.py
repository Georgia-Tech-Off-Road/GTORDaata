from googleapiclient.http import MediaFileUpload
from Utilities.DataExport.Google import Create_Service
import os
import logging

logger = logging.getLogger("DataExport")


def upload_to_g_drive(self, filename, directory, g_drive_folder_id,
                      GD_oAuth_client_file):
    # Uses the Google Drive API to upload files onto a specific Google Drive
    # folder on an account that has sufficient permissions enabled.
    # To enable those permissions, see: https://learndataanalysis.org/google-
    # drive-api-in-python-getting-started-lesson-1/.
    # Citation: https://youtu.be/cCKPjW5JwKo, retrieved 09/30/2021

    # only works for .CSV and .MAT files of the same 'filename'

    CLIENT_SECRET_FILE = GD_oAuth_client_file
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    # See citation what the Google Drive folder_id is
    folder_id = g_drive_folder_id

    # full_file_name e.g.: a.csv, a.mat
    file_names = [filename + '.csv', filename + ".mat"]

    # This mime_type is only for CSV files, see
    # https://learndataanalysis.org/commonly-used-mime-types/,
    # https://www.mpi.nl/corpus/html/lamus2/apa.html
    # for other file types.
    mime_types = ['test/csv', 'text/x-matlab']

    for file_name, mime_type in zip(file_names, mime_types):
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        full_filepath = directory + file_name

        if not os.path.exists(full_filepath):
            logging.error("File " + file_name + " was not created and thus, "
                                                "cannot be uploaded to Google "
                                                "Drive")
            continue

        media = MediaFileUpload(
            full_filepath,
            mimetype=mime_type)

        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
