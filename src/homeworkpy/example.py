import homework  # importing the file that contains the objects. This is bound to change.
from private import link, login_info

LINK1 = link
LINK2 = "insert your link"
# Those are links to ics files. For now, ICS files are what we parse.


# m = input("Input 1 for homework or 2 for random ")

ns = homework.Student(
    "Note Salad",
    {
        link: True,
        "https://calendar.google.com/calendar/ical/njips87tv2foa0cdeehge6u17c%40group.calendar.google.com/private-eae13d44ba261de9f28664ded6223358/basic.ics": False,
        "https://har-tx.client.renweb.com/pwr/school/ical.cfm?u=1202570&h=7D8CF689EB7C&s=&ut=Student&f2=680740&sc=&t=sch": False,
    },
    True,
    renweb=True,
    renweb_link="https://har-tx.client.renweb.com",
    renwebCredentials=login_info,
)  # This is the creation of a Student object. It is assigned to "ns".
#  The parameter is a link to the server that will *immediately* serve the ics file.


ns.sync()
# this is the sync function. It will download the ics file from the link and parse it, and then it
# will sync the student object's dictionary of homework with it. (Moreso appends)

ns.cli_display_works()
# a simple test function that uses Rich to display
# a table of the homework objects. They are called works.
# print(ns.report_card.classes)
