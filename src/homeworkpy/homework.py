"""
Please refer to the documentation provided in the README.md,
"""
import datetime as dt
import json
import urllib
import urllib.request
from functools import cache

import recurring_ical_events
import requests
from bs4 import BeautifulSoup
from icalendar import Calendar
from rich.console import Console
from rich.table import Table

from .tools import cleanup_json, html_to_json

# TODO:


class ReportCard:
    def __init__(
        self,
        known_classes: list = [],
        classes: dict = None,
    ):
        self.known_classes = known_classes
        self.courses = classes

    def merge_data(input: list, table_headers):
        # TODO: Redo this whole function to incorpate homework.Student.Course
        """ONLY FOR USE WITH THE RENWEB REPORT CARD TABLES | Merge the stored table header with the table contents to prepare an accurate dictionary.
        Returns a list containing dictionaries corresponding to the amount of classes given to the initial inputs."""
        # Take two lists, merge them side by side into a dictionary
        EMPTYHEADERS = {}
        credit_count = 0
        exam_count = 0
        for element in table_headers:
            if element == "Credit":
                credit_count += 1
                if credit_count > 1:
                    EMPTYHEADERS[element + str(credit_count)] = None
            if element == "Exam":
                exam_count += 1
                if exam_count > 1:
                    EMPTYHEADERS[element + str(exam_count)] = None
            if element == "":
                # omit adding a false flag (do nothing)
                continue
            EMPTYHEADERS[element] = None
            key = None

        all_classes = []

        for row in input:
            temp_dict = EMPTYHEADERS.copy()
            for index, element in enumerate(row):
                try:
                    temp_dict[list(temp_dict)[index]] = element
                except:
                    continue
            all_classes.append(temp_dict)

        list_of_classes = []
        for obj in all_classes:
            # this loop iteration will be the umbrella over a single Course Object.
            # we will match the keys of the dictionary to the course object attributes
            course = Course(
                name=obj["Subject"],
                teacher=obj["Teacher"],
                first_quarter_grade=obj["1st"],
                second_quarter_grade=obj["2nd"],
                first_exam_grade=obj["Exam"],
                semester_grade_first=obj["Sem 1"],
                credit_first_semester=obj["Credit"],
                third_quarter_grade=obj["3rd"],
                fourth_quarter_grade=obj["4th"],
                second_exam_grade=obj["Exam2"],
                semester_grade_second=obj["Sem 2"],
                credit_second_semester=obj["Credit2"],
            )
            list_of_classes.append(course)

        return list_of_classes

    def extract(self, html):
        """Extracts data from a report card (NOT TO BE USED OUTSIDE OF THIS LIBRARY)"""
        content_no_thead = html

        nothead = json.loads((html_to_json(content_no_thead, indent=4)))

        # print("cleaned up version")
        table_headers = cleanup_json(nothead, self.known_classes)
        classDictonaries = ReportCard.merge_data(self.known_classes, table_headers)
        self.courses = classDictonaries
        return classDictonaries

    def extract_classes(self) -> dict:
        """Extracts classes from a report card"""
        student_Courses = {}
        for course in self.courses:
            student_Courses[course.name] = course

        return student_Courses


