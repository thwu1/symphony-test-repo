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
  after_create: echo "workspace ready"
---

You are working on a Linear ticket `{{ issue.identifier }}`

{% if attempt %}
This is retry attempt #{{ attempt }}.
Resume from the current workspace state.
{% endif %}

Issue context:
Identifier: {{ issue.identifier }}
Title: {{ issue.title }}
Current status: {{ issue.state }}
Labels: {{ issue.labels }}
URL: {{ issue.url }}

Description:
{{ issue.description }}

## CRITICAL: You MUST use the Linear GraphQL API to transition issue states.

The Linear API endpoint is https://api.linear.app/graphql
Use the LINEAR_API_KEY environment variable for authentication.

### State lookup query
```graphql
query { issues(filter: {identifier: {eq: "{{ issue.identifier }}"}}) { nodes { id team { states { nodes { id name } } } } } }
```

### Update state mutation
```graphql
mutation { issueUpdate(id: "<ISSUE_UUID>", input: {stateId: "<STATE_UUID>"}) { success } }
```

### Post comment mutation
```graphql
mutation { commentCreate(input: {issueId: "<ISSUE_UUID>", body: "<BODY>"}) { success } }
```

### Read comments query
```graphql
query { issues(filter: {identifier: {eq: "{{ issue.identifier }}"}}) { nodes { id comments { nodes { body createdAt user { name } } } } } }
```

## Status map and required transitions

- `Todo` → Immediately move to `In Progress`, then start work.
- `In Progress` → Do the work. When done, move to `Human Review`.
- `Rework` → Read ALL comments, address reviewer feedback, then move to `Human Review`.
- `Human Review` → Do nothing. End turn.
- `Done` → Do nothing. End turn.

## Execution steps

1. Look up the issue UUID and team state IDs using the state lookup query (use curl).
2. If state is `Todo`, move to `In Progress`.
3. Post a workpad comment: `## Codex Workpad\n\n### Plan\n- [ ] Investigate\n- [ ] Fix\n- [ ] Test\n- [ ] Verify`
4. Read the codebase, understand the issue, implement the fix.
5. Run tests.
6. Commit changes.
7. Update workpad comment with results.
8. Move to `Human Review`.

For `Rework`: Read all comments, address feedback, then move back to `Human Review`.

## Important
- Use `curl` to call the Linear GraphQL API.
- This is unattended. Never ask a human to perform actions.
- Work only in this repository copy.
