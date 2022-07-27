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
from requests.exceptions import MissingSchema
from rich.console import Console
from rich.table import Table

from .tools import cleanup_json, html_to_json


class ReportCard:
    """Object representing an instance of a Student's report card at a given time."""

    def __init__(
        self,
        known_classes: list = None,
        classes: dict = None,
    ):
        self.known_classes = known_classes
        self.courses = classes
        if self.known_classes is None:
            self.known_classes = []

    def merge_data(self, data: list, table_headers):

        """ONLY FOR USE WITH THE RENWEB REPORT CARD TABLES |
        Merge the stored table header with the table contents to prepare an accurate dictionary.
        Returns a list containing dictionaries corresponding to the amount of
        classes given to the initial inputs."""
        # Take two lists, merge them side by side into a dictionary
        empty_headers = {}  # usually empty
        credit_count = 0
        exam_count = 0
        for element in table_headers:
            if element == "Credit":
                credit_count += 1
                if credit_count > 1:
                    empty_headers[element + str(credit_count)] = None
            if element == "Exam":
                exam_count += 1
                if exam_count > 1:
                    empty_headers[element + str(exam_count)] = None
            if element == "":
                # omit adding a false flag (do nothing)
                continue
            empty_headers[element] = None

        all_classes = []

        for row in data:
            temp_dict = empty_headers.copy()
            for index, element in enumerate(row):
                try:
                    temp_dict[list(temp_dict)[index]] = element
                except IndexError:
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
        class_dictionaries = self.merge_data(
            data=self.known_classes, table_headers=table_headers
        )
        self.courses = class_dictionaries
        return class_dictionaries

    def extract_classes(self) -> dict:
        """Extracts classes from a report card"""
        student_courses = {}
        for course in self.courses:
            student_courses[course.name] = course

        return student_courses


