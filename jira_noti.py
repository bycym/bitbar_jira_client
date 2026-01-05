#!/usr/bin/python3
# -*- coding: utf-8 -*-

# <bitbar.title>Jira status</bitbar.title>
# <bitbar.version>v1.3</bitbar.version>
# <bitbar.author>Aron Benkoczy</bitbar.author>
# <bitbar.author.github>bycym</bitbar.author.github>
# <bitbar.desc>Displays Open jira tickets.</bitbar.desc>
# <bitbar.dependencies>python</bitbar.dependencies>

import requests
import base64
import logging
import datetime
import time

bitbar_header = ['BB', '---']
# As some above have stated, using an API token will work (for JIRA Cloud).
# Create an API token here: https://id.atlassian.com/manage/api-tokens
# Use your email address as the username
# Use the token value as the password
USER="<jira_user>@email"
PASSW="<jira_api_token>"
SERVER="<jira_server>"
assignee="assignee="+"currentuser()"
TOPRECENT=10
# Adjust title length of a ticket in status
STATUSLENGTH=20
# Adjust title length of a ticket in dropdown menu
TICKETLENGTH=80
COLORING=True
NONSPRINT='[Non sprint]'
CACHE_FILE="not/jira_noti.cache"
TIME_OUT=3

### CUSTOM SECTION ###
def add_custom_header(header):
  ## Custom header link >>>>>
  # example:
  # example = '<name of the link> | href=' + SERVER + '<link of board or whatelse on the server>'
  kanban = 'My board | href=' + SERVER + '/secure/RapidBoard.jspa?rapidView=28'
  # append to the header
  header.append("%s" % (kanban))
  refresh = "Refresh... | refresh=true"
  header.append("%s" % (refresh))
  ## <<<<< Custom header link

# color option for the priority
def priorityColorCoding(priority):
  priorityColor = " color="
  if(str(priority) == "Blocker"):
    priorityColor = priorityColor + "#ff4000"
  elif (str(priority) == "Critical"):
    priorityColor = priorityColor + "#ff5d5d"
  elif (str(priority) == "Major"):
    priorityColor = priorityColor + "#ff8d8d"
  elif (str(priority) == "Minor"):
    priorityColor = priorityColor + "#FFC7C7"
  else:
    priorityColor = priorityColor + "#000000"
  return priorityColor

### END OF THE CUSTOM SECTION ###

# Defines a function for connecting to Jira using REST API v3
def create_jira_session(jira_server, jira_user, jira_password):
  try:
    session = requests.Session()
    # Create basic auth header
    credentials = f"{jira_user}:{jira_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    session.headers.update({
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    session.timeout = TIME_OUT
    return session, jira_server
  except Exception as e:
    logging.error("Failed to create JIRA session: %s" % e)
    return None, None

# Search issues using REST API v3
def search_issues_v3(session, server, jql, fields=None, max_results=50):
  try:
    # Ensure server doesn't have trailing slash for consistent URLs
    server = server.rstrip('/')
    url = f"{server}/rest/api/3/search/jql"
    params = {
        'jql': jql,
        'maxResults': max_results,
        'startAt': 0,
        'fields': 'key,summary,status,updated,priority,customfield_10007'
    }
    
    if fields:
        params['fields'] = ','.join(fields)
    
    response = session.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    return JiraSearchResult(data)
    
  except Exception as e:
    logging.error(f"Failed to search issues: {e}")
    return None

# Helper class to mimic the old JIRA client structure
class JiraSearchResult:
    def __init__(self, data):
        self.issues = [JiraIssue(issue) for issue in data.get('issues', [])]
    
    def __len__(self):
        return len(self.issues)
    
    def __iter__(self):
        return iter(self.issues)

class JiraIssue:
    def __init__(self, issue_data):
        self.key = issue_data.get('key')
        self.raw = issue_data
        self.fields = JiraFields(issue_data.get('fields', {}))

class JiraFields:
    def __init__(self, fields_data):
        self.status = JiraStatus(fields_data.get('status', {}))
        self.summary = fields_data.get('summary', '')
        self.updated = fields_data.get('updated', '')
        self.priority = JiraPriority(fields_data.get('priority', {}))
        self.customfield_10004 = fields_data.get('customfield_10004')  # Sprint field
        self.sprint = fields_data.get('sprint', '')
        
class JiraStatus:
    def __init__(self, status_data):
        self.name = status_data.get('name', '')
    
    def __str__(self):
        return self.name

class JiraPriority:
    def __init__(self, priority_data):
        self.name = priority_data.get('name', '')
    
    def __str__(self):
        return self.name

class JiraWorklog:
    def __init__(self, worklog_data):
        self.worklogs = [JiraWorklogEntry(wl) for wl in worklog_data.get('worklogs', [])]

class JiraWorklogEntry:
    def __init__(self, worklog_data):
        self.updated = worklog_data.get('updated', '')
        self.timeSpent = worklog_data.get('timeSpent', '')
        self.comment = worklog_data.get('comment', '')
        self.updateAuthor = JiraAuthor(worklog_data.get('updateAuthor', {}))

