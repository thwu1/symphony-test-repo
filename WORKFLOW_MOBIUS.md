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
  model: anthropic/claude-opus-4-20250514
  max_concurrent: 3
  timeout: 600
hooks:
  after_create: |
    apt-get update -qq && apt-get install -y -qq gh git jq curl 2>/dev/null || true
    git config --global user.email "symphony@rllm.dev"
    git config --global user.name "Symphony Agent"
    git remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@github.com/thwu1/symphony-test-repo.git" 2>/dev/null || true
    echo "${GITHUB_TOKEN}" | gh auth login --with-token 2>/dev/null || true
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

## Environment

- `gh` CLI is authenticated and ready to use.
- Git remote `origin` is configured with push access to `thwu1/symphony-test-repo`.
- `LINEAR_API_KEY` is available as an environment variable for `curl` calls.

## CRITICAL: Linear state transitions

Use `curl -H "Authorization: $LINEAR_API_KEY"` to call https://api.linear.app/graphql.

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
- `Rework` → Check out existing branch, read comments, fix, push, update PR, move to `Human Review`.
- `Human Review` → Do nothing.
- `Done` → Do nothing.

## Execution steps

1. Look up issue UUID and state IDs via Linear API (use curl).
2. Check for existing branch: `git fetch origin && git checkout {{ issue.identifier }} 2>/dev/null || git checkout -b {{ issue.identifier }}`
3. Check for existing PR: `gh pr list --head {{ issue.identifier }} --json number,url --jq '.[0]'`
4. If `Todo`, move to `In Progress`.
5. If `Rework`: read ALL Linear comments to find reviewer feedback.
6. Post a workpad comment with your plan.
7. Implement the fix (or address rework feedback).
8. Run tests: `python -m pytest tests/ -v`
9. Commit and push: `git add -A && git commit -m "{{ issue.identifier }}: <summary>" && git push -u origin {{ issue.identifier }}`
10. Create PR if none exists: `gh pr list --head {{ issue.identifier }} --json number | grep -q number || gh pr create --title "{{ issue.identifier }}: <title>" --body "<description>" --base main`
11. Post the PR URL in a Linear comment (get it with `gh pr view --json url -q .url`).
12. Move to `Human Review`.

## Important
- ALWAYS push your branch and create a PR before moving to Human Review.
- This is unattended. Never ask a human.
- Work only in this repository.
