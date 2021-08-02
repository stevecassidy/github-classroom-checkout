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
from nbconvert import HTMLExporter
from nbconvert.writers import FilesWriter
import glob

def read_github_roster(csvfile):
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
            if 'identifier' in line:
                match = re.search('\d+', line['identifier'])
                if match:
                    result[match.group(0)] = line['github_username']

    return result


def read_ilearn_export(csvfile):
    """Read the file exported from iLearn, return a
    dictionary with student id as the key and
    a dictionary with 'email' and 'group' as the values
    """

    result = {}
    with open(csvfile) as fd:
        reader = csv.DictReader(fd)
        for line in reader:
            if 'Email address' in line and line['Email address'] != '':
                groups = line['Groups'].split(';')
                workshop = [g for g in groups if 'Workshop' in g]
                if workshop != []:
                    workshop = workshop[0].replace('[', '').replace(']', '')
                    
                result[line['ID number']] = {'email': line['Email address'], 'workshop': workshop}

    return result


def merge_students(github, ilearn):
    """Generate one dictionary with info from both
    rosters, also return a dictionary with people not
    in both"""

    keys = set(github.keys())
    keys = set(keys.union(set(ilearn.keys())))

    roster = []
    missing = []
    for key in keys:
        if key in github and key in ilearn:
            student = ilearn[key].copy()
            student['id'] = key
            student['github'] = github[key]
            roster.append(student)
        elif key in github:
            missing.append({'id': key, 'github': github[key]})
        else:
            missing.append({'id': key, 'ilearn': ilearn[key]})

    return roster, missing


def checkout(config, student):
    """Checkout one student assignment into a directory
    named for the student id and workshop
    """

    if student['github']:
        outdir = os.path.join(config['outdir'], student['workshop'].replace("|", "-").replace(":", "."))
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        targetdir = os.path.join(outdir, student['id'])
        
        if os.path.exists(targetdir):
            # existing repo, pull
            cmd = ['git', 'pull']
            p1 = subprocess.Popen(cmd, cwd=targetdir, stdout=subprocess.PIPE)
            output = p1.communicate()
        else:
            repo = "%s/%s-%s" % (config['classroom'], config['assignment'], student['github'])
            cmd = ['git', 'clone', repo, targetdir]
            p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            output = p1.communicate()

        title = "<p>" + student['id'] + "</p>"
        return title + nbconvert(targetdir)
    
    else:
        return "<p>" + student['id'] + " has no Github ID</p>"


def nbconvert(targetdir):
    """Run 'jupyter nbconvert' in the target directory and return
    the path to any HTML files generated"""

    # 2. Instantiate the exporter. We use the `classic` template for now; we'll get into more details
    # later about how to customize the exporter further.
    html_exporter = HTMLExporter()
    html_exporter.template_name = 'classic'

    links = "<ul>"
    for nbfile in glob.glob(os.path.join(targetdir, '*.ipynb')):
        htmlfile = nbfile.replace('ipynb', 'html')
        (body, resources) = html_exporter.from_filename(nbfile)
        links += "<li><a target='new' href='" + htmlfile +"'>" + htmlfile + "</a></li>"
        with open(htmlfile, 'w') as out:
            out.write(body)

    links += "</ul>"

    return links


def checkout_workshop(config, students, workshops):
    """Checkout all students in the given workshops to
    targetdir, make subdirectories per workshop"""

    html = ""
    for student in students:
        if student['workshop'] in workshops:
            html += checkout(config, student)
            print('.', end='', flush=True)

    return html


def process(config):

    github = read_github_roster(config['github-roster'])
    ilearn = read_ilearn_export(config['ilearn-csv'])
    students, missing = merge_students(github, ilearn)

    return checkout_workshop(config, students, config['workshops'])



if __name__=='__main__':

    import sys

    config = {
        'github-roster': sys.argv[1],
        'ilearn-csv': sys.argv[2],
        'classroom': "git@github.com:MQCOMP2200-S2-2021",
        'assignment': "practical-week-1",
        'outdir': 'submissions',
        'workshops': ['Workshop_1|FRI|01:00PM|C13', 'Workshop_1|TUE|11:00AM|C01']
    }

    github = process(config)