class JiraAuthor:
    def __init__(self, author_data):
        self.displayName = author_data.get('displayName', '')
    
    def __str__(self):
        return self.displayName

# Get bitbar status
def get_in_progress_item(issues):
  myIssues=[]
  mySprints={}
  mySprints[NONSPRINT] = []
  bitbar_header = ['']

  ###############################################################################
  ## header rows
  ####################

  ## drop down started
  bitbar_header.append("%s" % ("---"))
  ## refer link to the in progress element
  dashboard = 'LINK_TO_TOP'
  bitbar_header.append("%s" % (dashboard))
  ## dashboard link
  dashboard = 'Dashboard | href=' + SERVER + '/secure/Dashboard.jspa'
  bitbar_header.append("%s" % (dashboard))
  ## add more custom link
  add_custom_header(bitbar_header)

  ###############################################################################

  # filter out Closed or Blocked items
  for issue in issues:
    if (str(issue.fields.status) not in ('Closed', 'Blocked', 'Done', 'QA', 'Resolved', 'Needs Info')):
      issue.fields.summary = issue.fields.summary.replace("|","::")
      myIssues.append(issue);
      sprintName = issue.fields.sprint
      if(sprintName != ''):
        mySprints[sprintName] = []

  myIssues.sort(key=lambda x: x.fields.updated, reverse=True)
  
  bitbar_header.append("%s" % ("---"))
  recent = 'Recent(' + str(TOPRECENT) + '):'
  bitbar_header.append("%s" % (recent))

  ###############################################################################
  ## TOP RECENT
  ####################
  i = 0
  for element in myIssues:
    status=""
    sprintName = element.fields.sprint

    # Create ticket with sprint name if it exsist
    # <ID>(<status>) :: <Title>
    status = status + str(element.key) + "(" + str(element.fields.status) + ") :: " + str(element.fields.summary)
    if(len(status) > TICKETLENGTH):
      status = status[0:TICKETLENGTH] + '..'
    else:
      status = status[0:TICKETLENGTH]
    status = status + " | href=" + SERVER + "/browse/" + str(element.key)
    # coloring
    if(COLORING):
      status = status + str(priorityColorCoding(element.fields.priority))

    # adding ticket to sprint
    if(sprintName):
      status = sprintName + " # " + status
      mySprints[sprintName].append("%s" % (status))
    else:
      mySprints[NONSPRINT].append("%s" % (status))

    # just show top TOPRECENT tickets
    if(i < TOPRECENT):
      bitbar_header.append("%s" % (status))

    if (str(element.fields.status) not in ('To Do', 'Open', 'New', 'Review', 'Prepare Testing', 'Integration', 'QA', 'Waiting')):
      top_status_bar = str(element.key) + " :: " + str(element.fields.summary)
      if(len(top_status_bar) > STATUSLENGTH):
        top_status_bar = top_status_bar[0:STATUSLENGTH] + '..'

      ###############################################################################
      ## header element
      ####################
      if(bitbar_header[0] == ''):
        bitbar_header[0] = str("%s" % (top_status_bar))
        ## link to that elem
        bitbar_header[2] = str("%s" % (status))
      ###############################################################################

    i = i + 1  
  
  ###############################################################################
  ## SPRINTS
  ####################

  bitbar_header.append("%s" % "---")
  sprintHeader="Sprints: ("+str(len(mySprints))+")"
  bitbar_header.append("%s" % (sprintHeader))
  bitbar_header.append("%s" % "---")
  for sprint in mySprints:
    # add sprint string [sprintname](length)
    sprintString = sprint + "(" + str(len(mySprints[sprint])) + ")"
    bitbar_header.append("%s" % (sprintString))
    # create submenus
    subElement = '\n--'.join(mySprints[sprint])
    subElement = "--" + subElement
    bitbar_header.append("%s" % subElement)
 
  if(bitbar_header[0] == ''):
    bitbar_header[0] = '(-) :: No "In progress" ticket'

  # Assigned tichets
  bitbar_header[0] = f"({len(myIssues)}) ~ {bitbar_header[0]}"


  ###############################################################################
  content = '\n'.join(bitbar_header)
  print(content)
  
  with open(CACHE_FILE, "w+") as f:
    f.write(content)
    f.write("\n---\n")
    f.write("cached\n")
    f.write(time.ctime())
    f.close()

  return (content)

def fallback():
  stored_issues=""
  with open(CACHE_FILE, "r") as f:
    stored_issues = f.read()
  if(len(stored_issues) > 0):
    print(stored_issues)
  else:
    bitbar_header = ['No jira issue (no cache)', '---', 'Connection error!!']
    print ('\n'.join(bitbar_header))  

def main():

  session, server = create_jira_session(SERVER, USER, PASSW)
  if (session is not None):
    issues = []
    try:
      issues_result = search_issues_v3(session, server, assignee)
      issues = issues_result.issues if issues_result else []
    except Exception as e:
      fallback()

    if(len(issues) > 0):
      get_in_progress_item(issues)
    else:
      bitbar_header = ['No jira issue', '---', 'Connection error?']
      print ('\n'.join(bitbar_header))

  else:
    fallback()

   
main()
