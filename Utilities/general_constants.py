from pathlib import Path
import os

"""
Google Drive Handler constants
"""

# do not change the \\ to / as it will require change in code in other areas
_DEFAULT_DIRECTORY = str(Path.home()) + '\\AppData\\Local\\GTOffRoad\\'
DEFAULT_UPLOAD_DIRECTORY = _DEFAULT_DIRECTORY + 'UploadQueue\\'
DEFAULT_DOWNLOAD_DIRECTORY = _DEFAULT_DIRECTORY + 'Downloads\\'
PICKLE_DIRECTORY = './Utilities/GoogleDriveHandler'
GDRIVE_OAUTH2_SECRET = f"{os.getcwd()}\\secret_oAuth_key.json"

DURATION_OPTIONS = ("All", "Under 4 minutes", "4-20 minutes",
                    "Over 20 minutes")
TEST_DATE_PERIOD_OPTIONS = ("All", "Last hour", "Today", "This week",
                            "This month", "This year")

# CUSTOM_PROPERTIES is only as guidance, no enforcement
"""CUSTOM_PROPERTIES = ("collection_start_time",
                     "collection_stop_time",
                     "scene",
                     "test_length",
                     "notes",
                     "some_properties_removed")"""

FILENAME_TIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
ISO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# validating filename using regex by src
# https://stackoverflow.com/a/11794507/11031425
FILENAME_REGEX = "^[\w\-.][\w\-. ]*$"

"""
Miscellaneous
"""
DISPLAYABLE_IMPORTED_SCENES = {"DataCollection", "EngineDyno"}