class Student:
    """Object representing an individual student with data."""

    def __init__(
        self,
        name: str,
        providers: dict,
        # is_file: bool,
        email: str = None,
        assignments: list = None,
        report_card: ReportCard = None,
        courses: dict = None,
        renweb: bool = False,
        renweb_link: str = None,
        renweb_credentials: dict = None,
        renweb_district_code: str = None,
        renweb_logged_in: bool = False,
        renweb_calendar_sync: bool = False,
        auto_sync: bool = False,
        auto_sort: bool = False,
    ):
        self.name = name
        self.email = email
        self.providers = providers
        # self.providerIsFile = is_file
        self.assignments: list = assignments
        self.report_card: ReportCard = report_card
        self.courses = courses
        self.renweb = renweb
        self.renweb_link: self = renweb_link
        self.renweb_credentials: dict = renweb_credentials
        self.renweb_district_code: str = renweb_district_code
        self.renweb_session = None
        self.renweb_calendar_sync: bool = renweb_calendar_sync
        self.renweb_logged_in: bool = renweb_logged_in
        self.auto_sync: bool = auto_sync
        self.synced: bool = False
        self.auto_sort: bool = auto_sort

        if self.renweb_credentials is None:
            self.renweb_credentials = {
                "DistrictCode": None,
                "username": None,
                "password": None,
                "UserType": "PARENTSWEB-STUDENT",  # broken across sites
                "login": "Log+In",
            }
            # TODO Update this to the correct value when done

        if self.assignments is None:
            self.assignments = []
        if self.courses is None:
            self.courses = {}

        if self.renweb is True:
            self.renweb_session = requests.Session()

        # <-----> Initialization Done <----->
        if self.auto_sync is True:
            # very simple. We sync as soon as we initialize.
            self.sync()
            self.synced = True
        if self.synced and self.report_card is not None:
            #  assume classes from renweb report card.
            self.courses = self.report_card.extract_classes()
        if self.auto_sort is True:
            self.sort_assignments()

    def sort_assignments(self) -> list:
        """A function that sorts the self.assignments list by datetime.date in-place but also
        returns a copy of the sorted list."""
        self.assignments.sort(key=lambda x: x.due_date)
        return self.assignments

    def convert_to_dict(self, omit_assignments: bool = False) -> dict:
        """Convert all attributes of student to dictionary,
        but if save_space is true, take it out of the dictionary.
        :param save_space: If True, the dictionary will omit
        any assignments to save space. This is great for databases."""
        if omit_assignments:
            return {
                "name": self.name,
                "email": self.email,
                "provider": self.providers,
            }
        if omit_assignments is False:
            assignments = []
            for assignment in self.assignments:
                assignments.append(assignment.convert_to_dict())
            return {
                "name": self.name,
                "email": self.email,
                "provider": self.providers,
                "assignments": assignments,
            }

    def renweb_login(self) -> requests.Session:
        """Logs into the renweb website"""
        try:

            self.renweb_session.post(
                self.renweb_link + "/pwr/index.cfm", data=self.renweb_credentials
            )
            self.renweb_logged_in = True
        except requests.exceptions.MissingSchema:
            print("Failed to authenticate with Renweb Servers")

    def import_card_from_renweb(self):
        """imports data from the given renweb server url"""

        if self.renweb_logged_in is not True:
            self.renweb_login()
        try:
            report_card_main = self.renweb_session.get(
                self.renweb_link + "/pwr/student/report-card.cfm"
            )

            soup = BeautifulSoup(report_card_main, "html.parser")
            nas_report_card_element = soup.find_all("iframe", {"class": "gframe"})

            report_card_location = nas_report_card_element[0].attrs["src"]

            report_card_request = self.renweb_session.get(
                self.renweb_link + report_card_location
            )
            report_card_html = report_card_request.content

        except MissingSchema as error:
            print("HEEHEE HAAA")
            print(error)
            # Open local file
            report_card_request = open(self.renweb_link, "r", encoding="utf-8").read()

            report_card_html = report_card_request

        self.report_card = ReportCard()

        self.report_card.extract(report_card_html)

        self.renweb_session.close()

    # def some_random_calc(self):
    #     stt = dt.date.today() - dt.timedelta(days=1)  # yesterday
    #     yesterday = stt.strftime("%Y, %m, %d")
    #     fourtdayslater = dt.date.today() + dt.timedelta(days=14)
    #     truefourt = fourtdayslater.strftime("%Y, %m, %d")
    #     start_date = tuple(map(int, yesterday.split(", ")))
    #     end_date = tuple(map(int, truefourt.split(", ")))

    def datetime_to_tuple(self, datetime: dt.datetime) -> tuple:
        """Converts datetime objects to tuple for use in renweb calendar"""
        un_tupled_start_date = datetime.strftime("%Y, %m, %d")
        start_date = tuple(map(int, un_tupled_start_date.split(", ")))
        return start_date

    def datetime_to_string(self, datetime: dt.datetime, humanize: bool = False) -> str:
        """converts datetime object into string"""

        if humanize is False:
            starttime_formatted = datetime.strftime("%Y, %m, %d")
        if humanize is True:
            starttime_formatted = datetime.strftime("%B %d, %Y")
            return starttime_formatted

    def calculate_timeframe(self, rangetype: int = None) -> tuple | list:
        """Function that creates a timeframe
        :param rangetype: 1 for today, 2 for tomorrow, 3 for this week, 4 for next week,
        5 for this month, 6 for next month"""
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
                self.datetime_to_string(assignment.due_date, True),
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
        is_file: bool,
    ):
        """This function is designed to be iterable.
        NOT TO BE USED OUTSIDE OF LIBRARY"""
        try:
            # raw_assignments = Calendar.from_ical(fetch_calendar(self.provider).read())
            # this is the main kicker, or the ol can o' beans. It throws around the calendar file
            unprocessed_assignments = fetch_calendar(link, is_file=is_file)
        except FileNotFoundError:
            print(
                """Error fetching raw assignments.
                (Calendar file could not be reached or accessed.)
                Possible fixes include checking internet connection.
                \nThere could also be no events."""
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
                except KeyError:
                    event_name = "No Title"
                try:
                    event_course = event["CATEGORIES"].cats[
                        0
                    ]  # the first category found
                except KeyError:
                    event_course = "No course"
                try:
                    date = event["DTSTART"].dt
                    date_final = dt.datetime(date.year, date.month, date.day)

                except KeyError:
                    date_final = "No Start Time"
                try:
                    event_description = event["DESCRIPTION"]
                except KeyError:
                    event_description = "No Description"

                assignment = Assignment(
                    name=f"{event_name}",
                    description=f"{event_description}",
                    due_date=date_final,
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
        :param range_start: tuple of start date ex. (2020, 1, 2) -->
        (year, month, day)
        :param range_end: tuple of end date
        :param rangetype: None for no preconfig, 0 for all, 1 for today,
        2 for tomorrow, 3 for this week, 4 for next week,
        5 for this month, 6 for next month"""
        # ~~~~~~~~~~SYNCING CALENDARS~~~~~~~~~~~~~~~~
        listofassignments = []
        for provider in self.providers:
            # x = self.providers[provider]
            returned_assignments = self.process_append_ical_file(
                provider,
                range_start,
                range_end,
                rangetype,
                is_file=self.providers[provider],
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

        # ~~~~~~~~~~SYNCING REPORT CARDS~~~~~~~~~~~~~~~~
        if self.renweb is True:
            self.import_card_from_renweb()

        if self.synced is False:
            self.synced = True


class Course:
    """Object representing a Course a student may take in an education setting."""

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


class Assignment:
    """A class representing the an educational assignment a student may be given."""

    def __init__(
        self,
        name: str,
        description: str,
        due_date: dt.datetime,
        course: Course,
        is_homework: bool = None,
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
        self.is_homework = is_homework

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
    if is_file is False:
        file = urllib.request.urlopen(src)
        # return x
        raw_assignments = Calendar.from_ical(file.read())
        return raw_assignments
    if is_file is True:
        file = open(src, "r", encoding="utf-8")
        # return file
        raw_assignments = Calendar.from_ical(file.read())
        return raw_assignments
