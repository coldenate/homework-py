# The issues I am hoping to solve

**Moodle** will automatically send assignments through an ICS file. This method is useful because it provides absence of authentication on the library end. Unfortuantely, we have to use an external calendar parsing tool that can slow things down. Post-parse, we assign the parcels into according object-oriented classes. This allows us to simplify the process of extracting assignment data through calendar files.

**Canvas**, my favorite SIS[1], offers an api to any data hungry student!! There is even a [python wrapper](https://github.com/ucfopen/canvasapi) for the Canvas LMS API made and ready to use. In this case, we use this library to make a universal OOP library that manages the assignments for one Student across different SIS[1]-es.

**FACTS RENWEB**, my enemy -- the spark for the fire of this project, holds an extremely rudimentary service (in comparison to canvas and moodle) for managing data. It is a closed source swamp of School - Family data. Holding billing information, student grade information, directory information, and student calendar information, this service bears no open use API, or service to authorize access to any data. However, in my school's situation, it remains as the hierarchy for all the data!! It hosts my school's Moodle instance. This means it is the golden treasure trove for student data, yet it is the hardest to access. Although it has a similar assignment - calendar file system to moodle, I wanted the grades out of it. So now, we have reverse engineering tasks to complete. This library will soon communicate with the website, and it will extract the data clean by using barebones form authorization. (The most insecure and distrustful way of authentication. No OAUTH2.)

## Why would a student need to have a universal bridge for MULTIPLE SIS[1]-es??

Good question...

> Ya' know, at first, it seems like a bizarre idea.

However, take a summer student for example, and throw multiple courses at them. If they learn CS and Calculus from different course systems, they need to have all their alert data in one place. This library doesn't forget data origin, but it allows users to have a flow of data to one place for clean representation.
