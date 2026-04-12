Feature: Add to Cart and Complete Purchase
  As a shopper on demoblaze.com
  I want to add a product to my cart and check out
  So that I can buy items from the store

  Scenario: Full purchase flow from product selection to confirmation
    Given I am on the home page
    When I click on the product "Samsung galaxy s6"
    Then I see the product detail page with name "Samsung galaxy s6"
    When I add the product to the cart
    And I navigate to the cart
    Then the cart contains "Samsung galaxy s6"
    When I place an order with my details
    Then I see a purchase confirmation message
