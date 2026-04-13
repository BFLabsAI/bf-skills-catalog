---
name: github-ops
description: Unified GitHub operations skill covering git commit workflows (conventional commits, staging, message generation), GitHub CLI (gh) for repos, issues, PRs, Actions, releases, gists, codespaces, and more, plus README creation best practices.
version: 1.0.0
tags: [git, github, gh-cli, commits, pull-requests, issues, actions, releases, readme]
license: MIT
allowed-tools: Bash
---

# GitHub Operations

Unified skill covering three domains: git commit workflows, GitHub CLI (gh), and README creation.

---

## Part 1: Git Commit with Conventional Commits

### Conventional Commit Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

| Type       | Purpose                        |
| ---------- | ------------------------------ |
| `feat`     | New feature                    |
| `fix`      | Bug fix                        |
| `docs`     | Documentation only             |
| `style`    | Formatting/style (no logic)    |
| `refactor` | Code refactor (no feature/fix) |
| `perf`     | Performance improvement        |
| `test`     | Add/update tests               |
| `build`    | Build system/dependencies      |
| `ci`       | CI/config changes              |
| `chore`    | Maintenance/misc               |
| `revert`   | Revert commit                  |

### Breaking Changes

```bash
# Exclamation mark notation
feat!: remove deprecated endpoint

# BREAKING CHANGE footer
feat: allow config to extend other configs

BREAKING CHANGE: `extends` key behavior changed
```

### Commit Workflow

**Step 1 — Analyze diff**

```bash
# If files are staged
git diff --staged

# If nothing staged, check working tree
git diff

# Check status
git status --porcelain
```

**Step 2 — Stage files (if needed)**

```bash
# Stage specific files
git add path/to/file1 path/to/file2

# Stage by pattern
git add *.test.*
git add src/components/*

# Interactive staging
git add -p
```

Never commit secrets (.env, credentials.json, private keys).

**Step 3 — Generate commit message**

Analyze the diff to determine:
- **Type**: What kind of change is this?
- **Scope**: What area/module is affected?
- **Description**: One-line summary (present tense, imperative mood, <72 chars)

**Step 4 — Execute commit**

```bash
# Single line
git commit -m "<type>[scope]: <description>"

# Multi-line with body/footer
git commit -m "$(cat <<'EOF'
<type>[scope]: <description>

<optional body>

<optional footer>
EOF
)"
```

### Commit Best Practices

- One logical change per commit
- Present tense: "add" not "added"
- Imperative mood: "fix bug" not "fixes bug"
- Reference issues: `Closes #123`, `Refs #456`
- Keep description under 72 characters

### Git Safety Protocol

- NEVER update git config
- NEVER run destructive commands (--force, hard reset) without explicit user request
- NEVER skip hooks (--no-verify) unless the user explicitly asks
- NEVER force push to main/master
- If a commit fails due to a hook, fix the issue and create a NEW commit — do not amend

---

## Part 2: GitHub CLI (gh)

**Version:** 2.85.0 (current as of January 2026)

### Installation

```bash
# macOS
brew install gh

# Linux (Debian/Ubuntu)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh

# Windows
winget install --id GitHub.cli

# Verify
gh --version
```

### Authentication

```bash
# Interactive login
gh auth login

# Web-based
gh auth login --web

# With specific git protocol
gh auth login --git-protocol ssh

# GitHub Enterprise
gh auth login --hostname enterprise.internal

# Token from stdin
gh auth login --with-token < token.txt

# Check status
gh auth status
gh auth status --active
gh auth status --show-token

# Switch accounts
gh auth switch --hostname github.com --user monalisa

# View active token
gh auth token

# Refresh scopes
gh auth refresh --scopes write:org,read:public_key
gh auth refresh --remove-scopes delete_repo
gh auth refresh --reset-scopes

# Setup git credential helper
gh auth setup-git
gh auth setup-git --hostname enterprise.internal --force

# Logout
gh auth logout --hostname github.com --user username
```

### Environment Variables

```bash
export GH_TOKEN=ghp_xxxxxxxxxxxx       # GitHub token (for automation)
export GH_HOST=github.com              # GitHub hostname
export GH_PROMPT_DISABLED=true         # Disable prompts
export GH_EDITOR=vim                   # Custom editor
export GH_PAGER=less                   # Custom pager
export GH_TIMEOUT=30                   # HTTP timeout
export GH_REPO=owner/repo              # Override default repository
export GH_ENTERPRISE_HOSTNAME=hostname # Enterprise hostname
```

