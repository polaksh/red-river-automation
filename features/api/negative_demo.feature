Feature: Negative Test Demo (API)
  Demonstrates that the framework properly captures and reports API test failures.
  This scenario is EXPECTED TO FAIL — it validates failure handling, not API behavior.

  Review the test output to see:
    - TracedAPIClient logs showing the HTTP call, endpoint name, and 404 status
    - Step-level logs showing which step failed
    - Clear assertion message with expected vs actual status code

  HOW TO FIX: Change the Then step to assert a 404 instead of expecting contact
  details. The ID "000000000000000000000000" does not exist, so the API returns 404.
  Replace: Then the response contains the contact details
  With:    Then the response status is 404

  @expected_failure
  Scenario: Intentional failure fetching a nonexistent contact
    Given I am an authenticated API user
    When I get the contact with ID "000000000000000000000000"
    Then the response status is 404
