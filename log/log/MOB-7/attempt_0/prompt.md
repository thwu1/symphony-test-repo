You are working on a Linear ticket `MOB-7`

{% if attempt %}
This is retry attempt #0.
Resume from the current workspace state.
{% endif %}

Issue context:
Identifier: MOB-7
Title: Fix task completion endpoint returning wrong status code
Current status: Todo
Labels: 
URL: https://linear.app/rllm-project/issue/MOB-7/fix-task-completion-endpoint-returning-wrong-status-code

Description:
The PUT /api/tasks/<id>/complete endpoint returns 200 instead of the correct status code. It should return 200 with the updated task data, but currently returns an incorrect response format.

Steps to reproduce:

1. Create a task via POST /api/tasks
2. Complete it via PUT /api/tasks/<id>/complete
3. Observe the response status and body

Expected: 200 with updated task JSON
Actual: Returns wrong status code

## CRITICAL: You MUST use the Linear GraphQL API to transition issue states.

The Linear API endpoint is https://api.linear.app/graphql
Use the LINEAR_API_KEY environment variable for authentication.

### State lookup query
```graphql
query { issues(filter: {identifier: {eq: "MOB-7"}}) { nodes { id team { states { nodes { id name } } } } } }
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
query { issues(filter: {identifier: {eq: "MOB-7"}}) { nodes { id comments { nodes { body createdAt user { name } } } } } }
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