### Global Flags

| Flag                       | Description                            |
| -------------------------- | -------------------------------------- |
| `--help` / `-h`            | Show help for command                  |
| `--version`                | Show gh version                        |
| `--repo [HOST/]OWNER/REPO` | Select another repository              |
| `--hostname HOST`          | GitHub hostname                        |
| `--jq EXPRESSION`          | Filter JSON output                     |
| `--json FIELDS`            | Output JSON with specified fields      |
| `--template STRING`        | Format JSON using Go template          |
| `--web`                    | Open in browser                        |
| `--paginate`               | Make additional API calls              |
| `--verbose`                | Show verbose output                    |
| `--debug`                  | Show debug output                      |
| `--timeout SECONDS`        | Maximum API request duration           |
| `--cache CACHE`            | Cache control (default, force, bypass) |

### Configuration

```bash
gh config list
gh config get editor
gh config set editor vim
gh config set git_protocol ssh
gh config set prompt disabled
gh config set pager "less -R"
gh config clear-cache
```

### Browse

```bash
gh browse                                # Open repo in browser
gh browse script/                        # Open specific path
gh browse main.go:312                    # Open file at line
gh browse 123                            # Open issue or PR
gh browse 77507cd94ccafcf568f8560cfecde965fcfa63  # Open commit
gh browse main.go --branch bug-fix
gh browse --repo owner/repo
gh browse --actions
gh browse --projects
gh browse --releases
gh browse --settings
gh browse --wiki
gh browse --no-browser                   # Print URL instead of opening
```

---

### Repositories (gh repo)

```bash
# Create
gh repo create my-repo --public --description "My project"
gh repo create my-repo --private
gh repo create my-repo --license mit --gitignore python
gh repo create my-repo --homepage https://example.com
gh repo create my-repo --disable-issues --disable-wiki
gh repo create org/my-repo              # In organization
gh repo create my-repo --source=.       # No local clone

# Clone
gh repo clone owner/repo
gh repo clone owner/repo my-directory
gh repo clone owner/repo --branch develop

# List
gh repo list
gh repo list owner --limit 50 --public --source
gh repo list --json name,visibility,owner
gh repo list --json name --jq '.[].name'

# View
gh repo view
gh repo view owner/repo
gh repo view --json name,description,defaultBranchRef
gh repo view --web

# Edit
gh repo edit --description "New description"
gh repo edit --homepage https://example.com
gh repo edit --visibility private
gh repo edit --enable-issues
gh repo edit --disable-wiki
gh repo edit --default-branch main
gh repo rename new-name
gh repo archive
gh repo unarchive

# Delete
gh repo delete owner/repo --yes

# Fork
gh repo fork owner/repo
gh repo fork owner/repo --org org-name --clone --remote-name upstream

# Sync fork
gh repo sync
gh repo sync --branch feature --force

# Set default
gh repo set-default owner/repo
gh repo set-default --unset

# Autolinks
gh repo autolink list
gh repo autolink add --key-prefix JIRA- --url-template https://jira.example.com/browse/<num>
gh repo autolink delete 12345

# Deploy keys
gh repo deploy-key list
gh repo deploy-key add ~/.ssh/id_rsa.pub --title "Production server" --read-only
gh repo deploy-key delete 12345

# Templates
gh repo gitignore
gh repo license mit
gh repo license mit --fullname "John Doe"
```

---

### Issues (gh issue)

