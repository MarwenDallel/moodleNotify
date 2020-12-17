#!python
# -*- coding: utf-8 -*-

import json
import os
import pickle
from urllib.parse import urlparse, urljoin, parse_qs

import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

import elComparator
from setupLogger import logger

# Disable SSL warning due to a shitty ass SSL certificate configuration
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
DATA_DIR = "./data"
COURSES_PATH = f"{DATA_DIR}/courses.json"
AVERAGES_PATH = f"{DATA_DIR}/averages.json"
GRADES_PATH = f"{DATA_DIR}/grades.json"


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


class MoodleWrapper:
    def __init__(self, url):
        self.url = url
        self.login_url = urljoin(url, "login/index.php")
        self.averages_url = urljoin(url, "grade/report/overview/index.php")
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

    @staticmethod
    def __get_url_parameter(url, parameter):
        parsed = urlparse(url)
        return parse_qs(parsed.query)[parameter]

    def __load_cookies(self):
        if os.path.exists("cookies"):
            logger.info("loading cookies")
            with open("cookies", "rb") as f:
                self.session.cookies.update(pickle.load(f))

    def __save_cookies(self):
        logger.info("saving cookies")
        with open("cookies", "wb") as f:
            pickle.dump(self.session.cookies, f)

    def __get_token(self):
        login_page = self.session.get(self.login_url, verify=False).content
        login_token = BeautifulSoup(login_page, self.parser).find(
            "input", attrs={"name": "logintoken"}
        )["value"]
        return login_token

    def is_logged(self):
        self.__load_cookies()
        home_page = self.session.get(self.login_url, verify=False).content
        login_status = (
            BeautifulSoup(home_page, self.parser)
            .find("div", {"class": "logininfo"})
            .text
        )
        logger.info(login_status.lower())
        if "You are not logged in." in login_status:
            return False
        return True

    def login(self, username, password):
        logger.info("logging in")
        login_token = self.__get_token()
        payload = dict(anchor="", logintoken=login_token, username=username, password=password, rememberusername="1")
        home_page = self.session.post(
            self.login_url, verify=False, data=payload
        ).content
        login_status = (
            BeautifulSoup(home_page, self.parser)
            .find("div", {"class": "logininfo"})
            .text
        )
        if "You are not logged in." in login_status:
            return False
        self.__save_cookies()
        return True

    # Shows all courses on the homepage
    def get_courses(self):
        logger.info("retrieving courses")
        home_page = self.session.get(self.url).content
        soup = BeautifulSoup(home_page, self.parser)
        courses = {}
        for h3 in soup.findAll("h3", {"class": "coursename"}):
            for a in h3.findAll("a", "aalink"):
                course_name = a.text.strip()
                courses[course_name] = a.get("href")
        return courses

    def get_grade_items(self, averages):
        logger.info("retrieving grade items")
        all_grades = averages.copy()
        for course_name, value in all_grades.items():
            grade_link = value["gradeLink"]
            grades = self.get_grades(grade_link)
            all_grades[course_name]["gradeDetails"] = grades
        return all_grades

    def get_averages(self):
        logger.info("retrieving averages")
        averages_page = self.session.get(self.averages_url).content
        soup = BeautifulSoup(averages_page, self.parser)
        averages = {}
        for tr in soup.select("table[id=overview-grade] > tbody > tr[class='']"):
            a = tr.select_one("td > a")
            grade_link = a.get("href")
            course_name = a.text.strip()
            grade = tr.find("td", "cell c1").text.strip()
            rank = tr.find("td", "cell c2").text.strip()
            course_id = self.__get_url_parameter(grade_link, "id")[0]
            averages[course_name] = {
                "courseLink": urljoin(self.url, f"course/view.php?id={course_id}"),
                "gradeLink": grade_link,
                "grade": grade,
                "rank": rank,
            }
        return averages

    def get_grades(self, grade_url):
        logger.info("retrieving grade item details")
        grade_page = self.session.get(grade_url).content
        soup = BeautifulSoup(grade_page, self.parser)
        grades = {}
        for tr in soup.select("table[class*=user-grade] > tbody > tr"):
            tr_content = (
                tr.select_one("th > a")
                if tr.select_one("th > a") is not None
                else tr.select_one("th > span")
            )
            if tr_content:
                grade_item = tr_content.text.strip()
                grade = tr.select_one("td[headers*=grade]").text.strip()
                letter_grade = tr.select_one("td[headers*=lettergrade]").text.strip()
                rank = tr.select_one("td[headers*=rank]").text.strip()
                grades[grade_item] = {
                    "grade": grade,
                    "letterGrade": letter_grade,
                    "rank": rank,
                }
        return grades

    @staticmethod
    def init(moodle_wrapper):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        courses = moodle_wrapper.get_courses()
        json_to_file(COURSES_PATH, courses)

        averages = moodle_wrapper.get_averages()
        json_to_file(AVERAGES_PATH, averages)

        all_grades = moodle_wrapper.get_grade_items(averages)
        json_to_file(GRADES_PATH, all_grades)

    @staticmethod
    def check_grades(moodle_wrapper):
        el_comparator = elComparator.Comparator()
        el_comparator.old_grades = json.load(open(GRADES_PATH))

        courses = moodle_wrapper.get_courses()
        json_to_file(COURSES_PATH, courses)

        averages = moodle_wrapper.get_averages()
        json_to_file(AVERAGES_PATH, averages)

        all_grades = moodle_wrapper.get_grade_items(averages)
        json_to_file(GRADES_PATH, all_grades)

        new_grades = el_comparator.find_new_grades(all_grades)
        return new_grades
