import homework

link1 = "https://har-tx.moodle.renweb.com/calendar/export_execute.php?userid=509&authtoken=afe92bc34dfe7877aec562349a943f3ec47447a6&preset_what=all&preset_time=monthnow"
link = "https://calendar.google.com/calendar/ical/njips87tv2foa0cdeehge6u17c%40group.calendar.google.com/private-eae13d44ba261de9f28664ded6223358/basic.ics"
ns = homework.Student("Nate_Solis", link)

# ns.sync((2022, 5, 1), (2022, 5, 15))
#
# # collect data from the link

ns.sync(rangetype=6)
ns.cli_display_works()


# print(f"True:{ns.convert_to_dict(True)}")  # convert
# print(f"False:{ns.convert_to_dict()}")  # convert