```bash
# Create
gh issue create
gh issue create --title "Bug: Login not working" --body "Steps to reproduce..."
gh issue create --body-file issue.md
gh issue create --title "Fix bug" --labels bug,high-priority
gh issue create --title "Fix bug" --assignee user1,user2
gh issue create --repo owner/repo --title "Issue title"
gh issue create --web

# List
gh issue list
gh issue list --state all
gh issue list --state closed
gh issue list --limit 50
gh issue list --assignee @me
gh issue list --labels bug,enhancement
gh issue list --milestone "v1.0"
gh issue list --search "is:open is:issue label:bug"
gh issue list --json number,title,state,author
gh issue list --sort created --order desc

# View
gh issue view 123
gh issue view 123 --comments
gh issue view 123 --web
gh issue view 123 --json title,body,state,labels,comments
gh issue view 123 --json title --jq '.title'

# Edit
gh issue edit 123 --title "New title" --body "New description"
gh issue edit 123 --add-label bug,high-priority
gh issue edit 123 --remove-label stale
gh issue edit 123 --add-assignee user1,user2
gh issue edit 123 --remove-assignee user1
gh issue edit 123 --milestone "v1.0"

# Close / Reopen
gh issue close 123 --comment "Fixed in PR #456"
gh issue reopen 123

# Comment
gh issue comment 123 --body "This looks good!"
gh issue comment 123 --edit 456789 --body "Updated comment"
gh issue comment 123 --delete 456789

# Status
gh issue status
gh issue status --repo owner/repo

# Pin / Lock / Transfer / Delete
gh issue pin 123
gh issue unpin 123
gh issue lock 123 --reason off-topic
gh issue unlock 123
gh issue transfer 123 --repo owner/new-repo
gh issue delete 123 --yes

# Create draft PR from issue
gh issue develop 123
gh issue develop 123 --branch fix/issue-123 --base main
```

---

### Pull Requests (gh pr)

```bash
# Create
gh pr create
gh pr create --title "Feature: Add new functionality" --body "This PR adds..."
gh pr create --body-file .github/PULL_REQUEST_TEMPLATE.md
gh pr create --base main --head feature-branch
gh pr create --draft
gh pr create --assignee user1,user2 --reviewer user1,user2
gh pr create --labels enhancement,feature
gh pr create --issue 123
gh pr create --repo owner/repo --web

# List
gh pr list
gh pr list --state all
gh pr list --state merged
gh pr list --state closed
gh pr list --head feature-branch --base main
gh pr list --author @me
gh pr list --assignee username
gh pr list --labels bug,enhancement
gh pr list --limit 50
gh pr list --search "is:open is:pr label:review-required"
gh pr list --json number,title,state,author,headRefName
gh pr list --sort created --order desc

# View
gh pr view 123
gh pr view 123 --comments
gh pr view 123 --web
gh pr view 123 --json title,body,state,author,commits,files
gh pr view 123 --json title,state --jq '"\(.title): \(.state)"'

# Checkout
gh pr checkout 123
gh pr checkout 123 --branch name-123 --force

# Diff
gh pr diff 123
gh pr diff 123 --color always
gh pr diff 123 --name-only
gh pr diff 123 > pr-123.patch

# Merge
gh pr merge 123
gh pr merge 123 --merge
gh pr merge 123 --squash
gh pr merge 123 --rebase
gh pr merge 123 --delete-branch
gh pr merge 123 --subject "Merge PR #123" --body "Merging feature"
gh pr merge 123 --admin   # Force merge / bypass checks

# Close / Reopen
gh pr close 123 --comment "Closing due to..."
gh pr reopen 123

# Edit
gh pr edit 123 --title "New title" --body "New description"
gh pr edit 123 --add-label bug,enhancement
gh pr edit 123 --remove-label stale
gh pr edit 123 --add-assignee user1,user2
gh pr edit 123 --remove-assignee user1
gh pr edit 123 --add-reviewer user1,user2
gh pr edit 123 --remove-reviewer user1
gh pr edit 123 --ready

# Ready for review
gh pr ready 123

# Checks
gh pr checks 123
gh pr checks 123 --watch --interval 5

# Comment
gh pr comment 123 --body "Looks good!"
gh pr comment 123 --edit 456789 --body "Updated"
gh pr comment 123 --delete 456789

# Review
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "Please fix these issues"
gh pr review 123 --comment --body "Some thoughts..."
gh pr review 123 --dismiss

# Update branch
gh pr update-branch 123
gh pr update-branch 123 --force --merge

# Lock / Unlock
gh pr lock 123 --reason off-topic
gh pr unlock 123

# Revert
gh pr revert 123
gh pr revert 123 --branch revert-pr-123

# Status
gh pr status
gh pr status --repo owner/repo
```

---

### GitHub Actions

**Workflow Runs (gh run)**

