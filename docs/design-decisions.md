# Design Decisions/Tradeoffs

Log of all the times "I considered X vs Y, and chose X, Y or Z because"

## Username Uniqueness

- Considered: how to check if a username is unique?
- Options
  - A: Check first, then insert (what I originally was thinking)
    - Query: "does a user with this username already exist?"
    - If yes → return an error, stop here
    - If no → proceed to insert the new user
  - B: Just try to insert, and catch the failure
    - Attempt the insert directly
    - If the UNIQUE constraint on the DB rejects it (throws an error), catch that error in your code and translate it into a friendly "username already taken" response
    - If it succeeds, great — no separate check needed
- Decided: on Approach A because intuitively it made more sense to me
  - But Claude said Approach B is actually often preferred in real systems, because Approach A has a subtle flaw: between my "check" and my "insert," a tiny window exists where another request could sneak in and create that same username — so relying only on the check isn't always airtight. The database's UNIQUE constraint is the actual, guaranteed source of truth; your own check-first query is more of a nicety for a faster/friendlier error, not a substitute for it.

## POST/habits - user_id

- Considered: how does user_id get into a POST/habits request?
- Options
  - A: Client sends user_id directly in the request body -> security issues & potential issue of saving habit to wrong user
  - B: Server determines user_id from authentication (e.g., a JWT token), not from the request body at all
- Decided: Approach B is slightly more work but safer security wise so I will go with that

## Password hashing

- Considered: should password hashing remain in my POST/users route or should I move it into its own standalone fx outside of the route?
- pros: easier unit testing (no need to involve server, DB, HTTP etc)
- cons: requires creating new fx/new file
- Decided: create a new auth.py file which will store my security/auth related fxs: hash_password, verify_password, create_jwt etc

## ORM

- Considered: to use an ORM or to not?
- AI recommended me to use an ORM; rather than just defaulting to use what AI suggested I asked AI to list what the tradeoffs were
- ORM (e.g., SQLAlchemy): less boilerplate, built-in SQL injection protection, easier migrations but hides the actual SQL, adds a new abstraction to learn, and can generate inefficient queries I don't immediately see
- Raw SQL (e.g., psycopg2): full transparency into exactly what queries run, reinforces SQL skills directly, no new abstraction to learn but more manual work per query, manual connection handling, and no automatic migration tooling
- Decided: go with raw SQL because I want to practice writing queries and know exactly what's happening; allows me to see the actual mechanics that every ORM is secretly doing on my behalf; understand why a connection and cursor are needed per-request; also this way makes learning an ORM later much faster bc once I eventually do pick up SQLAlchemy (or go back to Mongoose/similar), I'll understand what it's actually doing for me, rather than treating it as magic. I'll recognize "oh, this ORM is just doing the connection/cursor dance I already know, behind a nicer interface"

## Security

- CORS
  - Currently using `allow_origins=["*"]` for CORS since this is local-only
  - will replace with specific allowed origin(s) before any public deployment
