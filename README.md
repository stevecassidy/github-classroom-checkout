# Github Classroom Tool

This project provides a tool to checkout all of the
student github repositories for one or more workshops.  It
assumes that you have password-less checkout configured 
for github.

Open the notebook to run the code or use the scripts directly.

`get-repos.py COMP2200-weekly.json` will use the Github API to find the 
github repository for each student for an assignment. It needs a Github
access token (from [https://github.com/settings/tokens](Github))
JSON config file.  It writes results to a csv file that is then read by the 
classroom script or notebook.

Note that it can happen that get-repos.py doesn't find the right repository 
for a student or doesn't find the repository. You might need to edit the
file before running the classrrom script or notebook.

`classroom.py COMP2200-weekly.json` will report on the status of students 
and then clone all repositories in the list of workshops specified in the JSON file. 

