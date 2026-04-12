"""Create and read contact — uses generic data-driven steps from conftest."""

from pytest_bdd import scenarios


scenarios("api/create_contact.feature")

# All steps are generic (conftest.py):
#   "I call {endpoint} with:" — sends data table as POST body
#   "the response status is {N}" — asserts status code
#   "the response has an ID" — checks _id field
#   "I call the same endpoint for the last created contact" — GET by ID
#   "the response fields match what I sent" — field-by-field assertion
#   "I call {endpoint}" — no-body call (GET list)
