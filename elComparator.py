class Comparator():
    def __init__(self):
        self.__old_grades = None
        self.__old_courses = None
        self.__old_averages = None

    @property
    def old_grades(self):
        return self.__old_grades

    @old_grades.setter
    def old_grades(self, value):
        self.__old_grades = value

    @property
    def old_courses(self):
        return self.__old_courses

    @old_courses.setter
    def old_courses(self, value):
        self.__old_courses = value
 
    @property
    def old_averages(self):
        return self.__old_averages

    @old_averages.setter
    def old_averages(self, value):
        self.__old_averages = value
        
    def getAssignment(self, course_name, assignment_name):
        if assignment_name in self.old_grades[course_name]['gradeDetails']:
            return self.old_grades[course_name]['gradeDetails'][assignment_name]

    """
    This function will find new assignments and assignments whose grades were changed
    :param grades: dict
    :return: courses: dict
    """
    def findNewGrades(self, grades):
        courses = {}
        for course_name, course_content in grades.items():
            for assignment_name, assignment_details in course_content['gradeDetails'].items():
                assignment_old = self.getAssignment(course_name, assignment_name)
                try: 
                    if ((assignment_old == None and assignment_details['grade'] != "-") 
                        or (assignment_old['grade'] == "-" and assignment_details['grade'] != "-")):
                        courses[course_name] = {assignment_name: assignment_details}
                except:
                    pass
        return courses