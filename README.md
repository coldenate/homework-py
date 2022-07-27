# homework-py
[![Released to PyPi](https://github.com/colderinit/homework-py/actions/workflows/release.yml/badge.svg)](https://github.com/colderinit/homework-py/actions/workflows/release.yml)

An unofficial wrapper for FACTS SIS Renweb. It utilizes a combination of web scraping and data parsing to objectify student data.
There *are* plans to branch out to other services like Canvas, Moodle, and Google Classroom.

## Why is this project a little dead?

<details>
    <summary>TLDR: It got really difficult to keep up with the changes to the websites. Webscraping for makeshift api is not a sound way of doing this. Or at least I think.... `¯\_(ツ)_/¯` </summary>
        While I was working on attempting to reverse engineer another login form for Renweb, I came to the conclusion that it was not worth the effort trying to reverse every single login for each and every school. I don't know the actual sitemaps of individual pages for different schools as they may be able to edit the layout. I am also pretty stuck on some problems, but I have none to list because they require a ton of access to real datasets from my school's database. I think it was when I saw the global login form, I lost the groove that drove the first ~45 commits. If I find anything out, I may hit back to this repo, but for now, this is just a web scraping wrapper for Renweb. (Posing as a normal wrapper for an api that I don't have access to. Renweb closed that off a while ago, and you have to partner with them for heavy business - according to what I read.)

This repo will capture what I was able to write at an educational standpoint. My knowledge of oop and data comprehension. If you go to the school "HCA" and understand the following abbreviations [HCA, FBC] and know a man with a name that sounds like "*o***Kay** *would*" - then I have good news for you. This project does work with our school's sitemap because it is the only one I have the ability to test in.

</details>

I won't fully let go of this project as a maintainer, I simply would like to step back, (especially because I have no data to work with) and learn a little bit more about the subject matter and target problem. :) Cheers!

## Getting started

### How to install


```sh
pip install -U homeworkpy
```


### Features

- [x] Assignment Due Date Sorting
- [x] Automatic Syncing and Scraping
- [x] Import Renweb Report cards
- [x] Keep track of assignments through iCal files
- [x] Fetch ics files from url or drive path.
- [ ] import student-visible gradebook (the actual goodness of the project. Dataset not available untill November 2022. :( )  

#### How to Import

```python
from homeworkpy import homework
```

#### How to initialize a student

```python
bob_ross = homework.Student(
    name="Bob Ross",
    providers={"https://awesomecalendarwebsite.com/bobross/export.ics": True},
    email="bobross@painting.com",
    renweb=True,
    renweb_link="renweb_link",
    renweb_credentials={
        "DistrictCode": "HAR-TX",
        "username": "bross@woopainting!!.com",
        "password": "titaniumwhite",
        "UserType": "PARENTSWEB-STUDENT", # this is difficult to narrow down. This is why this library is not applicable to everyone. The form data input names changed per page. 
        "login": "Log+In",
    },
    auto_sync=True

)
```

In that snippet, we initialize a Student object with the name Bob Ross, and then tell the homework fetcher the icalendar files. The boolean value accompanying the icalendar paths determines whether or not it is a local file on the machine.
We provide an optional email, and give the renweb_link. This link is the url of the root of the SIS server.
The credentials are given in dictionary form. This is where the project dies a little bit. This is actually form data, but in a python dict. *For now,* I only have the form data working on one website. Feel free to contribute your own school.

```python
if ns.synced:
    ns.sort_assignments()
    ns.print_assignments()
```

Finally, if the auto_sync automatically synced with all the provided files and servers, we sort the assignments in chronological order, and print them to the console in a nice table format. The output may look like this:

```shell
Bob Ross's assignments                                     
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Name                     ┃ Description                            ┃ Due Date      ┃ course    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Happy Birthday Merica    │Wahoo this is a great day               │ July 04, 2022 │ No course │
└──────────────────────────┴────────────────────────────────────────┴───────────────┴───────────┘
```

I made this for fun to see how I could extract my grades with code.

### Awesome dependencies of this library(!!)

Full list of technical dependencies found [here](https://github.com/colderinit/homework-py/network/dependencies).

- beautifulsoup4 = {version = "4.11.1"}
- recurring-ical-events = {version = "1.0.2b0"}
- requests = {version = "2.28.0"}
- rich = {version = "12.4.4"}

## MIT License

`Copyright (c) 2022 Nathan Solis`
