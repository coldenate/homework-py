import homework  # importing the file that contains the objects. This is bound to change.

link1 = "insert your link"
link2 = "insert your link" 
# Those are links to ics files. For now, ICS files are what we parse. 



m = input("Input 1 for homework or 2 for random ")

if m == "1":
    ns = homework.Student("Note Salad", link1) # This is the creation of a Student object. It is assigned to "ns". The parameter is a link to the server that will *immediately* serve the ics file.
if m == "2":
    ns = homework.Student("Note Salad", link2)

ns.sync() # this is the sync function. It will download the ics file from the link and parse it, and then it will sync the student object's dictionary of homework with it. (Moreso appends)
ns.cli_display_works() # a simple test function that uses Rich to display a table of the homework objects. They are called works.
