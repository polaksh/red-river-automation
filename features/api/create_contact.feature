Feature: Create and Read Contact API
  As an authenticated user
  I want to create contacts and retrieve them
  So that I can manage my contact list

  Scenario: Create a contact and read it back
    Given I am an authenticated API user
    When I call "Add Contact" with:
      | firstName     | Jerry           |
      | lastName      | Garcia          |
      | birthdate     | 1942-08-01      |
      | email         | jerry@dead.net  |
      | phone         | 8005550001      |
      | street1       | 710 Ashbury St  |
      | street2       | Apt 2           |
      | city          | San Francisco   |
      | stateProvince | CA              |
      | postalCode    | 94117           |
      | country       | USA             |
    Then the response status is 201
    And the response has an ID
    When I call "Get Contact" for that contact
    Then the response fields match what I sent
    When I call "Get Contact List"
    Then the response status is 200
