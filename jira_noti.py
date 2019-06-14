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

  # filter out Closed or Blocked items
  for issue in issues:
    if (str(issue.fields.status) not in ('Closed', 'Blocked')):
      myIssues.append(issue);

  myIssues.sort(key=lambda x: x.fields.updated, reverse=True)
  recent = 'Recent(' + str(TOPRECENT) + '):'
  bitbar_header = ['BB', '---', recent, '---']

  i = 0
  for element in myIssues:
    if(i >= TOPRECENT):
      break
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
    if(sprintName):
      status = status + sprintName + " # "

    status = status + str(element.key) + "(" + str(element.fields.status) + ") :: " + str(element.fields.summary) + " | href=https://cae-hc.atlassian.net/browse/" + str(element.key)

    bitbar_header.append("%s" % (status))
    if (str(element.fields.status) not in ('Open')):
      status = str(element.key) + "(" + str(element.fields.status) + ") :: " + str(element.fields.summary)
      bitbar_header[0]= str("%s" % (status))

    i = i + 1  
  print ('\n'.join(bitbar_header))

def main():
  log = logging.getLogger(__name__)
  jira = connect_jira(log, SERVER, USER, PASSW)
  issues = jira.search_issues(assignee)
  if(len(issues) > 0):
    get_in_progress_item(issues)

main()