class Student:
    def __init__(
        self,
        name: str,
        providers: dict,
        # is_file: bool,
        email: str = None,
        assignments: list = [],
        report_card: ReportCard = None,
        classes: dict = [],
        renweb: bool = False,
        renweb_link: str = None,
        renwebCredentials: dict = {
            "DistrictCode": None,
            "username": None,
            "password": None,
            "UserType": "PARENTSWEB-STUDENT",  # I think this will break across different renweb sites...
            "login": "Log+In",
        },
        renwebDisctrictCode: str = None,
        renwebLoggedIn: bool = False,
        renwebCalendarSync: bool = False,
        autoSync: bool = False,
    ):
        self.name = name
        self.email = email
        self.providers = providers
        # self.providerIsFile = is_file
        self.assignments: list = assignments
        self.report_card: ReportCard = report_card
        self.classes = classes
        self.renweb = renweb
        self.renweb_link: self = renweb_link
        self.renwebCredentials: dict = renwebCredentials
        self.renwebDisctrictCode: str = renwebDisctrictCode
        self.renwebSession = None
        self.renwebCalendarSync: bool = renwebCalendarSync
        self.renwebLoggedIn: bool = renwebLoggedIn
        self.autoSync: bool = autoSync
        self.synced: bool = False

        if self.renweb == True:
            self.renwebSession = requests.Session()

        # <-----> Initialization Done <----->
        if self.autoSync == True:
            # very simple. We sync as soon as we initialize.
            self.sync()
            self.synced = True
        if self.synced and self.report_card != None:
            #  assume classes from renweb report card.
            self.classes = self.report_card.extract_classes()

    def convert_to_dict(self, omit_assignments: bool = False) -> dict:
        """Convert all attributes of student to dictionary, but if save_space is true, take it out of the dictionary.
        :param save_space: If True, the dictionary will omit any assignments to save space. This is great for databases."""
        if omit_assignments:
            return {
                "name": self.name,
                "email": self.email,
                "provider": self.providers,
            }
        if omit_assignments == False:
            assignments = []
            for assignment in self.assignments:
                assignments.append(assignment.convert_to_dict())
            return {
                "name": self.name,
                "email": self.email,
                "provider": self.providers,
                "assignments": assignments,
            }

    def renwebLogin(self) -> requests.Session:
        """Logs into the renweb website"""
        try:

            login_info = self.renwebSession.post(
                self.renweb_link + "/pwr/index.cfm", data=self.renwebCredentials
            )
            self.renwebLoggedIn = True
        except requests.exceptions.MissingSchema:
            print("Failed to authenticate with Renweb Servers")

    def import_card_from_renweb(self):

        if self.renwebLoggedIn != True:
            self.renwebLogin()
        try:
            reportCardMain = self.renwebSession.get(
                self.renweb_link + "/pwr/student/report-card.cfm"
            )

            soup = BeautifulSoup(reportCardMain, "html.parser")
            NASReportCardElement = soup.find_all("iframe", {"class": "gframe"})

            reportCardLocation = NASReportCardElement[0].attrs["src"]

            report_card_request = self.renwebSession.get(
                self.renweb_link + reportCardLocation
            )
            reportCardHTML = report_card_request.content

        except Exception as e:
            print(e)
            # Open local file
            report_card_request = open(self.renweb_link, "r").read()
            reportCardHTML = report_card_request

        self.report_card = ReportCard()

        self.report_card.extract(reportCardHTML)

        self.renwebSession.close()

    def some_random_calc(self):
        stt = dt.date.today() - dt.timedelta(days=1)  # yesterday
        yesterday = stt.strftime("%Y, %m, %d")
        fourtdayslater = dt.date.today() + dt.timedelta(days=14)
        truefourt = fourtdayslater.strftime("%Y, %m, %d")
        start_date = tuple(map(int, yesterday.split(", ")))
        end_date = tuple(map(int, truefourt.split(", ")))

    def datetime_to_tuple(self, datetime: dt.datetime) -> tuple:
        un_tupled_start_date = datetime.strftime("%Y, %m, %d")
        start_date = tuple(map(int, un_tupled_start_date.split(", ")))
        return start_date

    def calculate_timeframe(self, rangetype: int = None) -> tuple | list:
        """Function that creates a timeframe
        :param rangetype: 1 for today, 2 for tomorrow, 3 for this week, 4 for next week, 5 for this month, 6 for next month"""
        if rangetype == 1:
            raw_format = dt.datetime.today()
            return self.datetime_to_tuple(raw_format)
        if rangetype == 2:
            raw_format = dt.datetime.today() + dt.timedelta(days=1)
            return self.datetime_to_tuple(raw_format)
        if rangetype == 3:
            ranges = []
            raw_start_time = dt.datetime.today()
            ranges.append(self.datetime_to_tuple(raw_start_time))
            raw_end_time = dt.datetime.today() + dt.timedelta(days=6)
            ranges.append(self.datetime_to_tuple(raw_end_time))
            return ranges
        if rangetype == 4:
            ranges = []
            raw_start_time = dt.datetime.today() + dt.timedelta(days=7)
            ranges.append(self.datetime_to_tuple(raw_start_time))
            raw_end_time = dt.datetime.today() + dt.timedelta(days=13)
            ranges.append(self.datetime_to_tuple(raw_end_time))
            return ranges
        if rangetype == 5:
            ranges = []
            raw_start_time = dt.datetime.today()
            raw_end_time = dt.datetime.today() + dt.timedelta(days=30)
            ranges.append(self.datetime_to_tuple(raw_start_time))
            ranges.append(self.datetime_to_tuple(raw_end_time))
            return ranges
        if rangetype == 6:
            ranges = []
            raw_start_time = dt.datetime.today() + dt.timedelta(days=31)
            raw_end_time = dt.datetime.today() + dt.timedelta(days=60)
            ranges.append(self.datetime_to_tuple(raw_start_time))
            ranges.append(self.datetime_to_tuple(raw_end_time))
            return ranges

    def print_assignments(self):
        """display all assignments in a table view using rich library"""
        table = Table(title=f"{self.name}'s assignments")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Due Date")
        table.add_column("course")
        for assignment in self.assignments:
            table.add_row(
                assignment.title,
                assignment.description,
                assignment.due_date,
                assignment.course.name,
            )
        console = Console()
        console.print(table)

    def process_append_ical_file(
        self,
        link: str,
        range_start: tuple,
        range_end: tuple,
        rangetype: int,
        isFile: bool,
    ):
        """This function is designed to be iterable.
        NOT TO BE USED OUTSIDE OF LIBRARY"""
        try:
            # raw_assignments = Calendar.from_ical(fetch_calendar(self.provider).read())
            # this is the main kicker, or the ol can o' beans. It throws around the calendar file
            unprocessed_assignments = fetch_calendar(link, is_file=isFile)
        except:
            print(
                "Error fetching raw assignments. (Calendar file could not be reached or accessed.) | Possible fixes include checking internet connection.\nThere could also be no events."
            )
            unprocessed_assignments = None

        if range_start is None and range_end is None or rangetype == 0:
            events = recurring_ical_events.of(unprocessed_assignments).all()
        if range_start is not None and range_end is not None:
            events = recurring_ical_events.of(unprocessed_assignments).between(
                range_start, range_end
            )
        if rangetype == 0:
            events = recurring_ical_events.of(unprocessed_assignments).all()
        if rangetype == 1:
            events = recurring_ical_events.of(unprocessed_assignments).at(
                self.calculate_timeframe(1)
            )
        if rangetype == 2:
            events = recurring_ical_events.of(unprocessed_assignments).at(
                self.calculate_timeframe(2)
            )
        if rangetype == 3:
            ranges = self.calculate_timeframe(3)
            events = recurring_ical_events.of(unprocessed_assignments).between(
                ranges[0], ranges[1]
            )
        if rangetype == 4:
            ranges = self.calculate_timeframe(4)
            events = recurring_ical_events.of(unprocessed_assignments).between(
                ranges[0], ranges[1]
            )
        if rangetype == 5:
            ranges = self.calculate_timeframe(5)
            events = recurring_ical_events.of(unprocessed_assignments).between(
                ranges[0], ranges[1]
            )
        if rangetype == 6:
            ranges = self.calculate_timeframe(6)
            events = recurring_ical_events.of(unprocessed_assignments).between(
                ranges[0], ranges[1]
            )

        assignments = []
        if len(events) == 0:
            return assignments
        if len(events) > 0:
            for event in events:
                try:
                    event_name = event["SUMMARY"]
                except:
                    event_name = "No Title"
                try:
                    event_course = event["CATEGORIES"].cats[
                        0
                    ]  # the first category found
                except:
                    event_course = "No course"
                try:
                    event_starttime = event["DTSTART"].dt
                    starttime_formatted = event_starttime.strftime("%B %d, %Y")
                except:
                    event_starttime = "No Start Time"
                try:
                    event_description = event["DESCRIPTION"]
                except:
                    event_description = "No Description"

                assignment = Assignment(
                    name=f"{event_name}",
                    description=f"{event_description}",
                    due_date=f"{starttime_formatted}",
                    course=Course(name=f"{event_course}"),
                )
                assignments.append(assignment)
            return assignments

    def sync(
        self,
        range_start: tuple = None,
        range_end: tuple = None,
        rangetype: int = None,
    ):
        """Function syncs assignments Object type with cloud calendar file provider
        :param provider: url of calendar file provider
        :param range_start: tuple of start date ex. (2020, 1, 2) --> (year, month, day)
        :param range_end: tuple of end date
        :param rangetype: None for no preconfig, 0 for all, 1 for today, 2 for tomorrow, 3 for this week, 4 for next week, 5 for this month, 6 for next month"""
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~SYNCING CALENDARS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        listofassignments = []
        for provider in self.providers:
            # x = self.providers[provider]
            returned_assignments = self.process_append_ical_file(
                provider,
                range_start,
                range_end,
                rangetype,
                isFile=self.providers[provider],
            )
            listofassignments.append(returned_assignments)

        final_export = []
        for seto in listofassignments:
            for assignment in seto:
                final_export.append(
                    assignment
                )  # we iterate through each individual event, and append it to an exportable list.
                # then we replace the object's assignments attribute with that.
        self.assignments = final_export

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~SYNCING REPORT CARDS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if self.renweb == True:
            self.import_card_from_renweb()

        if self.synced == False:
            self.synced = True


