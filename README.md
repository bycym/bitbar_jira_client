# bitbar_jira_client


```
pip3 install jira-client
```

Create an API token here for password: 
https://id.atlassian.com/manage/api-tokens


connection:
```py
USER="<jira_user>@email"
PASSW="<jira_api_token>"
SERVER="<jira_server>"
assignee="assignee="+"<username>"
TOPRECENT=10
```

example:
```py
USER="foo.foo@mymail.com"
PASSW="th1s1s4n4p1t0k3n"
SERVER="https://myserver.atlassian.net"
assignee="assignee="+"foo.foo"
TOPRECENT=10
```

if assignee doesn't work then try it with emai:
```py
assignee="assignee="+"foo.foo@mail.com"
```

## TODO: 

* create side the open ticket in different sprint