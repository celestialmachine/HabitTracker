# TODO: eventually i want to test my habits endpoints but i'm not
# sure how to without creating a bunch of dummy users/habits and
# polluting my DB...
import pytest
from fastapi import HTTPException


def test_mark_habit_incomplete_success():
    pass


def test_mark_habit_incomplete_invalid_habit():
    pass


def test_mark_habit_incomplete_nothing_to_unmark():
    pass


"""
## Tests
# successful deletion (complete -> incomplete)
# habit not found (doesn't exit / belongs to a diff user)
# incomplete habit  (incomplete -> incomplete)


"""
