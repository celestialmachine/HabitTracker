# Command Line & CLI Reference

A quick-reference guide for running the local server, interacting with the database, and managing Python dependencies.

## Python & Project Commands

- start server: `uvicorn main:app --reload`
- run tests: `python3 -m pytest`
- regenerate requirements.txt to capture all newly installed dependencies: `pip3 freeze > requirements.txt`
- generate a secret key as a one off command in terminal (one-off): `pip3 freeze > requirements.txt`
- to activate venv: `source .venv/bin/activate`

## Git

- amend most recent commit: `git commit --amend -m "Your new commit message"`
- force update the remote server if I already pushed it to github: `git push origin main --force-with-lease`
- create a new branch and switch to it: `git checkout -b {branch_name}` or `git switch -c {branch_name}`
- switch branches: `git checkout {branch_name}` or `git switch`
- just create new branch: `git checkout {branch_name}`
- merging branch back to main: `git checkout main` AND `git merge {branch_name}`
- see list of branches: `git branch`
- push a branch to github for first time: `git push -u origin {name_of_branch_getting_first_push}`
- delete an old branch from github: `git push origin --delete {old_branch_name}`
- refresh your remote-tracking references aka tells git go check what actually exists on the remote right now, and remove any local references to remote branches that no longer really exist there.`git fetch --prune`
- applies most recent stash and removes it from list: `git stash pop`
- applies the specified stash and removes it from the list: `git stash pop stash@{stash_number}`
- `git stash push -m "{description}" {files}`
- to stash edits I am not ready to commit yet: `git stash`
- to see list of stashes: `git stash list`
- to see what is inside a stash (most recent one)`git stash show -p stash@{0}`

## PostgreSQL (`psql`) Commands

- connect to postgres server, specifically pointed to postgres db:
  `psql postgres`
- switch to diff db:
  `\c {db_name}`
- see a list of tables in the db: `\dt`
- see the schema for a table: `d {table_name}`
- `quit` or `\q` to exit out of psql completely
- `Ctrl+C` to instantly kill the current multi-line statement and return to a fresh `=#` prompt.
- `cursor.execute()` is the method that actually runs a SQL command against my db, using the connection your cursor is tied to.
  - important: cursor.execute() returns None! need the separate .fetchone()/.fetchall() step to retrieve results from SQL query

### Psql Terminal Tips

- When psql shows -# instead of =#, it means it's waiting for more lines/statements

# Quick Definitions

**FastAPI** = framework for building APIs (similar to Express in Node)

**FastAPI route** = regular Python function with decorator (@app.get(...), @app.post(...)), so that FastAPI knows to call it when a matching request comes in

**framework** = provides structural skeleton, handles routes, logic (calls my code for me when an endpoint is requested) and architecture

**Uvicorn** = runs the server and listens on specified port (similar to Node.js)

**schema** = defines db organization, how tables relate and what rules the data must follow

**psycopg2** = library that allows python to talk to postgreSQL db

**pydantic** = library for data validation and parsing using type hints; powers the BaseModel classes

**pyjwt** = library for creating and verifying JWTs for authenticating users

**dotenv** = library to load .env files in python

**requirements.txt** = equivalent to package.json for node aka lists dependencies and their versions for reproducibility purposes

**cursor** = Python object psycopg2 gives me to actually talk to the database and get results back; client-side tool

**BaseModels** = # Pydantic model that auto validates payload data before anything else runs in the routes; provides automatic 422 error for missing/incorrect-typed fields

# HTTP Status Codes

- 200 OK: The request succeeded
- 201 Created: The request succeeded and a new resource was created as a result
- 202 Accepted: The request has been accepted for processing, but processing is not complete yet
- 400 Bad Request: The server cannot process the request due to perceived client error (e.g., malformed request syntax)
- 401 Unauthorized: The request lacks valid authentication credentials
- 403 Forbidden: The server understands the request and the client identity is known, but the client does not have permission access rights
- 404 Not Found: The server cannot find the requested resource
- 422 Unprocessable Entity: more specific to "the request is structured correctly (valid JSON, right fields present), but a value inside it fails a validation rule" — e.g., password is too short, email isn't in a valid email format
- 429 Too Many Requests: The user has sent too many requests in a given amount of time (rate-limiting)
- 500 Internal Server Error: A generic error message when the server encounters an unexpected condition
- 502 Bad Gateway: The server, while acting as a gateway or proxy, received an invalid response from the upstream server
- 503 Service Unavailable: The server is currently unable to handle the request due to temporary overloading or maintenance
- 504 Gateway Timeout: The server, while acting as a gateway or proxy, did not receive a timely response from the upstream server

# Curl

## Login (return token)

```
curl -i -X POST http://localhost:8000/logins \
-H "Content-Type: application/json" \
-d '{"username": "michy7", "password": "password123"}'
```

returned token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMSwidXNlcm5hbWUiOiJtaWNoeTcifQ.5TUR1RuXTwIWwoo8EB1X2myZ3YwvjTclFx-vYpiIzn4

## Add a habit

```
curl -i -X POST http://localhost:8000/habits \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMSwidXNlcm5hbWUiOiJtaWNoeTcifQ.5TUR1RuXTwIWwoo8EB1X2myZ3YwvjTclFx-vYpiIzn4" \
-H "Content-Type: application/json" \
-d '{"content": "buy a matcha"}'

```

## Get all habits

```
curl -i http://localhost:8000/habits \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMSwidXNlcm5hbWUiOiJtaWNoeTcifQ.5TUR1RuXTwIWwoo8EB1X2myZ3YwvjTclFx-vYpiIzn4" \
-H "Content-Type: application/json"
-d "
```
