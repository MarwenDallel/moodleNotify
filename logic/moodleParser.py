from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .utils import get_url_parameter


class MoodleParser:
    parser = "html.parser"

    @classmethod
    def parse_token(cls, response):
        def parse(self):
            login_token = BeautifulSoup(response(self).content, cls.parser).find(
                "input", attrs={"name": "logintoken"}
            )["value"]
            return login_token

        return parse

    @classmethod
    def parse_session_status(cls, response):
        def parse(self):
            session_status = response(self).json()
            return session_status[0]['data']['timeremaining']

        return parse

    @classmethod
    def parse_courses(cls, response):
        def parse(self):
            soup = BeautifulSoup(response(self).content, cls.parser)
            courses = {}
            for h3 in soup.findAll("h3", {"class": "coursename"}):
                for a in h3.findAll("a", "aalink"):
                    course_name = a.text.strip()
                    courses[course_name] = a.get("href")
            return courses

        return parse

    @classmethod
    def parse_grades(cls, response):
        def parse(self, grade_url):
            soup = BeautifulSoup(response(self, grade_url).content, cls.parser)
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

        return parse

    @classmethod
    def parse_averages(cls, response):
        def parse(self):
            soup = BeautifulSoup(response(self).content, cls.parser)
            averages = {}
            for tr in soup.select("table[id=overview-grade] > tbody > tr[class='']"):
                a = tr.select_one("td > a")
                grade_link = a.get("href")
                course_name = a.text.strip()
                grade = tr.find("td", "cell c1").text.strip()
                rank = tr.find("td", "cell c2").text.strip()
                course_id = get_url_parameter(grade_link, "id")[0]
                averages[course_name] = {
                    "courseLink": urljoin(self.url, f"course/view.php?id={course_id}"),
                    "gradeLink": grade_link,
                    "grade": grade,
                    "rank": rank,
                }
            return averages

        return parse

    @classmethod
    def parse_grade_items(cls, get_grade_items):
        def parse(self, averages):
            all_grades = get_grade_items(self, averages).copy()
            for course_name, value in all_grades.items():
                grade_link = value["gradeLink"]
                grades = self.get_grades(grade_link)
                all_grades[course_name]["gradeDetails"] = grades
            return all_grades

        return parse
