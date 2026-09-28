# Issues ive ran across so far..

## venv

- renamed my venv folder to .venv manually rather than deleting it and creating it fresh; this caused my venv to break -> claude gave me a bunch of lines to run in my terminal
  to rebuild it from scratch which looked like a bunch of gibberish so i stopped and asked what each
  line meant and what it was doing beforehand:

  ```
  deactivate
  rm -rf .venv
  python3 -m venv .venv
  source .venv/bin/activate
  which python3
  echo $VIRTUAL_ENV
  ```

  deactivates broken venv

  recursively removes folders and everything inside the venv

  create brand new venv

  activates it

  two verification checks - confirms both paths match

## syntax issue: using single vs double quotes in psql

- single quotes is a string literal
- double quotes is an identifier (e.g. a column, table name, etc)

## cursor is undefined error

- Every time a route needs to talk to the database, it needs its own fresh connection and cursor, created inside that route's function — created and creating a cursor doesn't happen once for your whole app; it happens per-request, inside whatever function is handling that specific request.
- Connection vs. Cursor
  - Connection (conn) — represents the actual open "line" between your Python program and the Postgres server. Think of it like picking up a phone and dialing — you're now linked to the database, but you haven't said anything yet. Opening a connection is a relatively "expensive" operation (it takes a moment to establish), so you typically open one connection and reuse it for multiple operations, rather than reconnecting for every single query.
  - Cursor (cursor) — created from an open connection, and it's what actually lets you execute commands and retrieve results. Continuing the phone analogy: the connection is the open phone line, and the cursor is you actually speaking into it — sending a specific request ("run this query") and listening for the response.
- why this error? This comes down to your choice not to use an ORM (a decision you made deliberately, remember) — you're using the "raw" driver, which means you're doing the low-level work yourself (open connection, create cursor, execute, fetch, close) instead of a library doing it invisibly for you. If you had used SQLAlchemy (the Postgres equivalent of Mongoose, roughly) — you'd similarly set up a connection once.

## CORS policy error

- tried using fetch() request to POST/users endpoint from about:blank origin and came across CORS policy error
  - about:blank's origin is treated as "null" (string null) and bc its origin doesn't match the server, the cors policy gets triggered
- CORS policy: built in browser security that prevents clients from different or unauthorized origins to make requests to APIs; requires that the frontend and backend be on same origin or an authorized origin in order for them to talk to each other
- origin: the combination of protocol + domain + port (e.g. http://localhost:3000, http://localhost:8000)
- possible solutions suggested by AI
  - option 1: allow_origins=["*"]
    - fixes/bypasses the CORS error but potentially exposes the app/makes it vulnerable to the security issues that this policy protects against (e.g. malicious site trying to make direct requests to my API)
    - fine for local dev since my API isn't deployed publicly, it is only reachable on localhost and there's no real user/sensitive data at stake yet
    - The purpose right now is learning/testing, not securing a production system; optimizing for "unblock myself and keep learning" is the right tradeoff at this stage
  - option 2: explicitly list only the specific origin(s) I trust
    - prevents random sites from making authorized cross-origin requests to my API
    - more restrictive which requires me to actually know and maintain the list of allowed origins which may require a bit of ongoing configuration as my setup changes (e.g. different port for a future frontend)

## pytest not being able to locate my auth.py file to import the fx I am trying to test

- error msg: `ImportError while importing test module '/Users/michellely/Desktop/habit_tracker/tests/test_auth.py'.  ModuleNotFoundError: No module named 'auth'`
- why? bc pytest does't know where my home/root dir is
- AI initially recommended to fix by creating an empty conftest.py file which essentially tells pytest where the root dir is
- I pushed back because I didn't like the idea of having an empty file to clutter up my root dir since it seems like a waste of space and so I asked for alt options
- AI suggested instead of running `pytest` to use `python3 -m pytest` which runs pytest as a module via python itself and tells pytest directly where my project root is (still don't fullyyy understand this well but it worked..lol)

## except order matters here

```
  except jwt.InvalidTokenError:
    raise HTTPException(status_code=401,
    detail="Invalid token.")
  except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=401,
    detail="Expired token.")
```

- ExpiredSignatureError is actually a subclass of InvalidTokenError meaning an expired token is also an InvalidTokenError and since Python checks except blocks in order, top to bottom, and stops at the first match my `except jwt.InvalidTokenError` will catch expired tokens too,
- so expired tokens will always get the generic "Invalid token." message, never "Expired token."
- fix: put the more specific exception first

## Token verification kept failing even though the token itself was valid.

- error msg:

```
  (.venv) michellely@MichellesLaptop habit_tracker % curl -i -X POST http://localhost:8000/habits \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer [token]" \
  -d '{"content":"sleep"}'
  HTTP/1.1 401 Unauthorized
  date: Fri, 18 Sep 2026 06:16:10 GMT
  server: uvicorn
  content-length: 27
  content-type: application/json

{"detail":"Invalid token."}%
```

- Debugging process

  - Verified the token I sent matched what POST /logins actually returned -> allowed me to rule out a copy/paste error.
  - Decoded the token at jwt.io to confirm the payload itself was valid.
  - Spotted an unrelated typo (user_ud → user_id), fixed it in my code, generated a fresh token but error persisted, so ruled that out as the cause.
  - Checked the server terminal for the actual error traceback instead of relying on the client-side error
  - Printed the raw request.headers["Authorization"] value and saw it was "Bearer <token>" aka the "Bearer " prefix was still attached and being passed into jwt.decode() as-is
  - Fix: Split the header on the space to isolate just the token, which fixed it

- Pattern across this process: rule out the obvious/easy explanations first then go to the source of truth aka server logs

## Bug: psycopg2.ProgrammingError "no results to fetch"

**The symptom:** I was getting a 201 (success) status code back, but my `except` block was also executing - which seemed contradictory at first.

**Why the misleading status code happened:** My route had `status_code=201` set on the decorator, and my `except` block used `return {...}` instead of `raise HTTPException(...)`. Since `return` (even from inside an except block) looks like a normal, successful completion to FastAPI, it applied the `201` I'd configured - regardless of the fact that my code had actually taken the failure path internally. This taught me that `status_code` on a decorator applies to ANY non-exception-raising return, not specifically to a "happy path" return.

**How I found the real error:** My `except` block was a bare `except:` that silently swallowed whatever the real exception was. I temporarily changed it to `except Exception as e: print(type(e), e)` so I could see the actual exception in my terminal, rather than guessing blindly.

**The real error:** `psycopg2.ProgrammingError: no results to fetch`

**Root cause:** I was calling `cursor.fetchone()` right after an `INSERT` statement that had no `RETURNING` clause. Without `RETURNING`, Postgres has nothing to hand back, so `.fetchone()` has nothing to fetch and throws this error.

**The fix:** Added `RETURNING completion_id` (and other relevant columns) to the `INSERT` statement, giving `.fetchone()` something real to retrieve.

**Takeaways**

- A misleading/wrong status code doesn't always mean the status code logic itself is wrong - sometimes it's a symptom of a swallowed exception via a bare `except` + `return` instead of `raise`.
- Bare `except:` blocks hide the actual problem. Temporarily catching `Exception as e` and printing it is a fast, low-effort way to surface the real error before deciding on a proper fix.
- Any `INSERT`/`UPDATE`/`DELETE` that I want to `.fetchone()`/`.fetchall()` after MUST have a `RETURNING` clause - otherwise there's nothing to fetch, even if the statement itself succeeded.
