Feature: User Authentication on Product Store
  As a visitor to demoblaze.com
  I want to sign up, log in, and log out
  So that I can manage my account

  Scenario: Full authentication lifecycle
    Given I am on the home page
    When I sign up with a unique username and password
    Then I see a signup success alert
    When I log in with those credentials
    Then I see my username in the navbar
    And the logout link is visible
    When I log out
    Then the login and signup links reappear
