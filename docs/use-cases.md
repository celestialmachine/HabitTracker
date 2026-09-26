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
4. BE returns the newly created habit as a habit_id and date_created

**error/edge cases**

- what happens if habit content is invalid (e.g. empty or null) -> return an error (e.g. "missing habit content") instead of saving a blank habit
- what if the habit content is really long? -> DB restricts content limit via VARCHAR(255)
- what if DB fails to write (e.g. network issues etc) -> return an error (e.g. "Network issue, please try again later") instead of silently pretending it worked
- saving habit to wrong user due to missing token/invalid token? -> BE should reject request
- can user create two habits with same content? -> no, DB requires habits to be unique

### Mark a habit as complete for the current date

### Mark a habit as incomplete for the current date

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
