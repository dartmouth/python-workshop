#!/usr/bin/env python3
import os
import sys
import csv
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()
glBaseUrl   = "git.dartmouth.edu"
ghBaseUrl   = "github.com"
gl_username = os.getenv("gl_username")
gh_username = os.getenv("gh_username")
gl_token    = os.getenv("gl_token")
gh_token    = os.getenv("gh_token")
os.environ["GITHUB_TOKEN"] = gh_token
os.environ["GH_TOKEN"]     = gh_token

def migrate_batch(batch_file):
  with open(batch_file) as batchfile:
    reader = csv.DictReader(batchfile, delimiter=',')
    for row in reader:
      group       = row['SOURCE_GROUP_NAME']
      source_repo = row['SOURCE_REPO']
      visibility  = row['TARGET_VISIBILITY']
      org         = row['TARGET_ORG']
      target_repo = row['TARGET_REPO']
      migrate_one(group, source_repo, visibility, org, target_repo)

def migrate_one(group, source_repo, visibility, org, target_repo):
  glSourceRepo = f"{glBaseUrl}/{group}/{source_repo}"
  resp = requests.get(f"https://{glSourceRepo}")
  if resp.status_code == 200:
    # create a local mirror, create the repo in GitHub, and push the local mirror
    subprocess.call(["mkdir", source_repo])
    subprocess.call(["git", "clone", "--mirror", f"https://{gl_username}:{gl_token}@{glSourceRepo}.git", source_repo + "/.git"])
    subprocess.call(["git", "config", "--bool", "core.bare", "false"], cwd="./" + source_repo)
    subprocess.call(["git", "remote", "set-url", "origin", f"https://{gh_username}:{gh_token}@{ghBaseUrl}/{org}/{target_repo}"], cwd="./" + source_repo)
    subprocess.call(["gh", "repo", "create", org + "/" + target_repo, "--" + visibility])
    subprocess.call(["git", "push", "--mirror"], cwd="./" + source_repo)
    # add the webhooks if there are any
    webhooks_resp = requests.get(f"https://{glBaseUrl}/api/v4/projects/{group}%2f{source_repo}/hooks", headers={"PRIVATE-TOKEN": gl_token})
    webhooks_content = webhooks_resp.json()
    for webhook in webhooks_content:
      events = []
      if webhook["push_events"]:
        events.append("push")
      if webhook["merge_requests_events"]:
        events.append("pull_request")
      params = {"events": events, "config": {"url": webhook["url"], "content_type": "json"}}
      headers = {"X-GitHub-Api-Version": "2022-11-28", "Authorization": "Bearer " + gh_token, "Accept": "application/vnd.github+json"}
      create_wh_resp = requests.post(f"https://api.github.com/repos/{org}/{target_repo}/hooks", json=params, headers=headers)
      if create_wh_resp.status_code == 201:
        print(f"Webhook created for {target_repo}")
    # delete files on disk to prevent clutter
    subprocess.call(["rm", "-rf", source_repo])
    print(f" - Source: https://{glSourceRepo}")
    print(f" - Target: https://{ghBaseUrl}/{org}/{target_repo}")

if __name__ == "__main__":
  migrate_batch(sys.argv[1])