```bash
gh run list
gh run list --workflow "ci.yml" --branch main --limit 20
gh run list --json databaseId,status,conclusion,headBranch

gh run view 123456789
gh run view 123456789 --log
gh run view 123456789 --job 987654321
gh run view 123456789 --web

gh run watch 123456789
gh run watch 123456789 --interval 5

gh run rerun 123456789
gh run rerun 123456789 --job 987654321

gh run cancel 123456789
gh run delete 123456789

gh run download 123456789
gh run download 123456789 --name build --dir ./artifacts
```

**Workflows (gh workflow)**

```bash
gh workflow list
gh workflow view ci.yml
gh workflow view ci.yml --yaml --web

gh workflow enable ci.yml
gh workflow disable ci.yml

gh workflow run ci.yml
gh workflow run ci.yml --raw-field version="1.0.0" environment="production"
gh workflow run ci.yml --ref develop
```

**Action Caches (gh cache)**

```bash
gh cache list
gh cache list --branch main --limit 50
gh cache delete 123456789
gh cache delete --all
```

**Secrets (gh secret)**

```bash
gh secret list
gh secret set MY_SECRET
echo "$MY_SECRET" | gh secret set MY_SECRET
gh secret set MY_SECRET --env production
gh secret set MY_SECRET --org orgname
gh secret delete MY_SECRET
gh secret delete MY_SECRET --env production
```

**Variables (gh variable)**

```bash
gh variable list
gh variable set MY_VAR "some-value"
gh variable set MY_VAR "value" --env production
gh variable set MY_VAR "value" --org orgname
gh variable get MY_VAR
gh variable delete MY_VAR
gh variable delete MY_VAR --env production
```

---

### Projects (gh project)

```bash
gh project list
gh project list --owner owner --open
gh project view 123
gh project view 123 --format json --web
gh project create --title "My Project"
gh project create --title "Project" --org orgname --readme "Description here"
gh project edit 123 --title "New Title"
gh project delete 123
gh project close 123
gh project copy 123 --owner target-owner --title "Copy"
gh project mark-template 123

# Fields
gh project field-list 123
gh project field-create 123 --title "Status" --datatype single_select
gh project field-delete 123 --id 456

# Items
gh project item-list 123
gh project item-create 123 --title "New item"
gh project item-add 123 --owner-owner --repo repo --issue 456
gh project item-edit 123 --id 456 --title "Updated title"
gh project item-delete 123 --id 456
gh project item-archive 123 --id 456

# Links
gh project link 123 --id 456 --link-id 789
gh project unlink 123 --id 456 --link-id 789
```

---

### Releases (gh release)

```bash
gh release list
gh release view
gh release view v1.0.0
gh release view v1.0.0 --web

gh release create v1.0.0 --notes "Release notes here"
gh release create v1.0.0 --notes-file notes.md
gh release create v1.0.0 --target main
gh release create v1.0.0 --draft
gh release create v1.0.0 --prerelease
gh release create v1.0.0 --title "Version 1.0.0"

gh release upload v1.0.0 ./file.tar.gz
gh release upload v1.0.0 ./file1.tar.gz ./file2.tar.gz

gh release delete v1.0.0 --yes
gh release delete-asset v1.0.0 file.tar.gz

gh release download v1.0.0
gh release download v1.0.0 --pattern "*.tar.gz"
gh release download v1.0.0 --dir ./downloads
gh release download v1.0.0 --archive zip

gh release edit v1.0.0 --notes "Updated notes"
gh release verify v1.0.0
gh release verify-asset v1.0.0 file.tar.gz
```

---

### Gists (gh gist)

```bash
gh gist list
gh gist list --public --limit 20
gh gist view abc123
gh gist view abc123 --files

gh gist create script.py
gh gist create script.py --desc "My script" --public
gh gist create file1.py file2.py
echo "print('hello')" | gh gist create

gh gist edit abc123
gh gist delete abc123
gh gist rename abc123 --filename old.py new.py

gh gist clone abc123
gh gist clone abc123 my-directory
```

---

### Codespaces (gh codespace)

