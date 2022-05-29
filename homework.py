import datetime as dt
import json
import urllib

import aiohttp
import humanize
import recurring_ical_events
import requests
from icalendar import Calendar, Event

link = "https://har-tx.moodle.renweb.com/calendar/export_execute.php?userid=509&authtoken=afe92bc34dfe7877aec562349a943f3ec47447a6&preset_what=all&preset_time=recentupcoming"

assignments = Calendar.from_ical(urllib.request.urlopen(link).read())

class Subject: 
    def __init__(name, level, description):
        pass
    pass

class Test:
    pass
class Quiz:
    def __init__(self, name, due_date, points, weight):
        self.name = name
        self.due_date = due_date
        self.points = points
        self.weight = weight

    def __str__(self):
        return f"{self.name} ({self.due_date})"

class Assignment:
    def __init__(assignment, name, description, due_date):
        assignment.title = name
        assignment.description = description
        assignment.due_date = due_date

