import homework

link1 = "https://har-tx.moodle.renweb.com/calendar/export_execute.php?userid=509&authtoken=afe92bc34dfe7877aec562349a943f3ec47447a6&preset_what=all&preset_time=recentupcoming"
link2 = "https://calendar.google.com/calendar/ical/njips87tv2foa0cdeehge6u17c%40group.calendar.google.com/private-eae13d44ba261de9f28664ded6223358/basic.ics"


# ns.sync((2022, 5, 1), (2022, 5, 15))
m = input("Input 1 for homework or 2 for random ")
# # collect data from the link
if m == "1":
    ns = homework.Student("Nate_Solis", link1)
if m == "2":
    ns = homework.Student("Nate_Solis", link2)

ns.sync()
ns.cli_display_works()


# print(f"True:{ns.convert_to_dict(True)}")  # convert
# print(f"False:{ns.convert_to_dict()}")  # convert
