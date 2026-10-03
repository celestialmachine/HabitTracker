## Use Cases

### Create a user account

**main flow**

1. User sends a POST/users request that includes a valid username and password
2. BE verifies username is valid aka unique
3. BE verifies password is valid aka at least 5 chars in length and contains at least one number
4. BE hashes password and stores into DB
5. BE returns newly created user as a user_id and username (not the hashed password bc security!)

**errors/edge cases**

- username already exists -> returns error
- invalid username/password (e.g. null or empty) -> returns 400 error?

### Add a new habit:

**main flow**

1. User sends a POST/habits request to create a new habit by supplying content
2. BE validates the request, ensuring content is not empty or null (could it be null?)
3. BE saves the new habit into DB, associated with the user
4. BE returns the newly created habit

**error/edge cases**

- what happens if habit content is invalid (e.g. empty or null) -> return an error (e.g. "missing habit content") instead of saving a blank habit
- what if the habit content is really long? -> DB restricts content limit via VARCHAR(255)
- what if DB fails to write (e.g. network issues etc) -> return an error (e.g. "Network issue, please try again later") instead of silently pretending it worked
- saving habit to wrong user due to missing token/invalid token? -> BE should reject request
- can user create two habits with same content? -> no, DB requires habits to be unique

### Mark a habit as complete for the current date

### Mark a habit as incomplete for the current date

Deletes the row from the completions table
**main flow**

1. User sends a DELETE/habits/{habit_id}/complete and provides habit_id
2. BE validates that there is an existing habit_id for that user
3. BE queries the completions table for matching habit_id for current_date and deletes that row
4. BE returns a message that the habit_id has been marked incomplete for today's date

**error/edge cases**

- what if the there isn't an existing habit_id that matches the user? (doesn't exist / belongs to another user) -> raise an HTTP 404 error that a matching habit_id can not be found
  - how would we know? BE queries habits table for a row where habit_id and user_id both match
  - if this returns nothing, that means there isn't an existing habit_it
- what if the user is trying to mark an incomplete habit incomplete again? ana what should happen if a user tries to "unmark" a habit that was never marked complete today in the first place? -> raise an HTTP 404 error that the habit is already marked incomplete
  - how would we know? 0 rows are affected from the completions table after the DELETE query which means no rows were deleted
- What if the user tries to mark a habit incomplete from a past date? -> not possible bc the route's DELETE query is hardcoded to `completion_date = CURRENT_DATE`, with no parameter anywhere that lets a client specify a different date. This isn't a validation check rejecting bad input but rather it prevents the user's capability to target a past date.

### "Delete" a habit

Sets the habit's is_active flag from True to False

### See all habits

**main flow**

1. User sends a GET/habits request along with token that has user id, user also specifies if they want to see complete habits only, incomplete habits only or both
2. BE filters DB for user specific habits
3. BE returns list of habits which will include their habit_id, content, date_created

**errors/edge cases**

- missing token/invalid token? -> return an error
- missing habit type filter (complete only, incomplete only etc) -> return all habits
- invalid habit type filter -> reject with an error
- network issues -> return an error instead of silently pretending it worked
- BE returns all habits regardless of user -> issue with querying the DB or potentially issue with the way habits are getting saved
- what happens if user has thousands of habits? -> implement pagination so that not all of them are returned at once?
- what happens if user has no habits? -> return empty list

## What can go wrong when...

- creating a new user
  - username is not unique -> this is enforced by the db schema via UNIQUE
  - manually include the user_id -> enforced by schema via "GENERATED ALWAYS AS IDENTITY" which makes postgres auto generate it and also spits out an error if we try to override/provide a user_id
- creating a habit:
  - habit doesn't get saved properly to db bc of network errors? db errors?
  - new habit is missing required fields so shouldn't be saved
-
