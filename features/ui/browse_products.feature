Feature: Browse Products by Category
  As a shopper on demoblaze.com
  I want to filter products by category
  So that I can find items I'm interested in

  Scenario: Category filtering shows correct products
    Given I am on the home page
    When I select the "Phones" category
    Then only phone products are displayed
    When I select the "Laptops" category
    Then only laptop products are displayed
    When I select the "Monitors" category
    Then only monitor products are displayed
