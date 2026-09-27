# Project Takeaways & Lessons Learned

Brain dump of my "aha" moments aka conceptual thoughts, software principles I attempted to apply and lessons learned during development

## Backend logic

- my main.py file builds the app object which holds all routes
- every decorator runs once at startup and registers the route to app (not everytime a request comes in)
- the fx itself is not called yet until a request comes in
- after the whole file has been executed, uvicorn starts listening on port and waits for incoming requests
- let's say I defined two routes with same path & method, FastAPI doesn't overwrite the first with second; instead it registers both routes into the app obj and when a req comes in, it executes the first match

- Backends can send requests just like a browser can too!
- why? to talk to third party APIs to retrieve their data!
- if a website doesn't have an API, devs will sometimes web scrape

## HTTP Requests

- An HTTP request has a few separate parts, and they don't mix:
- The URL/route — POST /habits, tells FastAPI which function to run
  Headers — metadata about the request, sits separately from the body. This is where Authorization: Bearer <token> lives
  The body — the actual payload, in your case the JSON you're sending: {habit: "...", frequency: "..."}
- Your BaseModel is specifically wired to look at #3, the body. It has no idea headers even exist — that's not what it's for. So you're right that your habit content comes in through the BaseModel, but the token needs a separate mechanism, because it lives in a separate part of the request.

- GET requests do not have a body! so data must be sent via URL using query params
  - since no body, no need for content-type header!
  - only need auth header to verify token

## FastAPI

- FastAPI convention/rule: when a route parameter's type is a Pydantic BaseModel, FastAPI automatically knows to look for that data in the request body (parsed from JSON), rather than the URL (path or query).
- Type hints (`: str`) are not enforced by Python itself — but FastAPI uses Pydantic internally to enforce them for ALL type-hinted parameters, whether they're inside a BaseModel or just plain function parameters.
- What actually differs between a BaseModel param and a plain typed param isn't "is it validated" (both are) — it's WHERE FastAPI looks for the data:
  - plain param matching a `{}` in the URL path → path parameter
  - plain param not in the path → query parameter (`?username=...`)
  - BaseModel type → request body (JSON)
- BaseModel is the specific signal to FastAPI: "expect this data in the JSON request body, parse it, and validate/construct an instance of this class from it."

## Curl

- Curl ("client URL"): command-line tool used to transfer data to or from a server without any user interface AKA acts like the frontend!
  - takes a URL, fetches the raw data (HTML, JSON, or code), and dumps it directly into your terminal screen
- Basic anatomy of a curl command: `curl [options] [URL]`
- important flags
  - `-X`: tells the server how to handle the req (POST, DELETE, PUT)
    - GET is what curl does if you don't say otherwise
    - `curl -X DELETE https://example.com`
  - `-H`: header; Sends extra metadata to the server, like authentication tokens or the type of data you are sending.
    - `curl -H "Authorization: Bearer MY_TOKEN" https://example.com`
  - `-d`: data/payload: Sends a body of data to the server (used with POST or PUT). This automatically makes curl default to a POST request even if you skip the -X flag.
    - `curl -d "username=bob" https://example.com`
  - `-i`: include headers in output; Tells curl to show you the HTTP status code and response headers sent back by the server. This is arguably the most useful flag for backend debugging.
    - `curl -i https://example.com`

## Virtual Environments

what is it?

- a folder of installed packages and small scripts inside venv/bin (such as activate)
- these scripts have the exact absolute path baked into them via plain text
- let's say I manually rename the folder, the scripts will continue to point to old path which no longer exists -> problemo
  - lesson learned: don't rename a venv folder after creating, instead delete and recreate it

benefits

- avoids version clashes bc it isolates project packages/dependencies so they don't conflict with other probjects
- helps with reproducability
- keeps computer clean bc packages get installed into isolated folder preventing global clutter

db in venv

- when trying to set up my db i was unsure if i needed to re-install postgres into my venv (which alr existed globally)
- postgres is a standalone db server that does not live in venv
- venv is only for python packages!

## PyJWT

