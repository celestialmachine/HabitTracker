# Project Takeaways & Lessons Learned

Brain dump of my "aha" moments aka conceptual thoughts, software principles I attempted to apply and lessons learned during development

## Backend logic

- My main.py file builds the app object which holds all routes.
- Every decorator runs once at startup and registers the route to app (not every time a request comes in).
- The function itself isn't called yet until a request comes in.
- After the whole file has been executed, uvicorn starts listening on the port and waits for incoming requests.
- If I define two routes with the same path & method, FastAPI doesn't overwrite the first with the second - instead it registers both routes into the app object, and when a request comes in, it executes the first match.
- Backends can send requests just like a browser can too! Why? To talk to third-party APIs to retrieve their data. If a website doesn't have an API, devs will sometimes web scrape.

## HTTP Requests

An HTTP request has a few separate parts, and they don't mix:

- The URL/route - e.g. `POST /habits`, tells FastAPI which function to run
- Headers - metadata about the request, sits separately from the body. This is where `Authorization: Bearer <token>` lives
- The body - the actual payload, e.g. the JSON I'm sending: `{content: "..."}`

My BaseModel is specifically wired to look at the body. It has no idea headers even exist - that's not what it's for. My habit content comes in through the BaseModel, but the token needs a separate mechanism, because it lives in a separate part of the request.

There are three main places data can travel in an HTTP request, plus a fourth less obvious one (cookies).

**1. URL**

- **Path parameters** - part of the URL structure itself, marked with `{}` in the route definition. Used for identifying a specific resource. e.g. `{habit_id}` in `/habits/{habit_id}/complete`
- **Query parameters** - appended after `?` in the URL. Used for optional filters/modifiers. e.g. `?status=complete` in `/habits?status=complete`

**2. Request body**

- The actual JSON payload sent with the request - what my Pydantic `BaseModel` classes parse.
- Typically used with `POST`/`PUT`/`PATCH`, rarely with `GET`.
- I've used this for: `UserCreate`, `LoginRequest`, `HabitCreate`

**3. Headers**

- Metadata about the request itself, separate from the URL and body.
- I've used this for: `Authorization: Bearer <token>` (JWT auth), `Content-Type: application/json`

