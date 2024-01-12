# gl-gh-migration-script


This is a utility that must be run locally.

# Requirements

You will need to install the following Python libraries. You can install them with the `pip3` command:
`csv`
`request`
`subprocess`

You will need to have `gh` installed: 
`brew install gh`

You will need a GitLab access token with the following privileges:
`api`
`write_repository`
`sudo`
`admin_mode`

You can create your GitLab tokens here: https://git.dartmouth.edu/-/profile/personal_access_tokens

You will need a GitHub personal access token the following privileges:
`admin:enterprise` 
`admin:org`
`admin:org_hook` 
`admin:repo_hook`
`codespace`
`notifications`
`project`
`repo`
`user`
`workflow`
`write:discussion`
`write:packages`

You can create your GitHub tokens here: https://github.com/access/tokens 

You will need to give your GitHub PAT access to the target org in the GitHub web interface by choosing the org you wish to move repositories to in the dropdown menu titled "Configure SSO" for your token.

Once you have your tokens, you can paste them in as the values for `gl_access_token` and `gh_access_token`. Make sure you DO NOT commit these as they are very powerful and we don't want them floating around!

The script assumes that you are using an IDM0X account to run it. The account name will go in as the `username` variable. If you are not using an IDM0X account, you will have to change line 14.

# How to use the script

To migrate repositories from GitLab, you will list the repos in question in the `batch01.csv` file. You will list them in the format 
`group,repo`
with no whitespace after the comma. For example:
`idm,grouper`.
The script will create a mirror copy of the repo locally, create a new repo with the same name in GitHub, push the local copy to the new repo, and then copy over the webhooks if there are any.

If you have any questions go to Rodrigo.