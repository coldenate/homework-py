import homework  # importing the file that contains the objects. This is bound to change.
from private import link, link2, login_info

LINK1 = link
LINK2 = link2
LINK3 = "insert your link"
# Those are links to ics files. For now, ICS files are what we parse.


# m = input("Input 1 for homework or 2 for random ")

ns = homework.Student(
    "Note Salad",
    {
        # link: True,
        LINK2: False,
        # LINK3: False,
    },
    True,
    renweb=True,
    renweb_link="src/homeworkpy/Renweb Report.html",
    renwebCredentials=login_info,
    autoSync=False,
)  # This is the creation of a Student object. It is assigned to "ns".
#  The parameter is a link to the server that will *immediately* serve the ics file.


ns.sync(rangetype=1)  # This is the sync function. It will sync the student object with its provided file providers.
if ns.synced:

    print("Synced")
# this is the sync function. It will download the ics file from the link and parse it, and then it
# will sync the student object's dictionary of homework with it. (Moreso appends)

# ns.cli_display_works()
# a simple test function that uses Rich to display
# a table of the homework objects. They are called works.
# print(ns.report_card.classes)
