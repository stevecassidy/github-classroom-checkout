"""Check out student submissions for an assignment"""

# driven by two csv files:
#  - export from GitHub Classroom roster containing
#       identifier, github_username, github_id, name
#  - export from iLearn containing
#       'Email address', 'ID number'
#
# input classroom name and assignment name
# then checks out one repository per student into a directory
# named for the 'ID number'
# reports any missing or extra students
#

import csv
import subprocess
import os
import re
import glob

def read_github_grades(csvfile):
    """Read the roster exported from github, return
    a dictionary with the student ID as the key and the
    github username as the value. If there is no github ID then
    the value will be ""
    """

    result = {}
    nogithub = []
    with open(csvfile) as fd:
        reader = csv.DictReader(fd)
        for line in reader:
            if line['roster_identifier'] == '':
                nogithub.append(line)
            else:
                result[line['roster_identifier']] = line['student_repository_url']

    print("Unidentified Github accounts")
    for row in nogithub:
        print(row['github_username'], row['student_repository_url'])

    return result


def read_ilearn_export(csvfile, key_field):
    """Read the file exported from iLearn, return a
    dictionary with student id as the key and
    a dictionary with 'email' and 'group' as the values
    """

    workshops = []
    result = {}
    with open(csvfile) as fd:
        reader = csv.DictReader(fd)
        for line in reader:
            if 'Email address' in line and line['Email address'] != '':
                groups = line['Groups'].split(';')
                workshop = [g for g in groups if 'Practical' in g or 'Workshop' in g]
                if workshop != []:
                    workshop = workshop[0].replace('[', '').replace(']', '')
                    if not workshop in workshops:
                        workshops.append(workshop)
                
                tmp = {'id': line['ID number'], 'email': line['Email address'], 'workshop': workshop}
                result[tmp[key_field]] = tmp

    return result

def read_github_roster(csvfile):
    """Read the CSV file class roster from GitHub Classroom"""

    roster = {}
    with open(csvfile) as fd:
        reader = csv.DictReader(fd)
        for line in reader:
            roster[line['identifier']] = line['github_username']

    return roster


def merge_students(config, github, ilearn, roster):
    """Generate one dictionary with info from both
    rosters, also return a dictionary with people not
    in both"""

    keys = set(roster.keys())
    keys = set(keys.union(set(ilearn.keys())))


    students = []
    not_in_github = []
    no_assignment_repo = []
    no_github_account = []
    for key in keys:
        if key in roster and key in ilearn:
            student = ilearn[key].copy() 
            if roster[key] != '':
                student['github'] = roster[key]
                if key in github:
                    student['url'] = github[key]
                else:
                    no_assignment_repo.append(key)
                students.append(student)
            else:
                no_github_account.append(ilearn[key])
                students.append(student)
        elif key in ilearn:
            not_in_github.append(key)

    return students, not_in_github, no_assignment_repo, no_github_account


def checkout(config, student, pull=True):
    """Checkout one student assignment into a directory
    named for the student id and workshop
    """

    student['count'] = 0
    if 'url' in student:
        outdir = os.path.join(config['outdir'], student['workshop'].replace("|", "-").replace(":", "."))
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        repoDir = os.path.join(outdir, student['id'])
        
        if os.path.exists(repoDir) and pull:
            # existing repo, pull
            cmd = ['git', 'pull']
            p1 = subprocess.Popen(cmd, cwd=repoDir, stdout=subprocess.PIPE)
            output = p1.communicate()
        elif pull:
            cmd = ['git', 'clone', '-n', student['url'], repoDir]
            print(' '.join(cmd))
            p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            output = p1.communicate()

        # if the repo exists then count commits
        if os.path.exists(repoDir):
            student['count'] = count_commits_for_student(repoDir)
    

def checkout_workshop(config, students, workshops, pull=True):
    """Checkout all students in the given workshops, 
    make subdirectories per workshop"""

    for student in students:
        if workshops == [] or student['workshop'] in workshops:
            count = checkout(config, student, pull)
            print('.', end='', flush=True)


def count_commits_for_student(repodir):
    """Count the number of commits per student"""

    cmd = ['git', '-C', repodir, 'log', '--oneline']
    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, foo = p1.communicate()

    output = output.decode().split('\n')
    return len(output)


def process(config):

    github = read_github_grades(config['github-grades'])
    roster = read_github_roster(config['roster-csv'])
    ilearn = read_ilearn_export(config['ilearn-csv'], config['key-field'])

    students, not_in_github, no_assignment_repo, no_github_account = merge_students(config, github, ilearn, roster)

    if config['report']:
        print("These students do not have a repo for this assignment yet\n")
        for m in no_assignment_repo:
            print(m)
        print("\nStudents not in Github Classroom Roster")
        print("Add these to the roster to associate with student github accounts\n")
        for m in not_in_github:
            print(m)
            #print(m[config['key-field']])

        print("\nThese students have no github account yet\n")
        for m in no_github_account:
            print(m['email'])

    checkout_workshop(config, students, config['workshops'], config['update-repos'])

    return students



if __name__=='__main__':

    import sys
    import json
    import csv

    with open(sys.argv[1]) as input:
        config = json.load(input)

    students = process(config)

    # Write the output to the csv file named on the command line

    keys = ['id', 'email', 'workshop', 'github', 'url', 'count']
    with open(sys.argv[2], 'w') as output:
        writer = csv.DictWriter(output, keys)
        writer.writeheader()

        for student in students:
            writer.writerow(student)

