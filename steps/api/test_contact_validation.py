"""Contact validation — missing fields, invalid data."""

from pytest_bdd import scenarios


scenarios("api/contact_validation.feature")

# All steps are generic (conftest.py):
#   "I call {endpoint} with:" — sends data table
#   "the response status is {N}" — asserts status code
