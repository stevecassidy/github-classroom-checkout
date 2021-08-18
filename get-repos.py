from github import Github

import sys
import json

with open(sys.argv[1]) as input:
    config = json.load(input)


# personal access token from https://github.com/settings/tokens
g = Github(config['github-token'])

org = g.get_organization(config['organisation'])

students = {}
for repo in org.get_repos():
    if config['assignment'] in repo.full_name:
        for user in repo.get_collaborators("direct"):
           
            if user.login in students:
                students[user.login].append(repo.clone_url)
            else:
                students[user.login] = [repo.clone_url]


import csv

with open(config['github-repos-csv'], 'w') as fd:
    writer = csv.DictWriter(fd, ['githubID', 'githubURL'])
    writer.writeheader()
    for student in students:
        writer.writerow({'githubID': student, 'githubURL': "|".join(students[student])})
