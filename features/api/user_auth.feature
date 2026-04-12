Feature: User Authentication API
  As an API consumer
  I want to register, login, view my profile, and logout
  So that I can manage my account on the contact list app

  Scenario: Full user authentication lifecycle
    Given I register a new user via the API
    When I login with those credentials
    Then I receive a valid auth token
    When I request my user profile
    Then the profile matches my registration data
    When I logout
    Then the token is invalidated
