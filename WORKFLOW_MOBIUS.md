---
tracker:
  kind: linear
  project_slug: symphony-test-4b98847e6212
  active_states: [Todo, In Progress, Rework]
  terminal_states: [Done, Closed, Cancelled, Canceled, Duplicate]
  log_root: ./log
workspace:
  repo: /Users/tianhaowu/code/symphony-test-repo
agent:
  type: claude
  model: anthropic/claude-sonnet-4-20250514
  max_concurrent: 3
  timeout: 600
hooks:
  after_create: |
    apt-get update -qq && apt-get install -y -qq gh git jq curl 2>/dev/null || true
    git config --global user.email "symphony@rllm.dev"
    git config --global user.name "Symphony Agent"
---

You are working on a Linear ticket `{{ issue.identifier }}`

Attempt: {{ attempt }}
If this is a retry, resume from the current workspace state.

Issue context:
Identifier: {{ issue.identifier }}
Title: {{ issue.title }}
Current status: {{ issue.state }}
Labels: {{ issue.labels }}
URL: {{ issue.url }}

Description:
{{ issue.description }}

## Git and GitHub setup

You have `gh` CLI and `GITHUB_TOKEN` available. The repo remote is `https://github.com/thwu1/symphony-test-repo.git`.

Configure git remote with token auth:
```bash
git remote set-url origin https://x-access-token:${GITHUB_TOKEN}@github.com/thwu1/symphony-test-repo.git
```

## CRITICAL: Linear state transitions

Use `curl` with `$LINEAR_API_KEY` to call https://api.linear.app/graphql.

### State lookup
```graphql
query { issues(filter: {identifier: {eq: "{{ issue.identifier }}"}}) { nodes { id team { states { nodes { id name } } } } } }
```

### Update state
```graphql
mutation { issueUpdate(id: "<UUID>", input: {stateId: "<STATE_UUID>"}) { success } }
```

### Post comment
```graphql
mutation { commentCreate(input: {issueId: "<UUID>", body: "<BODY>"}) { success } }
```

## Status map

- `Todo` → Move to `In Progress`, then do work.
- `In Progress` → Implement, test, push branch, create PR, move to `Human Review`.
- `Rework` → Read comments, fix, push, update PR, move to `Human Review`.
- `Human Review` → Do nothing.
- `Done` → Do nothing.

## Execution steps

1. Look up issue UUID and state IDs via Linear API.
2. If `Todo`, move to `In Progress`.
3. Post a workpad comment with your plan.
4. Set up git remote: `git remote set-url origin https://x-access-token:${GITHUB_TOKEN}@github.com/thwu1/symphony-test-repo.git`
5. Create a branch: `git checkout -b {{ issue.identifier }}`
6. Implement the fix.
7. Run tests: `cd /root/workspace && python -m pytest tests/ -v`
8. Commit and push: `git add -A && git commit -m "{{ issue.identifier }}: <summary>" && git push -u origin {{ issue.identifier }}`
9. Create PR: `gh pr create --title "{{ issue.identifier }}: <title>" --body "<description>" --base main`
10. Post the PR URL in a Linear comment.
11. Move to `Human Review`.

For `Rework`: checkout existing branch, read comments, fix, push, move to `Human Review`.

## Important
- ALWAYS push your branch and create a PR before moving to Human Review.
- This is unattended. Never ask a human.
- Work only in this repository.
