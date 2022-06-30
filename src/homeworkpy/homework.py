"""
Please refer to the documentation provided in the README.md,
which can be found at gorpyter's PyPI URL: https://pypi.org/project/gorpyter/
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
from tools import cleanup_json, html_to_json, merge_data

# TODO:
# - Implement overwrites for syncing.
#  - Uitlize other objects within storage
#  - Implement a versatile calendar range system.


@cache
def fetch_calendar(src: str, is_file: bool = False):
    """Fetches calendar file from url,
    :param: is_file | uses a file opener instead of a link"""
    if is_file == False:
        file = urllib.request.urlopen(src)
        # return x
        raw_works = Calendar.from_ical(file.read())
        return raw_works
    if is_file == True:
        file = open(src, "r")
        # return file
        raw_works = Calendar.from_ical(file.read())
        return raw_works


class ReportCard:
    def __init__(
        self,
        known_classes: list = [],
        classes: dict = None,
    ):
        self.known_classes = known_classes
        self.classes = classes

    def extract(self, html):
        """Extracts data from a report card (NOT TO BE USED OUTSIDE OF THIS LIBRARY)"""
        content_no_thead = html

        nothead = json.loads((html_to_json(content_no_thead, indent=4)))

        # print("cleaned up version")
        table_headers = cleanup_json(nothead, self.known_classes)
        classDictonaries = merge_data(self.known_classes, table_headers)
        self.classes = classDictonaries
        return classDictonaries


class Student:
    def __init__(
        self,
        name: str,
        provider: dict,
        # is_file: bool,
        email: str = None,
        works: list = [],
        report_card: ReportCard = None,
        classes: list = [],
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
    ):
        self.name = name
        self.email = email
        self.providers = provider
        # self.providerIsFile = is_file
        self.works: list = works
        self.report_card: ReportCard = report_card
        self.classes = classes
        self.renweb = renweb
        self.renweb_link: self = renweb_link
        self.renwebCredentials: dict = renwebCredentials
        self.renwebDisctrictCode: str = renwebDisctrictCode
        self.renwebSession = None
        self.renwebCalendarSync: bool = renwebCalendarSync
        self.renwebLoggedIn: bool = renwebLoggedIn

        if self.renweb == True:
            self.renwebSession = requests.Session()

    def convert_to_dict(self, save_space: bool = False) -> dict:
        """Convert all attributes of student to dictionary, but if save_space is true, take it out of the dictionary.
        :param save_space: If True, the dictionary will omit any works to save space. This is great for databases."""
        if save_space:
            return {
                "name": self.name,
                "email": self.email,
                "provider": self.providers,
            }
        if save_space == False:
            works = []
            for work in self.works:
                works.append(work.convert_to_dict())
            return {
                "name": self.name,
                "email": self.email,
                "provider": self.providers,
                "works": works,
            }

    def renwebLogin(self) -> requests.Session:
        """Logs into the renweb website"""
        login_info = self.renwebSession.post(
            self.renweb_link + "/pwr/index.cfm", data=self.renwebCredentials
        )
        self.renwebLoggedIn = True

    def import_card_from_renweb(self):

        if self.renwebLoggedIn != True:
            self.renwebLogin()

        reportCardMain = self.renwebSession.get(
            self.renweb_link + "/pwr/student/report-card.cfm"
        )

        soup = BeautifulSoup(reportCardMain.content, "html.parser")
        NASReportCardElement = soup.find_all("iframe", {"class": "gframe"})

        reportCardLocation = NASReportCardElement[0].attrs["src"]

        report_card_request = self.renwebSession.get(
            self.renweb_link + reportCardLocation
        )

        reportCardHTML = report_card_request.content

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

    def cli_display_works(self):
        """display all works in a table view using rich library"""
        table = Table(title=f"{self.name}'s Works")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Due Date")
        table.add_column("Subject")
        for work in self.works:
            table.add_row(
                work.title, work.description, work.due_date, work.subject.name
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
            # raw_works = Calendar.from_ical(fetch_calendar(self.provider).read())
            # this is the main kicker, or the ol can o' beans. It throws around the calendar file
            raw_works = fetch_calendar(link, is_file=isFile)
        except:
            print(
                "Error fetching raw works. (Calendar file could not be reached or accessed.) | Possible fixes include checking internet connection.\nThere could also be no events."
            )
            raw_works = None

        if range_start is None and range_end is None or rangetype == 0:
            events = recurring_ical_events.of(raw_works).all()
        if range_start is not None and range_end is not None:
            events = recurring_ical_events.of(raw_works).between(range_start, range_end)
        if rangetype == 0:
            events = recurring_ical_events.of(raw_works).all()
        if rangetype == 1:
            events = recurring_ical_events.of(raw_works).at(self.calculate_timeframe(1))
        if rangetype == 2:
            events = recurring_ical_events.of(raw_works).at(self.calculate_timeframe(2))
        if rangetype == 3:
            ranges = self.calculate_timeframe(3)
            events = recurring_ical_events.of(raw_works).between(ranges[0], ranges[1])
        if rangetype == 4:
            ranges = self.calculate_timeframe(4)
            events = recurring_ical_events.of(raw_works).between(ranges[0], ranges[1])
        if rangetype == 5:
            ranges = self.calculate_timeframe(5)
            events = recurring_ical_events.of(raw_works).between(ranges[0], ranges[1])
        if rangetype == 6:
            ranges = self.calculate_timeframe(6)
            events = recurring_ical_events.of(raw_works).between(ranges[0], ranges[1])

        if len(events) == 0:
            return False
        if len(events) > 0:
            works = []
            for event in events:
                try:
                    event_name = event["SUMMARY"]
                except:
                    event_name = "No Title"
                try:
                    event_subject = event["CATEGORIES"].cats[
                        0
                    ]  # the first category found
                except:
                    event_subject = "No Subject"
                try:
                    event_starttime = event["DTSTART"].dt
                    starttime_formatted = event_starttime.strftime("%B %d, %Y")
                except:
                    event_starttime = "No Start Time"
                try:
                    event_description = event["DESCRIPTION"]
                except:
                    event_description = "No Description"

                    # description = event["DESCRIPTION"]
                    # if description == None:
                    #     description = "No description"
                dict = {
                    "event_name": event_name,
                    "event_subject": event_subject,
                    "event_starttime": starttime_formatted,
                    "event_description": event_description,
                }
                work = Work(
                    name=f"{event_name}",
                    description=f"{event_description}",
                    due_date=f"{starttime_formatted}",
                    subject=Subject(name=f"{event_subject}"),
                )
                works.append(work)
            return works

    def sync(
        self,
        range_start: tuple = None,
        range_end: tuple = None,
        rangetype: int = None,
    ):
        """Function syncs Works Object type with cloud calendar file provider
        :param provider: url of calendar file provider
        :param range_start: tuple of start date ex. (2020, 1, 2) --> (year, month, day)
        :param range_end: tuple of end date
        :param rangetype: None for no preconfig, 0 for all, 1 for today, 2 for tomorrow, 3 for this week, 4 for next week, 5 for this month, 6 for next month"""
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~SYNCING CALENDARS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        listofworks = []
        for provider in self.providers:
            # x = self.providers[provider]
            returned_works = self.process_append_ical_file(
                provider,
                range_start,
                range_end,
                rangetype,
                isFile=self.providers[provider],
            )
            listofworks.append(returned_works)

        final_export = []
        for seto in listofworks:
            for work in seto:
                final_export.append(work) # we iterate through each individual event, and append it to an exportable list.
                # then we replace the object's works attribute with that.
        self.works = final_export

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~SYNCING REPORT CARDS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if self.renweb == True:
            self.import_card_from_renweb()


class Subject(Student):
    def __init__(self, name: str = None, description: str = None):
        self.name = name
        self.description = description

    pass


class Work(Student):
    def __init__(
        self,
        name: str,
        description: str,
        due_date: dt.datetime,
        subject: Subject,
        point_weight: int = None,
        completed: bool = False,
        grade: float = None,
        teacher=None,
    ):
        self.title = name
        self.description = description
        self.due_date = due_date
        self.point_weight = point_weight
        self.subject = subject
        self.completed = completed
        self.grade = grade
        self.teacher = teacher

    def convert_to_dict(self) -> dict:
        """convert each work into a dictionary"""
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "subject": self.subject.name,
            "point_weight": self.point_weight,
            "completed": self.completed,
            "grade": self.grade,
            "teacher": self.teacher,
        }
