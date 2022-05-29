import datetime as dt
import json
import urllib

import aiohttp
import humanize
import recurring_ical_events
import requests
from icalendar import Calendar, Event

link = "https://har-tx.moodle.renweb.com/calendar/export_execute.php?userid=509&authtoken=afe92bc34dfe7877aec562349a943f3ec47447a6&preset_what=all&preset_time=recentupcoming"


class Student:
    def __init__(self, name: str, provider: str, email: str = None, works: list = []):
        self.name = name
        self.email = email
        self.provider = provider
        self.works: list = works

    def cli_display_works(self):
        """display all works in a table view"""
        print("\n\n")
        print("{:^20}".format("Works"))
        print("{:^20}".format("-" * 20))
        for work in self.works:
            print(
                "{:<20} | {:<20} | {:<20} | {:<20}".format(
                    work.title, work.description, work.due_date, work.subject.name
                )
            )

    def sync(self, rangetype: int):
        """Function syncs Works Object type with cloud calendar file provider
        :param provider: url of calendar file provider"""
        raw_works = Calendar.from_ical(urllib.request.urlopen(self.provider).read())
        stt = dt.date.today() - dt.timedelta(days=1)  # yesterday
        yesterday = stt.strftime("%Y, %m, %d")
        fourtdayslater = dt.date.today() + dt.timedelta(days=14)
        truefourt = fourtdayslater.strftime("%Y, %m, %d")
        start_date = tuple(map(int, yesterday.split(", ")))
        end_date = tuple(map(int, truefourt.split(", ")))
        # we create a window of 14 days later to view the calendar.
        humanstart = stt.strftime("%B %d, %Y")  # human readable starttime
        humanend = fourtdayslater.strftime("%B %d, %Y")  # human readable endtime

        events = recurring_ical_events.of(raw_works).between(
            (2022, 5, 1), (2022, 5, 15)
        )
        if len(events) == 0:
            return False
        if len(events) > 0:
            works = []
            for event in events:
                event_name = event["SUMMARY"]
                event_subject = event["CATEGORIES"]

                # description = event["DESCRIPTION"]
                # if description == None:
                #     description = "No description"
                event_starttime = event["DTSTART"].dt
                starttime_formatted = event_starttime.strftime("%B %d, %Y")
                event_description = event["DESCRIPTION"]
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
                self.works.append(work)


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
        teacher: Student = None,
    ):
        self.title = name
        self.description = description
        self.due_date = due_date
        self.point_weight = point_weight
        self.subject = subject
        self.completed = completed
        self.grade = grade
        self.teacher = teacher
