Feature: Delete Contact and Authorization API
  As an authenticated user
  I want to delete contacts and verify authorization is enforced
  So that I can trust the API's security

  Scenario: Delete a contact and verify it is gone
    Given I am an authenticated API user
    And I create a contact
    When I delete the contact
    Then the delete response confirms removal
    When I try to get the deleted contact
    Then I receive a 404 response

  Scenario: Unauthorized access is rejected
    When I request contacts without an auth token
    Then I receive a 401 response with an authentication error