class Course(Student):
    def __init__(
        self,
        name: str = None,
        teacher: str = None,
        first_quarter_grade: str | int = None,
        second_quarter_grade: str | int = None,
        first_exam_grade: str | int = None,
        semester_grade_first: str | int = None,
        credit_first_semester: str | float = None,
        third_quarter_grade: str | int = None,
        fourth_quarter_grade: str | int = None,
        second_exam_grade: str | int = None,
        semester_grade_second: str | int = None,
        credit_second_semester: str | float = None,
    ):
        self.name = name
        self.teacher = teacher
        self.first_quarter_grade = first_quarter_grade
        self.second_quarter_grade = second_quarter_grade
        self.third_quarter_grade = third_quarter_grade
        self.fourth_quarter_grade = fourth_quarter_grade
        self.first_exam_grade = first_exam_grade
        self.second_exam_grade = second_exam_grade
        self.semester_grade_first = semester_grade_first
        self.semester_grade_second = semester_grade_second
        self.credit_first_semester = credit_first_semester
        self.credit_second_semester = credit_second_semester


class Assignment(Student):
    def __init__(
        self,
        name: str,
        description: str,
        due_date: dt.datetime,
        course: Course,
        isHomework: bool = None,
        point_weight: int = None,
        completed: bool = False,
        grade: float = None,
        teacher=None,
    ):
        self.title = name
        self.description = description
        self.due_date = due_date
        self.point_weight = point_weight
        self.course = course
        self.completed = completed
        self.grade = grade
        self.teacher = teacher
        self.isHomework = isHomework

    def convert_to_dict(self) -> dict:
        """convert each assignment into a dictionary"""
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "course": self.course.name,
            "point_weight": self.point_weight,
            "completed": self.completed,
            "grade": self.grade,
            "teacher": self.teacher,
        }


@cache
def fetch_calendar(src: str, is_file: bool = False):
    """Fetches calendar file from url,
    :param: is_file | uses a file opener instead of a link"""
    if is_file == False:
        file = urllib.request.urlopen(src)
        # return x
        raw_assignments = Calendar.from_ical(file.read())
        return raw_assignments
    if is_file == True:
        file = open(src, "r")
        # return file
        raw_assignments = Calendar.from_ical(file.read())
        return raw_assignments
