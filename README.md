# bitbar_jira_client

Working on macos with [bitbar](https://github.com/matryer/bitbar)

![bitbar jira client](/jira-noti.png?raw=true "Optional Title")

Working on linux (popos) with [argos](https://github.com/p-e-w/argos)

![bitbar jira client](/jira-noti_argos.png?raw=true "Optional Title")

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
TOPRECENT=10
```

example:
```py
USER="foo.foo@mymail.com"
PASSW="th1s1s4n4p1t0k3n"
SERVER="https://myserver.atlassian.net"
TOPRECENT=10
```
