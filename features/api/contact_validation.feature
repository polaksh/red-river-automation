Feature: Contact Validation API
  As an authenticated user
  I want the API to reject invalid contact data
  So that data integrity is maintained

  Scenario: Missing required fields returns validation error
    Given I am an authenticated API user
    When I call "Add Contact" with:
      | email | incomplete@test.com |
    Then the response status is 400

  Scenario: Invalid phone number is rejected
    Given I am an authenticated API user
    When I call "Add Contact" with:
      | firstName | Test        |
      | lastName  | User        |
      | phone     | not-a-phone |
    Then the response status is 400
