import csv
import requests
import subprocess

### IMPORTANT ###
# Read the README or the Confluence article before you try to use this


https = "https://"
glBaseUrl = "git.dartmouth.edu"
ghBaseUrl = "github.com"
ghTargetOrg = "dartmouth-sandbox"
username = "" # idm0X
gh_username = "git-" + username
gh_token = ""
gl_token = ""
ghVisibility = "--internal" # can also be "private" or "public"

def stripWhitespace(path):
    return path.replace(" ", "-")

def migrateBatch():
    with open("batch01.csv") as batchfile:
        reader = csv.reader(batchfile, delimiter=',')
        for line in reader:
            group = stripWhitespace(line[0])
            repo = stripWhitespace(line[1])
            glSourceRepo = glBaseUrl + "/" + group + "/" + repo
            resp = requests.get(https + glSourceRepo)
            if resp.status_code == 200:
                # create a local mirror, create the repo in GitHub, and push the local mirror
                subprocess.call(["mkdir", repo])
                subprocess.call(["git", "clone", "--mirror", https + username + ":" + gl_token + "@" + glSourceRepo + ".git", repo + "/.git"])
                subprocess.call(["git", "config", "--bool", "core.bare", "false"], cwd="./" + repo)
                subprocess.call(["git", "remote", "set-url", "origin", https + gh_username + ":" + gh_token + "@" + ghBaseUrl + "/" + ghTargetOrg + "/" + repo], cwd="./" + repo)
                subprocess.call(["gh", "repo", "create", ghTargetOrg + "/" + repo, ghVisibility])
                subprocess.call(["git", "push", "--mirror"], cwd="./" + repo)
                
                # add the webhooks if there are any
                webhooks_resp = requests.get(https + glBaseUrl + "/api/v4/projects/" + group + "%2f" + repo + "/hooks", headers={"PRIVATE-TOKEN": gl_token})
                webhooks_content = webhooks_resp.json()
                for webhook in webhooks_content:
                    events = []
                    if webhook["push_events"]:
                        events.append("push")
                    if webhook["merge_requests_events"]:
                        events.append("pull_request")
                    params = {"events": events, "config": {"url": webhook["url"], "content_type": "json"}}
                    headers = {"X-GitHub-Api-Version": "2022-11-28", "Authorization": "Bearer " + gh_token, "Accept": "application/vnd.github+json"}
                    create_wh_resp = requests.post("https://api.github.com/repos/" + ghTargetOrg + "/" + repo + "/hooks", json=params, headers=headers)
                    
                    if create_wh_resp.status_code == 201:
                        print("Webhook created for " + repo)

                # delete files on disk to prevent clutter
                subprocess.call(["rm", "-rf", repo])

migrateBatch()

