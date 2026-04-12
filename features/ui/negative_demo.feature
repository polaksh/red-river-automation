Feature: Negative Test Demo (UI)
  Demonstrates that the framework properly captures and reports UI test failures.
  This scenario is EXPECTED TO FAIL — it validates failure handling, not site behavior.

  Review the test output to see:
    - Step-level logs showing which step failed and how long it took
    - TracedPage logs showing every browser interaction leading to the failure
    - Clear assertion message with expected vs actual values

  HOW TO FIX: Change the expected price from "$999.99" to "$360"
  in the Then step below. The Samsung Galaxy S6 costs $360 on demoblaze.com.

  @expected_failure
  Scenario: Intentional assertion failure on product price
    Given I am on the home page
    When I click on the product "Samsung galaxy s6"
    Then the product price is "$999.99"
