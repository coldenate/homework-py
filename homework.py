import datetime as dt
import json
import aiohttp
import humanize
import recurring_ical_events
import requests
from icalendar import Calendar, Event
import urllib

assignments = Calendar.from_ical(urllib.request.urlopen("link").read())

class Subject:
    pass

class Test:
    pass
class Quiz:
    pass
# an example of what I am looking for in hese classes
    # def __init__(self, name, due_date, points, weight):
    #     self.name = name
    #     self.due_date = due_date
    #     self.points = points
    #     self.weight = weight

    # def __str__(self):
    #     return f"{self.name} ({self.due_date})"

class Assignment:
    def __init__(assignment, name, description, due_date):
        assignment.title = name
        assignment.description = description
        assignment.due_date = due_date

