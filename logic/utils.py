import json
from urllib.parse import urlparse, parse_qs

from PySide2 import QtGui

APP_NAME = "moodleNotify"
VERSION = 2.2
MOODLE_URL = "https://moodle.medtech.tn/"
RELEASE_URL = "https://api.github.com/repos/MarwenDallel/moodleNotify/releases/latest"


def get_app_name():
    return APP_NAME


def get_version():
    return VERSION


def get_moodle_url():
    return MOODLE_URL


def get_release_url():
    return RELEASE_URL


def get_icon(path):
    return QtGui.QIcon(path)


def get_app_icon():
    return get_icon("assets/moodle.ico")


def get_url_parameter(url, parameter):
    parsed = urlparse(url)
    return parse_qs(parsed.query)[parameter]


def json_to_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def file_to_json(filename):
    with open(filename, "r") as f:
        json.load(f)


def display_averages(average):
    for key, value in average.items():
        print(
            f"""
{key}
    Grade: {value['grade']}
    Rank: {value['rank']}
    Link: {value['gradeLink']}"""
        )


def display_grades(grades):
    for key, value in grades.items():
        print(
            f"""
{key}
    Grade: {value['grade']}
    Letter Grade: {value['letterGrade']}
    Rank: {value['rank']}"""
        )