**4. Cookies (haven't used yet, but worth knowing)**

- Sent automatically by the browser with every request to a given domain, without manually attaching them like a header/body value each time.
- Relevant for session-based auth (an alternative to JWT, where the token lives in a cookie instead of requiring a manually-attached Authorization header).

**GET requests do not have a body!** So data must be sent via the URL using query params.

- Since there's no body, there's no need for a Content-Type header.
- Only need the auth header to verify the token.

### Quick reference table (what I've actually used)

| Location        | What I use it for                           |
| --------------- | ------------------------------------------- |
| Path parameter  | `habit_id` in `/habits/{habit_id}/complete` |
| Query parameter | `status` in `/habits?status=complete`       |
| Request body    | `UserCreate`, `LoginRequest`, `HabitCreate` |
| Header          | `Authorization: Bearer <token>`             |

### How FastAPI decides where to look for each param

- Plain type (`str`, `int`), matching a `{}` in the URL path -> path parameter
- Plain type, NOT in the URL path -> query parameter
- Pydantic `BaseModel` type -> request body (parsed as JSON)
- Declared via `Header(...)` or extracted from a `Request` object -> headers

## FastAPI

- FastAPI convention/rule: when a route parameter's type is a Pydantic BaseModel, FastAPI automatically knows to look for that data in the request body (parsed from JSON), rather than the URL (path or query).
- Type hints (`: str`) are not enforced by Python itself - but FastAPI uses Pydantic internally to enforce them for ALL type-hinted parameters, whether they're inside a BaseModel or just plain function parameters.
- What actually differs between a BaseModel param and a plain typed param isn't "is it validated" (both are) - it's WHERE FastAPI looks for the data:
  - plain param matching a `{}` in the URL path -> path parameter
  - plain param not in the path -> query parameter (`?username=...`)
  - BaseModel type -> request body (JSON)
- BaseModel is the specific signal to FastAPI: "expect this data in the JSON request body, parse it, and validate/construct an instance of this class from it."

## Curl

- Curl ("client URL"): command-line tool used to transfer data to or from a server without any UI - acts like the frontend!
  - Takes a URL, fetches the raw data (HTML, JSON, or code), and dumps it directly into my terminal screen.
- Basic anatomy of a curl command: `curl [options] [URL]`
- Important flags:
  - `-X`: tells the server how to handle the request (POST, DELETE, PUT). GET is the default if I don't say otherwise. e.g. `curl -X DELETE https://example.com`
  - `-H`: header; sends extra metadata to the server, like auth tokens or content type. e.g. `curl -H "Authorization: Bearer MY_TOKEN" https://example.com`
  - `-d`: data/payload; sends a body of data (used with POST/PUT). This automatically makes curl default to POST even if I skip `-X`. e.g. `curl -d "username=bob" https://example.com`
  - `-i`: include headers in output; shows the HTTP status code and response headers - probably the most useful flag for backend debugging. e.g. `curl -i https://example.com`

## Virtual Environments

**What is it?**

- A folder of installed packages and small scripts inside `venv/bin` (such as `activate`).
- These scripts have the exact absolute path baked into them via plain text.
- If I manually rename the folder, the scripts will continue to point to the old path, which no longer exists - problem. Lesson learned: don't rename a venv folder after creating it - instead delete and recreate it.

**Benefits**

- Avoids version clashes because it isolates project packages/dependencies so they don't conflict with other projects.
- Helps with reproducibility.
- Keeps my computer clean because packages get installed into an isolated folder, preventing global clutter.

**DB in venv**

- When setting up my DB, I was unsure if I needed to re-install Postgres into my venv (which already existed globally).
- Postgres is a standalone DB server that does not live in a venv.
- Venv is only for Python packages!

## PyJWT

- JWT (JSON Web Tokens): used for auth, aka proving I am who I say I am to a server.
- Tokens are readable! They are not encrypted.
- They consist of 3 parts separated by dots:
  1. Header (metadata about the token, e.g. the signing algo used)
  2. Payload (user data)
  3. Signature (proof the token hasn't been tampered with) - this is the part that provides security by making tampering detectable
- Nobody can forge or tamper with a token without knowing `SECRET_KEY`.
- Tokens are stateless - the server doesn't store them, but the client does (usually via localStorage, memory, or a cookie); the server verifies them purely through math (recomputing the expected signature).
- Cons: since the server isn't tracking active tokens, it can't easily "revoke" one early via force logout - a stolen token remains valid until it naturally expires.
- `jwt.encode()` uses `algorithm` (singular). `jwt.decode()` uses `algorithms` (plural list).
- JWT decoder website: https://www.jwt.io/ (shows the decoded payload!)

## SQL

- If it's a SELECT: `result = cursor.fetchone()` or `.fetchall()`
- If it's an INSERT/UPDATE/DELETE: `conn.commit()`

### fetchone()

- Returns ONE row from the last executed query, as a tuple - each item corresponds to one selected column, in the order selected.
  - e.g. `SELECT * FROM users` -> `(user_id, username, password_hash)` -> indexable via `result[0]`, `result[1]`, `result[2]`
  - e.g. `SELECT password_hash FROM users` -> `('hash_value',)` - a one-item tuple (note trailing comma)
- If no matching row exists, returns `None` (not an empty tuple) - this is why `if not existing_user:` correctly catches "no row found."
- Indexing (`result[0]`, `result[2]`, etc.) relies on knowing the exact column order from the query - fragile if column order changes; `SELECT *` depends on table definition order.
- Contrast: `.fetchall()` returns ALL matching rows as a list of tuples - `.fetchone()` is essentially "give me the first tuple from that list, or None if empty."

## Return type hints (`-> int`)

- `def fx(param: str) -> int:` - the `-> int` is a return type hint, saying what type the function is expected to return.
- Similar concept to TypeScript's `function fx(param: string): number` - same idea (annotate expected types), different syntax (`->` in Python vs `:` in TS).
- Like parameter type hints, NOT enforced by plain Python at runtime - just documentation/IDE support, unless paired with a tool like `mypy`.

## DRY

- DRY (don't repeat yourself) - implemented with my `get_connection()` function, which every route calls to create a connection with the DB, instead of repeating connection code everywhere.

## Browser Dev Tools

- `fetch()`: built-in JS function provided by the browser, specifically designed for making HTTP requests.

## Auto-incrementing IDs and gaps

I noticed that failed/rolled-back inserts still consume an ID value from the sequence - e.g. if creating `user_id=1` fails and the next attempt succeeds, it gets assigned `user_id=2`, not 1. This is normal, expected Postgres behavior (sequences increment regardless of insert success/failure, since checking success first would hurt performance under concurrent access). Gaps in IDs are completely fine - IDs only need to be unique, not perfectly sequential/gapless.

## Git workflow

- branches are just named pointers to a specific commit — not separate copies of files!
- my actual files on disk get rewritten by Git to match whichever branch I'm currently "on."so switching branches = Git rewrites my files to match that branch's latest commit.
- stashes are not tied to a specific branch at all so if I was to `git stash pop` on a branch, it would apply the most recent stash changes to whichever branch I am currently on
- helpful to be specific in what files I want to stash and include a message so it's less confusing

**Full cycle:**

1. `git checkout -b <branch-name>` - create + switch to a new branch off `main`
2. Make changes, `git add`, `git commit` as normal - these commits only exist on this branch, `main` is untouched
3. `git push -u origin <branch-name>` - push the branch to GitHub (`-u` only needed the first push; sets up tracking)
4. Open a Pull Request on GitHub (base: `main`, compare: my branch)
5. Review the diff
6. Merge the PR via GitHub's UI
7. Locally: `git checkout main` then `git pull` - syncs local `main` with the merge that happened on GitHub
8. Delete the branch - locally (`git branch -d <branch-name>`) and on GitHub (`git push origin --delete <branch-name>` or via the button GitHub shows after merging)
   - **Order matters:** pull BEFORE deleting locally, or Git may think the branch has unmerged work (since local `main` doesn't know about the merge yet)

**Key terms:**

- `origin` = the name for "my remote repo" (GitHub) - not a branch name
- `git push` = send my local commits up to GitHub
- `git pull` = fetch + merge remote changes into my current local branch
- Deleting a merged branch does NOT delete the commits - they already live in `main`'s history via the merge. Deleting just removes the now-unneeded label/pointer.

### Catching prerequisite work mid-branch

I noticed a pattern in myself: I'll start working on one feature (e.g., GET /habits endpoint) on its own branch, then realize partway through that I actually need something else first (e.g., adding an `is_active` flag to habits) - and instead of pausing to create a separate branch for that prerequisite, I just kept building it into my current branch.

**Why this isn't ideal:** each branch/PR is supposed to represent one coherent, describable unit of work. Mixing "add is_active flag" into "add GET /habits endpoint" means the branch no longer cleanly represents just one thing, which makes the diff/history less clean than it should be.

**What I should do instead, when I notice this happening mid-branch:**

1. Pause current work (commit or stash)
2. Switch back to `main`
3. Create a new branch specifically for the prerequisite
4. Finish + merge that prerequisite on its own
5. Switch back to the original branch and merge `main` into it to pick up the prerequisite, then continue

**Why I didn't do the "ideal" version this time:** it adds real overhead, and since I'm working solo (not colliding with teammates), the cost of not doing this perfectly is low right now. I recognized the pattern, decided the overhead wasn't worth it for something this small-scale, and kept going in the same branch deliberately, rather than by accident.

**The bigger takeaway:** this is the same underlying instinct as realizing "I need bcrypt hashing before I can build JWT auth" - discovering a hidden prerequisite mid-task. That happens naturally and isn't a flaw in my process; the skill to build is recognizing EARLY when a prerequisite is substantial enough to deserve its own branch, vs. small enough to just fold into current work.

**For interviews:** this is a good example of self-awareness about workflow/process - I can describe noticing an imperfect git habit in myself, understanding _why_ it's not ideal, and articulating the tradeoff I made (perfect branch hygiene vs. practical solo-project overhead), rather than just blindly following a rule without understanding it.

## Git workflow: the cost of not finishing one branch before starting the next

I spent a long stretch untangling a genuinely confusing multi-branch situation, and traced every single confusing moment back to one root cause: I had multiple branches open/parked simultaneously instead of finishing and merging one before starting the next.

**What went wrong, concretely:**

- Branches went stale (e.g. `mark-habit-complete`, `test-habits-endpoint`) because I started them, then moved to other work before finishing.
- A branch showed "7 commits ahead, 10 behind main" because it sat parked while other branches merged into `main` in the meantime.
- I hit real merge conflicts (in `main.py` and my notes files) specifically because `add-get-habits-endpoint` also went stale while other work (is_active flag, GET /habits, completions table) moved forward on/into `main` separately.
- A stray, confusing PR (#5) got created on top of an already-tangled multi-branch state, adding more noise.

**What I learned:**

- None of this would have happened if I'd finished and merged each branch fully (branch -> work -> PR -> merge -> pull -> delete) before starting the next one.
- GitHub's "X commits ahead / Y behind" summary can look alarming or confusing, but `git log main..<branch> --oneline` is the ground truth for what's actually unique/unmerged on a branch - worth checking this directly instead of trusting the UI summary when in doubt.
- Nothing was actually lost in the process - every commit was recoverable, every conflict was resolvable. The mess was about _confusion and time spent_, not lost work. Stashes and local commits are more durable than they feel in the moment of panic.

**The rule going forward:** don't create a new branch until the current one is merged and deleted. If I discover a prerequisite mid-branch, I now have real experience with both "just keep going in this branch" and "the mess that happens when multiple branches drift apart" - so I can make an informed choice each time, rather than defaulting to whichever feels easiest in the moment.

**For interviews:** this is a strong, honest story about learning git workflow discipline through direct experience rather than just reciting best practices - I can walk through what went wrong, why, how I diagnosed it (checking `git log`, `git stash list`, `git branch -a` rather than guessing), and resolved it without losing any work.

## LEFT JOIN and NULL: real constraint vs. query-result placeholder

I ran into a subtle question: if `completions.habit_id` has a `NOT NULL` constraint, how can a `LEFT JOIN` show it as NULL when checking for "no matching completion"? Doesn't that contradict the constraint?

**The resolution - two separate layers:**

- **Real stored data**: the `NOT NULL` constraint fully applies to actual rows stored in the `completions` table. I could never successfully INSERT a row there with a null `habit_id` - the constraint is enforced at the storage level, always.
- **Query-result placeholders**: a `LEFT JOIN` keeps every row from the left table (`habits`) even when there's no matching row in the right table (`completions`). When there's no match, Postgres fills in NULL for every column that WOULD have come from `completions`, purely as a way to represent "no match" in that one query's output. This doesn't touch, violate, or contradict the real table's constraint at all - it's a temporary placeholder in the result set, not a real null value from a real row.

**Why I should check `completion_id IS NULL` (primary key) rather than `habit_id IS NULL` (a NOT NULL foreign key) when detecting "no match":**

- `habit_id IS NULL` happens to work correctly today, but only because `habit_id` currently has a `NOT NULL` constraint - it's "correct by coincidence," relying on today's schema staying exactly as-is.
- `completion_id` is the primary key - by definition, a primary key can NEVER be null on a real row, under any possible schema change, ever (short of removing the primary key constraint entirely, which would be a much bigger, deliberate decision).
- If I ever changed `habit_id` to be nullable for some unrelated reason later (e.g. some future feature), a real completions row could have `habit_id = NULL` - and my LEFT JOIN check would then wrongly treat a real, existing completion as "no match found."

**The general principle:** choose the version of a check that's correct BY DEFINITION (primary key can never be null on a real row), not just correct by coincidence given the current schema. This is the same reasoning as adding explicit UNIQUE/NOT NULL constraints earlier rather than just hoping application code behaves correctly - relying on structural guarantees over incidental/current-state correctness.

if status == "complete":
cursor.execute(
"SELECT _
FROM habits
INNER JOIN completions
ON habits.habit_id = completions.habit_id
WHERE habit.user_id = %s AND habit.is_active = true AND completions.completion_date = CURRENT_DATE;", (user_id,),
)
elif status == "incomplete":
cursor.execute(
"SELECT _
FROM habits
LEFT JOIN completions
ON habits.habit_id = completions.habit_id
AND completions.completion_date = CURRENT_DATE
WHERE habit.user_id = %s AND habit.is_active = true;
",
(user_id,),
)
