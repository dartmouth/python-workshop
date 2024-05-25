#!/usr/bin/env python3
import os
import sys
import csv
import requests
import json
from dotenv import load_dotenv

load_dotenv()
ghBaseUrl   = "github.com"
gh_username = os.getenv("gh_username")
gh_token    = os.getenv("gh_token")

def artt_one(org, target_repo, admin_team):
  body_params = {
    'permission': 'admin'
  }
  url = f"https://api.github.com/orgs/{org}/teams/{admin_team}/repos/{org}/{target_repo}"
  headers = {
    'Content-Type': 'application/json',
    "Authorization": f"token {gh_token}",
    'X-GitHub-Api-Version': '2022-11-28'
  }
  response = requests.put(url, headers=headers, data=json.dumps(body_params))
  if response.status_code != 204:
    print(f"ERROR: Failed to add repo - {target_repo} to team - {admin_team}. Reason code: {response.status_code}")
  else:
    print(f"Added repo={target_repo} to team={admin_team}")

def artt_batch(batch_file):
  with open(batch_file) as batchfile:
    reader = csv.DictReader(batchfile, delimiter=',')
    for row in reader:
      org         = row['TARGET_ORG']
      target_repo = row['TARGET_REPO']
      admin_teams = row['ADMIN_TEAMS']
      for admin_team in admin_teams.split(':'):
        artt_one(org, target_repo, admin_team)

if __name__ == "__main__":
  artt_batch(sys.argv[1])
