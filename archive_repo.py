#!/usr/bin/env python3
import os
import sys
import csv
import gitlab
import json
from dotenv import load_dotenv

load_dotenv()
gl_url = 'https://git.dartmouth.edu'
gl_username = os.getenv("gl_username")
gl_token    = os.getenv("gl_token")
gitlab_projects_file = "gitlab_all_projects.json"

def build_id_file():
  gl = gitlab.Gitlab(gl_url, private_token=gl_token)
  projects = gl.projects.list(all=True)
  project_data = []
  for project in projects:
    project_info = {
      "id": project.id,
      "name": project.name,
      "git_uri": project.ssh_url_to_repo,
      "web_url": project.web_url,
      "visibility": project.visibility,
      'last_activity': project.last_activity_at,
      'members': '',
      "namespace": {
        "owner_type": project.namespace["kind"],
        "owner_name": project.namespace["name"],
        "owner_full_path": project.namespace["full_path"],
        "parent_id": project.namespace["parent_id"],
        "web_url": project.namespace["web_url"]
      }
    }
    project_data.append(project_info)
  with open(gitlab_projects_file, "w") as json_file:
    json.dump(project_data, json_file, default=str, indent=2)

def url_to_id(projects):
  op = {}
  for project in projects:
    op[project['web_url'].strip()] = project['id']
  return op

def archive_batch(batch_file):
  with open(gitlab_projects_file, 'r') as f:
    projects = url_to_id(json.load(f))
  with open(batch_file) as batchfile:
    reader = csv.DictReader(batchfile, delimiter=',')
    for row in reader:
      group       = row['SOURCE_GROUP_NAME']
      source_repo = row['SOURCE_REPO']
      web_url = f"{gl_url}/{group}/{source_repo}"
      archive_one(web_url, projects[web_url])

def archive_one(web_url, repo_id):
  gl = gitlab.Gitlab(gl_url, private_token=gl_token)
  try:
    project = gl.projects.get(repo_id)
    project.archive()
    print(f"- '{web_url}' = '{project.name}' archived successfully.")
  except Exception as e:
    print(f"- '{web_url}' archival failed: {repr(e)}")

if __name__ == "__main__":
  if sys.argv[1] == "--build_id_file":
    build_id_file()
  else:
    archive_batch(sys.argv[1])