```bash
gh codespace list
gh codespace create
gh codespace create --repo owner/repo --branch develop --machine premiumLinux
gh codespace view

gh codespace ssh
gh codespace ssh --command "cd /workspaces && ls"

gh codespace code
gh codespace code --codec                 # Open in VS Code
gh codespace code --path /workspaces/repo

gh codespace stop
gh codespace delete
gh codespace rebuild
gh codespace edit --machine standardLinux

gh codespace logs
gh codespace ports
gh codespace cp 8080:8080                 # Forward port
gh codespace jupyter

gh codespace cp file.txt :/workspaces/file.txt
gh codespace cp :/workspaces/file.txt ./file.txt
```

---

### Organizations (gh org)

```bash
gh org list
gh org list --user username
gh org list --json login,name,description
gh org view orgname
gh org view orgname --json members --jq '.members[] | .login'
```

---

### Search (gh search)

```bash
gh search code "TODO"
gh search code "TODO" --repo owner/repo --extension py
gh search commits "fix bug"
gh search issues "label:bug state:open"
gh search prs "is:open is:pr review:required" --web
gh search repos "stars:>1000 language:python"
gh search repos "topic:api" --limit 50
gh search repos "stars:>100" --json name,description,stargazers
gh search repos "language:rust" --order desc --sort stars
```

---

### Labels (gh label)

```bash
gh label list
gh label create bug --color "d73a4a" --description "Something isn't working"
gh label create enhancement --color "#a2eeef"
gh label edit bug --name "bug-report" --color "ff0000"
gh label delete bug
gh label clone owner/repo
gh label clone owner/repo --repo target/repo
```

---

### SSH Keys (gh ssh-key)

```bash
gh ssh-key list
gh ssh-key add ~/.ssh/id_rsa.pub --title "My laptop"
gh ssh-key add ~/.ssh/id_ed25519.pub --type "authentication"
gh ssh-key delete 12345
gh ssh-key delete --title "My laptop"
```

---

### GPG Keys (gh gpg-key)

```bash
gh gpg-key list
gh gpg-key add ~/.ssh/id_rsa.pub
gh gpg-key delete 12345
gh gpg-key delete ABCD1234
```

---

### Status (gh status)

```bash
gh status
gh status --repo owner/repo
gh status --json
```

---

### Extensions (gh extension)

```bash
gh extension list
gh extension search github
gh extension install owner/extension-repo
gh extension install owner/extension-repo --branch develop
gh extension upgrade extension-name
gh extension remove extension-name
gh extension create my-extension
gh extension browse
gh extension exec my-extension --arg value
```

---

### Aliases (gh alias)

```bash
gh alias list
gh alias set prview 'pr view --web'
gh alias set co 'pr checkout' --shell
gh alias delete prview
gh alias import ./aliases.sh
```

---

### API Requests (gh api)

```bash
# REST
gh api /user
gh api --method POST /repos/owner/repo/issues \
  --field title="Issue title" \
  --field body="Issue body"
gh api /user --header "Accept: application/vnd.github.v3+json"
gh api /user/repos --paginate
gh api /user --raw
gh api /user --include
gh api /user --silent
gh api --input request.json
gh api /user --jq '.login'
gh api /repos/owner/repo --jq '.stargazers_count'
gh api /user --hostname enterprise.internal

# GraphQL
gh api graphql -f query='
{
  viewer {
    login
    repositories(first: 5) {
      nodes { name }
    }
  }
}'
```

---

### Rulesets (gh ruleset)

```bash
gh ruleset list
gh ruleset view 123
gh ruleset check --branch feature
gh ruleset check --repo owner/repo --branch main
```

---

### Attestations (gh attestation)

```bash
gh attestation download owner/repo --artifact-id 123456
gh attestation verify owner/repo
gh attestation trusted-root
```

---

### Shell Completion

```bash
gh completion -s bash > ~/.gh-complete.bash
gh completion -s zsh > ~/.gh-complete.zsh
gh completion -s fish > ~/.gh-complete.fish
gh completion -s powershell > ~/.gh-complete.ps1
```

---

### Agent Tasks (gh agent-task)

```bash
gh agent-task list
gh agent-task view 123
gh agent-task create --description "My task"
```

---

### Output Formatting

```bash
# JSON
gh repo view --json name,description
gh repo view --json owner,name --jq '.owner.login + "/" + .name'
gh pr list --json number,title --jq '.[] | select(.number > 100)'
gh issue list --json number,title,labels \
  --jq '.[] | {number, title: .title, tags: [.labels[].name]}'

# Go templates
gh repo view --template '{{.name}}: {{.description}}'
gh pr view 123 --template 'Title: {{.title}}
Author: {{.author.login}}
State: {{.state}}'
```

