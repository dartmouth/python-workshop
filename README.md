## Initial setup

Create the following credentials (details below)
- GitLab username and access token
- GitHub username and access token

Then save these credentials to a dotenv file

```sh
cat << 'EOF' > .env
gl_username = "rc-github01"
gh_username = "rc-github01"
gl_token = "glpat-abcdefghijklmnopqrst"
gh_token = "ghp_abcdefghijklmnopqrstuvwxyz1234567890"
EOF
```

Then install the `gh` command line tool and setup your Python virtualenv.

```sh
brew install gh

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Prepare for a migration

Activate the virtualenv and then create a batch01.csv

```sh
source venv/bin/activate

cat << 'EOF' > batch01.csv
SOURCE_GROUP_NAME,SOURCE_REPO,TARGET_VISIBILITY,TARGET_ORG,TARGET_REPO
rci,docs,internal,dartmouth-itc,rci-docs
EOF
```

## Run the migration

```sh
# copy from GitLab to GitHub
./migrate.py batch01.csv

# in GitHub, grant teams admin access
./add_repos_to_teams batch01.csv

# in GitLab, archive the repos
./archive_repo.py batch01.csv
```

Note: if you are archiving recently created repos, you may need to rebuild the database file that matches projects to id. The following will do that.

```sh
./archive_repo.py --build_id_file
```

## Notes from the Kemeny Team about creating tokens

You can create your GitLab tokens here: https://git.dartmouth.edu/-/profile/personal_access_tokens. You will need a GitLab access token with the following privileges:
`api`
`write_repository`
`sudo`
`admin_mode`

You can create your GitHub tokens here: https://github.com/settings/tokens. You will need a GitHub personal access token the following privileges:
`repo`
`workflow`
`write:packages`
`admin:org`
`admin:repo_hook`
`admin:org_hook`
`notifications`
`user`
`write:discussion`
`admin:enterprise`
`codespace`
`project`

You will need to give your GitHub PAT access to the target org in the GitHub web interface by choosing the org you wish to move repositories to in the dropdown menu titled "Configure SSO" for your token.
