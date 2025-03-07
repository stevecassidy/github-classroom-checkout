# Github Classroom Tool

This project provides a tool to checkout all of the
student github repositories for one or more workshops.  It
assumes that you have password-less checkout configured
for github.

Create a file COMPXXX-something.json as a copy of CONFIG-SAMPLE.json and fill in the required values.

Files needed and where to get them.

`github-grades` is the 'grades' spreadsheet from the GitHub Classroom assignment, it contains the repository URLs for each student
`roster-csv` is downloaded from the GitHub Classroom student roster
`ilearn-csv` is the CSV version (download as plain text file) of the gradebook from iLearn, you don't need to 
include any grade items, just used for student details and workshop groups

Other configuration:

- `key-field` is the field from the iLearn CSV file that has been used as the student identifier on Classroom. Typically email or id.
- `outdir` a directory where repositories will be checked out
- `update-repo` if true, the script will checkout or pull changes for the student repo, if false, this is skipped
- `workshops` a list of workshop names to check out, default empty list means to check out all of them
- `commit-days` if set to a number N, will count the number of commits in the past N days, if left out, all commits are counted

`classroom.py COMP2200-weekly.json output.csv` will report on the status of students
and then clone all repositories in the list of workshops specified in the JSON file.  The output.csv file
will contain a report on the students and a count of the number of commits in their repository.