- Auth feedback
  - Context: considered how specific my error messages should be. for instance, "username not found" or "incorrect password" vs something more generic like "incorrect credentials"
  - attacker attempting to break into an account can efficiently enumerate valid usernames first by trying many usernames, watching for which ones return "incorrect password" instead of "username not found" — since that tells them the username exists, just the password was wrong
  - a generic, identical error for both cases (e.g. "invalid username or password)
    - denies the attacker any information about which part was wrong, forcing them to always guess both pieces together, with no shortcuts.

## DB Schema

- Schema changes get more expensive over time aka once I have real data in a table, changing its structure means migrating existing rows so its best to spend time planning schema in advance
- design decision tradeoffs:
  - **Approach #1 (my initial thought process): storing todays_completion_status inside the habits table**
    - pro: simple, fast reads because no counting/looping through rows, streak is just sitting right there as a column
    - pro/con: less data stored; not storing individual completion records over time so no historical data (but do i need that or is it just taking up storage?)
    - con: can only store one status at a time, will need to be cleared every day?
  - **Approach #2 (what I ultimately went with): separate habits table and completion history table**
    - pro: stores history/every date that a habit was completed (creates a new row)
    - pro: scales better since a habit can have multiple completions and I can choose to display them all via a calendar view or something later on if I build a FE
    - con: slightly more complex queries involving checking two tables via JOIN to answer qs like longest streak, current streak etc

## Approach #2 Schema design / data modeling notes

- users table (must create this table first so habit table can reference it; will only hold one row aka me for now)
  - user_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY -> postgres auto generates/populates
  - username VARCHAR(50) NOT NULL UNIQUE
  - password_hash VARCHAR(255) NOT NULL
- habits table
  - habit_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY
  - content TEXT NOT NULL
  - date_created DATE DEFAULT CURRENT_DATE -----> auto populates; user does not need to enter
  - user_id INT NOT NULL REFERENCES users(user_id)
  - is_active BOOLEAN DEFAULT TRUE (soft-delete flag)
- completions table
  - habit_id INT NOT NULL REFERENCES habits(habit_id)
  - completion_date DATE DEFAULT CURRENT_DATE

## POST/logins - payload

- Considered: should both username and user_id be returned as payload when logging in?
- Options
  - returning a dict with user_id and username or just user_id since that is all POST/habits needs to create a new habit for the user and save it to habits table
  - habits table cols: habit_id (auto generated), content (provided by user), date_created (auto generated), user_id (extracted from token provided by user)
- Decided: tso return username just in case for now, not sure if i would need it but better safe than sorry? is there any tradeoffs/cons of a slightly bigger paylod? I presume it can result in requiring more memory/effort but in this scenario, it should be fine?

## "Deleting" a habit

Historical vs. mutable data

**Context:** Completions table rows represent historical facts (e.g., "this habit was completed on this date") - they should only ever be inserted or deleted, never updated, since mutating a historical record risks losing information that can't be recovered.

**Design question:** If a user deletes a habit, should that cascade-delete its completion history or should the habit be soft-deleted instead (preserving history)?

**Decision:** Soft-delete via an `is_active` flag on `habits`. When a user "deletes" a habit, `is_active` is set to `False` rather than removing the row - this preserves the habit's full completion history rather than losing it to a cascade delete.

## Does "unmark" delete a row from completions table?

- Considered:

### The case for deleting the row:

If a user marks a habit complete, then immediately realizes they misclicked and unmarks it — arguably, "complete" was never really a true fact for that day; deleting the row simply undoes the mistake. Under this view, completions only ever contains rows that represent genuinely, currently-true completions.

### The case against deleting (worth considering, given the historical-data principle)

If you ever wanted to know "did the user ever mark this habit complete and then change their mind" — deleting the row destroys that information entirely. This is a real, if perhaps unlikely, thing you might want later (e.g., for debugging weird streak behavior, or just user-behavior curiosity).

### decision:

Unmarking today's completion, moments after marking it, isn't erasing meaningful history - it's correcting an immediate action, more like undoing a typo than rewriting the past.

If "unmark" could be used to retroactively delete a completion from, say, three weeks ago — that starts to feel more like altering history rather than correcting an immediate mistake. Worth deciding: should "unmark" only be allowed for today's completion, or can a user unmark any past date? This is actually a genuine design question worth being deliberate about, similar to the others you've worked through.

## Table naming: completions vs. completed_habits

- Considered `completed_habits`, but decided `completions` is more accurate.
- Naming principle: name a table after what each ROW represents, not a filtered description of a related entity. This table stores completion EVENTS (habit_id, completion_date) — not habit data itself — so `completions` fits; `completed_habits` implies it stores habits, which it doesn't.
- Kept naming consistent with `users`/`habits` pattern: each table name = the entity/concept its rows represent.

## Unmarking a habit - scope decision

- Considered: should users be able to unmark ANY past date, or only today's completion?
- Decided: restrict to today only. Allowing arbitrary past-date unmarking would let users effectively rewrite completion history, which conflicts with the historical-data principle (Victor's earlier point).
- Unmarking today's completion is different - it's correcting an immediate action, not rewriting the past.
- Implementation naturally enforces this scope: `DELETE FROM completions WHERE habit_id = %s AND completion_date = CURRENT_DATE;` - no extra validation needed, since the query itself is scoped to today by design.

## GET /habits - single endpoint with optional filter param vs. multiple endpoints

I considered two approaches for letting users filter habits by completion status:

1. Three separate endpoints: one for all habits, one for complete only, one for incomplete only
2. A single endpoint with an optional query param (e.g., `?status=complete` or `?status=incomplete`)

**I decided on option 2** - a single endpoint with an optional param, defaulting to returning all habits if no param is supplied OR if the param supplied doesn't match `complete`/`incomplete`.

**Why:**

- Avoids duplicating the core query logic across three separate endpoints - the filtering logic lives in one place
- More extensible - if I ever want to add more filter dimensions later (e.g., filter by date created), I don't need a new endpoint for every combination
- Matches standard REST convention (filtering via query params on a single resource endpoint, rather than baking filter logic into the URL/route itself)
- Defaulting invalid/unrecognized param values to "return all" (rather than throwing an error) keeps the endpoint forgiving/simple for now - a client sending a typo'd or unexpected value still gets a reasonable, safe response instead of a hard failure

**Tradeoff I'm accepting:** silently defaulting on invalid params means a client with a typo (e.g., `?status=complet`) won't get an explicit error telling them their param was wrong - they'll just quietly get all habits back. I'm okay with this for now since I'm the only consumer of this API right now, but if this were a public/multi-user API, I might reconsider returning a 400 for unrecognized filter values instead.

## Preventing duplicate completions on same day

One thing worth deciding now, before you create it: preventing duplicate completions on the same day

What stops a user from accidentally calling "mark complete" twice in one day, creating two rows for the same habit_id + completion_date? This matters for streak calculations — if you're counting distinct days completed, duplicate rows for the same day shouldn't cause a problem for counting logic (if written carefully), but it's messier data than necessary, and could cause bugs if your streak-counting logic isn't written defensively.

## TODO: minor schema cleanup

- `habits.date_created` is missing a `NOT NULL` constraint (has `DEFAULT CURRENT_DATE`, but nothing stops an explicit NULL from being inserted).
- Same reasoning applies here as `completions.completion_date` - a habit record without a creation date doesn't represent a coherent fact.
- Low priority, not blocking anything - fix later via a new migration file: `ALTER TABLE habits ALTER COLUMN date_created SET NOT NULL;`

## Mark habit incomplete

- involves deleting the habit's completion row for current date from completions table
- during dev, decided to run SELECT statement first to make sure I am returning the right row before deleting it!
