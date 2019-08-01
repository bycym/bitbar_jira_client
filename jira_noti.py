#!/usr/bin/env -S PATH="${PATH}:/usr/local/bin" PYTHONIOENCODING=UTF-8 python3
# -*- coding: utf-8 -*-

# <bitbar.title>Jira status</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Aron Benkoczy</bitbar.author>
# <bitbar.author.github>bycym</bitbar.author.github>
# <bitbar.desc>Displays Open jira tickets.</bitbar.desc>
# <bitbar.dependencies>python</bitbar.dependencies>

from collections import Counter
from jira.client import JIRA
import logging
import re
import datetime

bitbar_header = ['BB', '---']
# As some above have stated, using an API token will work (for JIRA Cloud).
# Create an API token here: https://id.atlassian.com/manage/api-tokens
# Use your email address as the username
# Use the token value as the password
USER="<jira_user>@email"
PASSW="<jira_api_token>"
SERVER="<jira_server>"
assignee="assignee="+"<username>"
TOPRECENT=10
# Adjust title length of a ticket in status
STATUSLENGTH=50
# Adjust title length of a ticket in dropdown menu
TICKETLENGTH=80

# Defines a function for connecting to Jira
def connect_jira(log, jira_server, jira_user, jira_password):
  try:
    log.info("Connecting to JIRA: %s" % jira_server)
    jira_options = {'server': jira_server}
    jira = JIRA(options=jira_options, basic_auth=(jira_user, jira_password))
    return jira

  except Exception as e:
    log.error("Failed to connect to JIRA: %s" % e)
    return None

# Get bitbar status
def get_in_progress_item(issues):
  myIssues=[]
  mySprints={}

  # filter out Closed or Blocked items
  for issue in issues:
    if (str(issue.fields.status) not in ('Closed', 'Blocked')):
      myIssues.append(issue);

      if(issue.fields.customfield_10007):
        fieldIndex = 0
        if(len(issue.fields.customfield_10007) > 1):
          fieldIndex = 1
        # store sprint name
        sprintName = re.search('name=(.+?),', str(issue.fields.customfield_10007[fieldIndex])).group(1)
        if(sprintName is not ''):
          mySprints[sprintName] = []

  myIssues.sort(key=lambda x: x.fields.updated, reverse=True)
  dashboard = 'Dashboard | href=' + SERVER + '/secure/Dashboard.jspa'
  recent = 'Recent(' + str(TOPRECENT) + '):'
  bitbar_header = ['', '---', dashboard, '---', recent, '---']

  # TOP RECENT
  i = 0
  for element in myIssues:
    status=""
    sprintName = ''
    if(element.fields.customfield_10007):
      fieldIndex = 0
      if(len(element.fields.customfield_10007) > 1):
        fieldIndex = 1
      try:
        sprintName = re.search('name=(.+?),', str(element.fields.customfield_10007[fieldIndex])).group(1)
      except AttributeError:
        sprintName = ''

    # Create ticket with sprint name if it exsist
    # <ID>(<status>) :: <Title>
    if(sprintName):
      status = status + sprintName + " # " + str(element.key) + "(" + str(element.fields.status) + ") :: " + str(element.fields.summary)
      if(len(status) > TICKETLENGTH):
        status = status[0:TICKETLENGTH] + '..'
      else:
        status = status[0:TICKETLENGTH]
      status = status + " | href=https://cae-hc.atlassian.net/browse/" + str(element.key)
      mySprints[sprintName].append("%s" % (status))
    else:
      status = status + str(element.key) + "(" + str(element.fields.status) + ") :: " + str(element.fields.summary)
      if(len(status) > TICKETLENGTH):
        status = status[0:TICKETLENGTH] + '..'
      else:
        status = status[0:TICKETLENGTH]
      status = status + " | href=https://cae-hc.atlassian.net/browse/" + str(element.key)

    # just show top TOPRECENT tickets
    if(i < TOPRECENT):
      bitbar_header.append("%s" % (status))

    if (str(element.fields.status) not in ('Open')):
      status = str(element.key) + "(" + str(element.fields.status) + ") :: " + str(element.fields.summary)
      if(len(status) > STATUSLENGTH):
        status = status[0:STATUSLENGTH] + '..'
      if(bitbar_header[0] is ''):
        bitbar_header[0] = str("%s" % (status))

    i = i + 1  
  
  # Sprints  
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
 
  if(bitbar_header[0] is ''):
    bitbar_header[0] = '(-) :: No "In progress" ticket'

  print ('\n'.join(bitbar_header))


def main():
  # create logger
  # logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
  # logging.warning('This will get logged to a file')
  log = logging.getLogger(__name__)
  jira = connect_jira(log, SERVER, USER, PASSW)
  issues = jira.search_issues(assignee)
  if(len(issues) > 0):
    get_in_progress_item(issues)
  else:
    bitbar_header = ['No jira issue', '---', 'Connection error?']
    print ('\n'.join(bitbar_header))

main()