---

### Common Workflows

**Create PR from Issue**

```bash
gh issue develop 123 --branch feature/issue-123
git add . && git commit -m "Fix issue #123" && git push
gh pr create --title "Fix #123" --body "Closes #123"
```

**Bulk Operations**

```bash
# Close all stale issues
gh issue list --search "label:stale" --json number --jq '.[].number' | \
  xargs -I {} gh issue close {} --comment "Closing as stale"

# Add label to multiple PRs
gh pr list --search "review:required" --json number --jq '.[].number' | \
  xargs -I {} gh pr edit {} --add-label needs-review
```

**Repository Setup**

```bash
gh repo create my-project --public \
  --description "My awesome project" \
  --clone \
  --gitignore python \
  --license mit

cd my-project
git checkout -b develop && git push -u origin develop

gh label create bug --color "d73a4a" --description "Bug report"
gh label create enhancement --color "a2eeef" --description "Feature request"
gh label create documentation --color "0075ca" --description "Documentation"
```

**CI/CD Workflow**

```bash
RUN_ID=$(gh workflow run ci.yml --ref main --jq '.databaseId')
gh run watch "$RUN_ID"
gh run download "$RUN_ID" --dir ./artifacts
```

**Fork Sync**

```bash
gh repo fork original/repo --clone
cd repo
git remote add upstream https://github.com/original/repo.git
gh repo sync
```

---

### gh Best Practices

1. Use `GH_TOKEN` env var for automation instead of interactive auth.
2. Set a default repo with `gh repo set-default owner/repo` to avoid repetition.
3. Use `--json` + `--jq` for data extraction in scripts.
4. Use `--paginate` for large result sets: `gh issue list --state all --paginate`
5. Use `--cache force` for frequently accessed, rarely-changing data.

### Shell Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
eval "$(gh completion -s bash)"  # or zsh/fish
alias gs='gh status'
alias gpr='gh pr view --web'
alias gir='gh issue view --web'
alias gco='gh pr checkout'
```

### Getting Help

```bash
gh --help
gh pr --help
gh issue create --help
gh help formatting
gh help environment
gh help exit-codes
```

### References

- Official Manual: https://cli.github.com/manual/
- GitHub Docs: https://docs.github.com/en/github-cli
- REST API: https://docs.github.com/en/rest
- GraphQL API: https://docs.github.com/en/graphql

---

## Part 3: README Creation

### Role

Act as a senior software engineer with extensive open source experience. README files must be appealing, informative, and easy to read.

### Task

1. Review the entire project and workspace before writing.
2. Create a comprehensive, well-structured README.md.
3. Take structural and tonal inspiration from these examples:
   - https://raw.githubusercontent.com/Azure-Samples/serverless-chat-langchainjs/refs/heads/main/README.md
   - https://raw.githubusercontent.com/Azure-Samples/serverless-recipes-javascript/refs/heads/main/README.md
   - https://raw.githubusercontent.com/sinedied/run-on-output/refs/heads/main/README.md
   - https://raw.githubusercontent.com/sinedied/smoke/refs/heads/main/README.md

### README Guidelines

- Use GFM (GitHub Flavored Markdown) throughout.
- Use [GitHub admonitions](https://github.com/orgs/community/discussions/16925) where appropriate (`> [!NOTE]`, `> [!WARNING]`, etc.).
- Do not overuse emojis — use sparingly, only when they add clarity.
- Keep the README concise and to the point — avoid padding.
- Do **not** include sections for LICENSE, CONTRIBUTING, or CHANGELOG — those have dedicated files.
- If a logo or icon exists for the project, include it in the header.

### Recommended README Structure

1. **Header** — project name, optional logo, one-line description
2. **Badges** — CI status, version, license (if applicable)
3. **Overview** — what the project does and why it exists
4. **Features** — key capabilities (brief list)
5. **Prerequisites** — runtime, tools, versions required
6. **Installation / Getting Started** — step-by-step
7. **Usage** — examples, commands, configuration
8. **Architecture / How It Works** — optional, for complex projects
9. **Contributing** — pointer to CONTRIBUTING.md if it exists
10. **License** — one-line reference to the license file
