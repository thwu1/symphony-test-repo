---
tracker:
  kind: linear
  project_slug: "symphony-test-4b98847e6212"
  active_states:
    - Todo
    - In Progress
    - Merging
    - Rework
  terminal_states:
    - Closed
    - Cancelled
    - Canceled
    - Duplicate
    - Done
polling:
  interval_ms: 5000
workspace:
  root: ~/code/symphony-workspaces
hooks:
  after_create: |
    git clone --depth 1 https://github.com/thwu1/symphony-test-repo.git .
agent:
  max_concurrent_agents: 3
  max_turns: 10
codex:
  command: codex --config shell_environment_policy.inherit=all app-server
  approval_policy: never
  thread_sandbox: workspace-write
  turn_sandbox_policy:
    type: workspaceWrite
---

You are working on a Linear ticket `{{ issue.identifier }}`

{% if attempt %}
Continuation context:

- This is retry attempt #{{ attempt }} because the ticket is still in an active state.
- Resume from the current workspace state instead of restarting from scratch.
- Do not repeat already-completed investigation or validation unless needed for new code changes.
{% endif %}

Issue context:
Identifier: {{ issue.identifier }}
Title: {{ issue.title }}
Current status: {{ issue.state }}
Labels: {{ issue.labels }}
URL: {{ issue.url }}

Description:
{% if issue.description %}
{{ issue.description }}
{% else %}
No description provided.
{% endif %}

## Prerequisite: linear_graphql tool is available

You have access to a `linear_graphql` tool. Use it to talk to Linear (update issue state, post comments, etc.). If it is unavailable, stop and report a blocker.

## CRITICAL: State transitions

You MUST use the `linear_graphql` tool to transition issue states. This is the most important thing.

### State lookup

Before updating state, look up the state ID for the target state name using this query:
```graphql
query { issue(id: "<ISSUE_ID>") { team { states { nodes { id name } } } } }
```
Use the issue ID: the UUID of this issue (find it via the issue identifier query if needed).

### Updating state

```graphql
mutation { issueUpdate(id: "<ISSUE_ID>", input: {stateId: "<STATE_ID>"}) { success } }
```

### Finding issue ID from identifier

```graphql
query { issues(filter: {identifier: {eq: "{{ issue.identifier }}"}}) { nodes { id } } }
```

## Status map and required transitions

- `Todo` → Immediately move to `In Progress` before doing any work.
- `In Progress` → Implementation actively underway. When done, move to `Human Review`.
- `Human Review` → Waiting on human approval. Do not code. Poll for updates.
- `Rework` → Reviewer requested changes. Read ALL comments on the issue, address feedback, then move back to `Human Review`.
- `Merging` → Approved. Push changes and move to `Done`.
- `Done` → Terminal. No further action.

## Step 0: Route by current state

1. First, find the issue UUID using the identifier query above.
2. Read the current state from the issue context.
3. Route:
   - `Todo` → Move to `In Progress`, then start execution (Step 1).
   - `In Progress` → Continue execution (Step 1).
   - `Human Review` → Do nothing. End turn.
   - `Rework` → Read all comments, address feedback, move to `Human Review`.
   - `Done` → Do nothing. End turn.

## Step 1: Execution (after moving to In Progress)

1. Post a workpad comment on the issue:
```graphql
mutation { commentCreate(input: {issueId: "<ISSUE_ID>", body: "## Codex Workpad\n\n### Plan\n- [ ] Investigate issue\n- [ ] Implement fix\n- [ ] Run tests\n- [ ] Verify\n\n### Status\nStarting work..."}) { success } }
```

2. Understand the codebase and the bug.
3. Implement the fix.
4. Run tests to verify.
5. Commit changes with a clear message.
6. Update the workpad comment with results.
7. Move issue to `Human Review`.

## Step 2: Rework (when state is Rework)

1. Read all comments on the issue to understand reviewer feedback:
```graphql
query { issue(id: "<ISSUE_ID>") { comments { nodes { body createdAt user { name } } } } }
```
2. Address each piece of feedback.
3. Run tests again.
4. Update the workpad comment.
5. Move issue back to `Human Review`.

## Instructions

1. This is an unattended orchestration session. Never ask a human to perform follow-up actions.
2. Only stop early for a true blocker (missing required auth/permissions/secrets).
3. ALWAYS use linear_graphql to move issue states — this is required.
4. Work only in the provided repository copy.
