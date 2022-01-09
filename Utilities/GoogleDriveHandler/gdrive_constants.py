from pathlib import Path

_DEFAULT_DIRECTORY = str(Path.home()) + '\\AppData\\Local\\GTOffRoad\\'
DEFAULT_UPLOAD_DIRECTORY = _DEFAULT_DIRECTORY + 'UploadQueue\\'
DEFAULT_DOWNLOAD_DIRECTORY = _DEFAULT_DIRECTORY + 'Downloads\\'
DURATION_OPTIONS = ("All", "Under 4 minutes", "4-20 minutes",
                    "Over 20 minutes")
TEST_DATE_PERIOD_OPTIONS = ("All", "Last hour", "Today", "This week",
                            "This month", "This year")

# CUSTOM_PROPERTIES is only as guidance, no enforcement
CUSTOM_PROPERTIES = ("collection_start_time",
                     "collection_stop_time",
                     "scene",
                     "test_length",
                     "notes",
                     "some_properties_removed")

TIME_FORMAT = "%Y-%m-%d-%H-%M-%S"

# validating filename using regex by src
# https://stackoverflow.com/a/11794507/11031425
FILENAME_REGEX = "^[\w\-.][\w\-. ]*$"
