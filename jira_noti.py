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
# for bitbar
# import json

bitbar_header = ['BB', '---']
# As some above have stated, using an API token will work (for JIRA Cloud).
# Create an API token here: https://id.atlassian.com/manage/api-tokens
# Use your email address as the username
# Use the token value as the password
USER="<jira_user>"
PASSW="<jira_api_token>"
SERVER="<jira_server>"

def get_status(status):
    # builders_url = url + 'api/v2/builders'
    # most_recent_build_url = builders_url + '/%s/builds?complete=true&order=-complete_at&limit=1'
    ### For bitbar
  # for builder in builders:
  # status = get_buildbot_status(url, builder)
  # result = parse_buildbot_status(url, status)
  #bitbar_header.append("%s | color=%s href=%s" % (status, 'green' if status else 'red', status))
  bitbar_header = ['BB', '---']
  bitbar_header[0]= str("%s" % (status))
  bitbar_header.append("---")
  bitbar_header.append("%s" % (status))
  print ('\n'.join(bitbar_header))
  ##
# end for bitbar

# Defines a function for connecting to Jira
def connect_jira(log, jira_server, jira_user, jira_password):
  '''
  Connect to JIRA. Return None on error
  '''
  try:
    log.info("Connecting to JIRA: %s" % jira_server)
    jira_options = {'server': jira_server}
    jira = JIRA(options=jira_options, basic_auth=(jira_user, jira_password))
                                      # ^--- Note the tuple
    return jira

  except Exception as e:
    log.error("Failed to connect to JIRA: %s" % e)
    return None

def get_in_progress_item(issues):
  # Find the top three projects containing issues reported by admin
  #top_three = Counter(
  #    [issue.fields.project.key for issue in issues]).most_common(3)
  #print(top_three)
  # Affected version, Assignee, Attachments, Category, Comment, Component, Created, Creator, Custom field, 
  # Customer Request Type, Description, Due, Environment, Epic link, Filter, Fix version, Issue key, Labels, 
  # Last viewed, Level, Original estimate, Parent, Priority, Project, Remaining estimate, Reporter, 
  # Resolution, Resolved, Sprint, Status, Summary, Text, Time spent, Type, Updated, Voter, Votes, Watcher, 
  # Watchers, Work log author, Work log comment, Work log date, Work ratio
  myIssues=[]
  for issue in issues:
    #print(type(issue.fields.status))
    #if (issue.fields.status == issue.fields.):
    #if issue.fields.status not in('Closed','reopen'):
    if (str(issue.fields.status) not in ('Closed', 'Blocked')):
      myIssues.append(issue);
      #print (issue)
      #print (myIssues[-1])
      #print(issue, "(", issue.fields.status, ") :: ", issue.fields.summary)
      #myObject = (issue.fields.updated, issue.key, str(issue.fields.status), issue.fields.summary)
      #print (myObject)
      #toPrint.append(myObject)
      # print("updated: ", issue.fields.updated)
  myIssues.sort(key=lambda x: x.fields.updated, reverse=True)
  bitbar_header = ['BB', '---']
  # print ('\n'.join(bitbar_header))
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
      # AAA, ZZZ not found in the original string
        sprintName = '' # apply your error handling
    if(sprintName):
      status = status + sprintName + " # "
    #if(element.customfield_13000["Sprint"]):
     # status = str(element.customfield_13000["Sprint"]) + " - " + str(element.key) + "(" + str(element.fields.status) + ") :: " + str(element.fields.summary) + " | href=https://cae-hc.atlassian.net/browse/" + str(element.key)  
    #else:
    # print (element.getCustomFieldValue("Sprint"))
    status = status + str(element.key) + "(" + str(element.fields.status) + ") :: " + str(element.fields.summary) + " | href=https://cae-hc.atlassian.net/browse/" + str(element.key)

    bitbar_header.append("%s" % (status))
    if (str(element.fields.status) not in ('Open')):
      status = str(element.key) + "(" + str(element.fields.status) + ") :: " + str(element.fields.summary)
      bitbar_header[0]= str("%s" % (status))
      #print (element)
      #return element
      #print(issue.fields.updated, " - ", element, "(", element.fields.status, ") :: ", element.fields.summary)
      # return (str(element.key) + "(" + str(element.fields.status) + ") :: " + str(element.fields.summary))
  print ('\n'.join(bitbar_header))
  #print(type(issue))
  #property_names=[p for p in dir(Issue) if isinstance(getattr(Issue,p),property)]
  #print(issue.raw)
  # print(issue.fields.customfield_10007[0])
  #print(issue.fields.customfield_10007[1])
  #return myIssues


def main():
  # create logger
  log = logging.getLogger(__name__)


  jira = connect_jira(log, SERVER, USER, PASSW)
  # Find all issues reported by the admin
  issues = jira.search_issues('assignee=aron.benkoczy')
   #print(issues);
  get_in_progress_item(issues)
  # get_status(issue)

main()
