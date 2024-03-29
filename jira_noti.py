#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# <bitbar.title>Jira status</bitbar.title>
# <bitbar.version>v1.3</bitbar.version>
# <bitbar.author>Aron Benkoczy</bitbar.author>
# <bitbar.author.github>bycym</bitbar.author.github>
# <bitbar.desc>Displays Open jira tickets.</bitbar.desc>
# <bitbar.dependencies>python</bitbar.dependencies>

from collections import Counter
from jira.client import JIRA
import logging
import re
import datetime
import time
import os
import json

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
STATUSLENGTH=30
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
  ## <<<<< Custom header link

# color option for the priority
def priorityColorCoding(priority):
  priorityColor = " color="
  if(str(priority) == "Blocker"):
    priorityColor = priorityColor + "#cc3300"
  elif (str(priority) == "Critical"):
    priorityColor = priorityColor + "#ff9999"
  elif (str(priority) == "Major"):
    priorityColor = priorityColor + "#ff0000"
  elif (str(priority) == "Minor"):
    priorityColor = priorityColor + "#808080"
  elif (str(priority) == "Trivial"):
    priorityColor = priorityColor + "#808080"
  else:
    priorityColor = ""
  return priorityColor

### END OF THE CUSTOM SECTION ###


# Defines a function for connecting to Jira
def connect_jira(log, jira_server, jira_user, jira_password):
  try:
    log.info("Connecting to JIRA: %s" % jira_server)
    jira_options = {'server': jira_server}
    jira = JIRA(timeout=TIME_OUT, options=jira_options, basic_auth=(jira_user, jira_password), max_retries=0)
    return jira

  except Exception as e:
    log.error("Failed to connect to JIRA: %s" % e)
    return None

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
  ## add more custom link
  add_custom_header(bitbar_header)

  ###############################################################################

  # filter out Closed or Blocked items
  for issue in issues:
    if (str(issue.fields.status) not in ('Closed', 'Blocked', 'Done', 'QA')):
      myIssues.append(issue);
      sprintName = ''
      if(issue.fields.customfield_10004):
        fieldIndex = 0
        if(len(issue.fields.customfield_10004) > 1):
          fieldIndex = 1
        # get sprint name
        if (issue.raw['fields']["customfield_10004"] and issue.raw['fields']["customfield_10004"][0]['name']):
          sprintName = issue.raw['fields']["customfield_10004"][0]['name']
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
    sprintName = ''
    if(element.fields.customfield_10004):
      fieldIndex = 0
      if(len(element.fields.customfield_10004) > 1):
        fieldIndex = 1
      try:
        sprintName = element.raw['fields']["customfield_10004"][0]['name']
      except AttributeError:
        sprintName = ''

    # Create ticket with sprint name if it exsist
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


def getParsedIssues():
  log = logging.getLogger(__name__)
  jira = connect_jira(log, SERVER, USER, PASSW)
  log = ""
  if ( jira is not None):
    issues = jira.search_issues(assignee)
    if(len(issues) > 0):
      log = get_in_progress_item(issues)
    else:
      bitbar_header = ['No jira issue', '---', 'Connection error?']
      log = ('\n'.join(bitbar_header))

    issues2 = jira.search_issues('assignee was in (currentuser()) and updatedDate < endOfDay() AND updatedDate > -1d ORDER BY updatedDate DESC, created ASC',fields=['key', 'project', 'timeSpent', 'worklog'], maxResults=30)
    if(len(issues2) > 0):
      log = log + get_time_spent_by_day(issues2)
  return log

def get_time_spent_by_day(issues):
  i = 0
  today_time_spent = []
  today_time_spent.append("%s" % ('--'))
  today_time_spent.append("%s" % ('Today logged:'))
  today_time_spent.append("%s" % ('--'))

  yesterday_time_spent = []
  yesterday_time_spent.append("%s" % ('--'))
  yesterday_time_spent.append("%s" % ('Yesterday logged:'))
  yesterday_time_spent.append("%s" % ('--'))
  for issue in issues:
    log_entry_count = len(issue.fields.worklog.worklogs)
    for i in range(log_entry_count):
      issue_strd = issue.fields.worklog.worklogs[i].updated
      issue_strd = issue_strd[0:issue_strd.find("+")]
      issue_d = datetime.datetime.strptime(issue_strd, '%Y-%m-%dT%H:%M:%S.%f')

      comment=''
      if hasattr(issue.fields.worklog.worklogs[i], 'comment'):
        comment = issue.fields.worklog.worklogs[i].comment
      status = "[" + str(issue.fields.worklog.worklogs[i].updateAuthor) + "] " + str(issue.key) + " :: " + str(issue.fields.worklog.worklogs[i].timeSpent) + " - " + str(comment)

      if(len(status) > TICKETLENGTH):
        status = status[0:TICKETLENGTH] + '..'
      else:
        status = status[0:TICKETLENGTH]
      status = status + " | href=" + SERVER + "/browse/" + str(element.key)
      if(issue_d.day == datetime.date.today().day):
        today_time_spent.append("%s" % (status))

      yesterday_d = datetime.datetime.strptime( ((datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')), '%Y-%m-%d' )
      if(issue_d.day == yesterday_d.day):
        yesterday_time_spent.append("%s" % (status))
    # return
  content = '\n'.join(today_time_spent) + '\n'.join(yesterday_time_spent)
  print(content)
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

  log = logging.getLogger(__name__)
  jira = connect_jira(log, SERVER, USER, PASSW)
  if ( jira is not None):
    issues = []
    try:
      issues = jira.search_issues(assignee)
    except Exception as e:
      fallback()

    if(len(issues) > 0):
      get_in_progress_item(issues)
    else:
      bitbar_header = ['No jira issue', '---', 'Connection error?']
      print ('\n'.join(bitbar_header))

    issues2 = []
    try:
      issues2 = jira.search_issues('assignee was in (currentuser()) and updatedDate < endOfDay() AND updatedDate > -1d ORDER BY updatedDate DESC, created ASC',fields=['key', 'project', 'timeSpent', 'worklog'], maxResults=30)
    except Exception as e:
      issues2 = []
    if(len(issues2) > 0):
      get_time_spent_by_day(issues2)

  else:
    fallback()

   
main()

