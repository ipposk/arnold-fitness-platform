# Penelope
Project Penelope

## API

### PATCH `/session/{test_id}`

Rename an existing pentest session.

Request body:

```json
{ "goal": "New session name" }
```

Requires Cognito authentication and returns the updated session context.

