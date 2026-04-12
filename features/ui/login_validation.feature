Feature: Login Validation
  As a visitor to demoblaze.com
  I want clear feedback when I enter wrong credentials
  So that I know my login attempt failed

  Scenario: Login with invalid credentials shows error
    Given I am on the home page
    When I attempt to log in with username "nonexistent_user_xyz" and password "wrongpass"
    Then I see a login failure alert

  Scenario: Login with empty credentials shows error
    Given I am on the home page
    When I attempt to log in with empty credentials
    Then I see a login failure alert
