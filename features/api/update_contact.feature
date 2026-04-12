Feature: Update Contact API
  As an authenticated user
  I want to update contacts using PUT and PATCH
  So that I can modify contact information

  Scenario: Full update with PUT and partial update with PATCH
    Given I am an authenticated API user
    And I create a contact
    When I PUT the contact with modified data and fewer optional fields
    Then all sent fields are updated
    And omitted optional fields are null
    When I PATCH the contact with only a new first name
    Then the first name is updated
    And other fields remain unchanged
