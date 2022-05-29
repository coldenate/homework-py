import homework

link = "https://har-tx.moodle.renweb.com/calendar/export_execute.php?userid=509&authtoken=afe92bc34dfe7877aec562349a943f3ec47447a6&preset_what=all&preset_time=monthnow"

ns = homework.Student("Nate_Solis", link)

ns.sync(1)

ns.cli_display_works()

