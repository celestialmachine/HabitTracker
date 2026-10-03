# Habit Tracker

## Overview

- supports multiple users
- a user can:
  - create a user account
  - add a new habit
  - get their habits
  - get a habit's current streak (could be <= longest streak)
  - get a habit's longest streak
  - mark a habit as completed for the day
  - mark a habit as incomplete for the day
  - delete a habit (marks it as inactive)
- a user can not:
  - mark a complete habit complete again
  - update contents of a habit -> bc if they could, it would cause problems later on when calculating streaks?
  - update habit completion status for dates that have passed or future dates
  - access/update other user's habits

## Features

## Tech-Stack

- Backend: Python
- Database: PostgreSQL
- Testing: Pytest
- Security: JWT, Bcrypt

## How to Run Locally

## Summary of Key Learnings

## Ideas for Future Improvement

- allowing users to
  - update habit completion status for dates that have passed or future dates
