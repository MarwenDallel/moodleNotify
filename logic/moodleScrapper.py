import json
import os
import pickle
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

from .credentialManager import CredentialManager
from .moodleParser import MoodleParser
from .setupLogger import logger
from .utils import json_to_file

# Disable SSL warning due to a shitty ass SSL certificate configuration
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
DATA_DIR = "./data"
COURSES_PATH = f"{DATA_DIR}/courses.json"
AVERAGES_PATH = f"{DATA_DIR}/averages.json"
GRADES_PATH = f"{DATA_DIR}/grades.json"


def required_login(func):
    def retry_login(self, *arg, **kw):
        res = func(self, *arg, **kw)
        if res.history and res.history[-1].status_code != 200:
            logger.warning("session expired")
            credential = CredentialManager.get_moodle_cred()
            self.login(credential.username, credential.password)
            res = func(self, *arg, **kw)
        return res

    return retry_login


class MoodleScrapper:
    def __init__(self, url):
        self.url = url
        self.login_url = urljoin(self.url, "login/index.php")
        self.averages_url = urljoin(self.url, "grade/report/overview/index.php")
        self.headers = {
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.parser = "html.parser"
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.cookies_path = 'cookies.bin'

    def __load_cookies(self):
        if os.path.exists(self.cookies_path):
            logger.info("loading cookies")
            with open(self.cookies_path, "rb") as f:
                self.session.cookies.update(pickle.load(f))

    def __save_cookies(self):
        logger.info("saving cookies")
        with open(self.cookies_path, "wb") as f:
            pickle.dump(self.session.cookies, f)

    def __get_token(self):
        login_page = self.session.get(self.login_url, verify=False).content
        login_token = BeautifulSoup(login_page, "html.parser").find(
            "input", attrs={"name": "logintoken"}
        )["value"]
        return login_token

    def is_logged(self):
        self.__load_cookies()
        home_page = self.session.get(self.login_url, verify=False).content
        login_status = (
            BeautifulSoup(home_page, self.parser).find(
                "div", {"class": "logininfo"}
            ).text
        )
        logger.info(login_status.lower())
        if "You are not logged in." in login_status:
            return False
        return True

    def login(self, username, password):
        logger.info("logging in")
        login_token = self.__get_token()
        payload = dict(anchor="",
                       logintoken=login_token,
                       username=username,
                       password=password,
                       rememberusername="1")
        home_page = self.session.post(
            self.login_url, verify=False, data=payload
        ).content
        soup = BeautifulSoup(home_page, self.parser)
        login_info = soup.find("div", {"class": "logininfo"})
        login_status = login_info.text
        if "You are not logged in." in login_status:
            return False
        self.__save_cookies()
        return True

    @MoodleParser.parse_courses
    @required_login
    def get_courses(self):
        self.__load_cookies()
        logger.info("retrieving courses")
        return self.session.get(self.url)

    @MoodleParser.parse_averages
    @required_login
    def get_averages(self):
        logger.info("retrieving averages")
        return self.session.get(self.averages_url)

    @MoodleParser.parse_grades
    @required_login
    def get_grades(self, grade_url):
        logger.info("retrieving grade item details")
        return self.session.get(grade_url)

    @MoodleParser.parse_grade_items
    def get_grade_items(self, averages):
        logger.info("retrieving grades")
        return averages

    def init(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        courses = self.get_courses()
        json_to_file(COURSES_PATH, courses)

        averages = self.get_averages()
        json_to_file(AVERAGES_PATH, averages)

        all_grades = self.get_grade_items(averages)
        json_to_file(GRADES_PATH, all_grades)

    def check_grades(self, comparator):
        comparator.old_grades = json.load(open(GRADES_PATH))

        courses = self.get_courses()
        json_to_file(COURSES_PATH, courses)

        averages = self.get_averages()
        json_to_file(AVERAGES_PATH, averages)

        all_grades = self.get_grade_items(averages)
        json_to_file(GRADES_PATH, all_grades)

        new_grades = comparator.find_new_grades(all_grades)
        return new_grades
