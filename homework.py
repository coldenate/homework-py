import datetime as dt
import json
import aiohttp
import humanize
import recurring_ical_events
import requests
from icalendar import Calendar, Event

assignments = Calendar.from_ical(urllib.request.urlopen("link").read())

class Assignment:
    def __init__(assignment, name, age):
        assignment.title = name
        assignment.description = description
        assignment.due_date = due_date