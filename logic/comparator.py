class Comparator:
    def __init__(self):
        self._old_grades = None
        self._old_courses = None
        self._old_averages = None

    @property
    def old_grades(self):
        return self._old_grades

    @old_grades.setter
    def old_grades(self, value):
        self._old_grades = value

    @property
    def old_courses(self):
        return self._old_courses

    @old_courses.setter
    def old_courses(self, value):
        self._old_courses = value

    @property
    def old_averages(self):
        return self._old_averages

    @old_averages.setter
    def old_averages(self, value):
        self._old_averages = value

    def get_assignment(self, course_name, assignment_name):
        if assignment_name in self.old_grades[course_name]["gradeDetails"]:
            return self.old_grades[course_name]["gradeDetails"][assignment_name]

    def find_new_grades(self, grades):
        courses = {}
        for course_name, course_content in grades.items():
            for assignment_name, assignment_details in course_content[
                "gradeDetails"
            ].items():
                assignment_old = self.get_assignment(course_name, assignment_name)
                try:
                    if (assignment_old is None and assignment_details["grade"] != "-") or (
                            assignment_old["grade"] == "-" and assignment_details["grade"] != "-"):
                        courses[course_name] = {assignment_name: assignment_details}
                except (KeyError, ValueError):
                    pass
        return courses