- JWT (jsonwebtokens): used for auth aka proving I am who I say I am to a server
- tokens are readable! they are not encrypted
- they consist of 3 parts separated by dots:
  1. header (metadata about the token aka the signing algo used)
  2. payload (user data)
  3. signature (proof that the token hasn't been tampered with) - this is the part that provides security by making tampering detectable
- Nobody can forge or tamper with it without knowing SECRET_KEY
- tokens are stateless meaning the server doesn't store them but the client does (usually via localStorage, memory or cookie); server verifies them purely through math algo calcs aka recomputing the expected signature
- cons:
  - since the server isn't tracking active tokens, it can't easily "revoke" one early via force log out thus a stolen token remains valid until it naturally expires
- jwt.encode() uses algorithm (Singular)
- jwt.decode() uses algorithms (Plural List)
- jwt decoder website: https://www.jwt.io/ (shows the decoded payload!)

## SQL

- if it's a SELECT: result = cursor.fetchone() or fetchall()
- if it's an INSERT/UPDATE/DELETE: conn.commit()

## fetchone()

- Returns ONE row from the last executed query, as a tuple — each item corresponds to one selected column, in the order selected.
  - e.g. `SELECT * FROM users` → `(user_id, username, password_hash)` → indexable via `result[0]`, `result[1]`, `result[2]`
  - e.g. `SELECT password_hash FROM users` → `('hash_value',)` — a one-item tuple (note trailing comma)
- If no matching row exists, returns `None` (not an empty tuple) — this is why `if not existing_user:` correctly catches "no row found."
- Indexing (`result[0]`, `result[2]`, etc.) relies on knowing the exact column order from the query — fragile if column order changes; `SELECT *` depends on table definition order.
- Contrast: `.fetchall()` returns ALL matching rows as a list of tuples — `.fetchone()` is essentially "give me the first tuple from that list, or None if empty."

## Return type hints (`-> int`)

- `def fx(param: str) -> int:` — the `-> int` is a **return type hint**, saying what type the function is expected to return.
- Similar concept to TypeScript's `function fx(param: string): number` — same idea (annotate expected types), different syntax (`->` in Python vs `:` in TS).
- Like parameter type hints, NOT enforced by plain Python at runtime — just documentation/IDE support, unless paired with a tool like `mypy`.

## Software Engineering Principles

- DRY
  - don't repeat yourself
  - implemented with get_connection fx that every route calls to create a connection with db

## Browser Dev Tools

- fetch(): built in js fx provided by the browser that is specifically designed for making HTTP reqs

## Git workflow

- branches are just named pointers to a specific commit — not separate copies of files!
- my actual files on disk get rewritten by Git to match whichever branch I'm currently "on."so switching branches = Git rewrites my files to match that branch's latest commit.
- stashes are not tied to a specific branch at all so if I was to `git stash pop` on a branch, it would apply the most recent stash changes to whichever branch I am currently on
- helpful to be specific in what files I want to stash and include a message so it's less confusing

**Full cycle:**

1. `git checkout -b <branch-name>` — create + switch to a new branch off `main`
2. Make changes, `git add`, `git commit` as normal — these commits only exist on this branch, `main` is untouched
3. `git push -u origin <branch-name>` — push the branch to GitHub (`-u` only needed the first push; sets up tracking)
4. Open a Pull Request on GitHub (base: `main`, compare: your branch)
5. Review the diff
6. Merge the PR via GitHub's UI
7. Locally: `git checkout main` then `git pull` — syncs local `main` with the merge that happened on GitHub
8. Delete the branch — locally (`git branch -d <branch-name>`) and on GitHub (`git push origin --delete <branch-name>` or via the button GitHub shows after merging)
   - **Order matters:** pull BEFORE deleting locally, or Git may think the branch has unmerged work (since local `main` doesn't know about the merge yet)

**Key terms:**

- `origin` = the name for "my remote repo" (GitHub) — not a branch name
- `git push` = send my local commits up to GitHub
- `git pull` = fetch + merge remote changes into my current local branch
- Deleting a merged branch does NOT delete the commits — they already live in `main`'s history via the merge. Deleting just removes the now-unneeded label/pointer.

## Git workflow: catching prerequisite work mid-branch

I noticed a pattern in myself: I'll start working on one feature (e.g., GET /habits endpoint) on its own branch, then realize partway through that I actually need something else first (e.g., adding an `is_active` flag to habits) — and instead of pausing to create a separate branch for that prerequisite, I just kept building it into my current branch.

**Why this isn't ideal:** each branch/PR is supposed to represent one coherent, describable unit of work. Mixing "add is_active flag" into "add GET /habits endpoint" means the branch no longer cleanly represents just one thing, which makes the diff/history less clean than it should be.

**What I should do instead, when I notice this happening mid-branch:**

1. Pause current work (commit or stash)
2. Switch back to `main`
3. Create a new branch specifically for the prerequisite
4. Finish + merge that prerequisite on its own
5. Switch back to the original branch and merge `main` into it to pick up the prerequisite, then continue

**Why I didn't do the "ideal" version this time:** it adds real overhead, and since I'm working solo (not colliding with teammates), the cost of not doing this perfectly is low right now. I recognized the pattern, decided the overhead wasn't worth it for something this small-scale, and kept going in the same branch deliberately, rather than by accident.

**The bigger takeaway:** this is the same underlying instinct as realizing "I need bcrypt hashing before I can build JWT auth" — discovering a hidden prerequisite mid-task. That happens naturally and isn't a flaw in my process; the skill to build is recognizing EARLY when a prerequisite is substantial enough to deserve its own branch, vs. small enough to just fold into current work.

**For interviews:** this is a good example of self-awareness about workflow/process — I can describe noticing an imperfect git habit in myself, understanding _why_ it's not ideal, and articulating the tradeoff I made (perfect branch hygiene vs. practical solo-project overhead), rather than just blindly following a rule without understanding it.
