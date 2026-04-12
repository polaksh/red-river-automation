"""Full purchase flow: browse -> add to cart -> checkout."""

import pytest
from pytest_bdd import scenarios, when, then, parsers

from support.aop import log_step
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.modals import PlaceOrderModal


scenarios("ui/purchase.feature")


@pytest.fixture
def purchase_state():
    return {}


@when(parsers.parse('I click on the product "{product_name}"'))
@log_step
def click_product(home_page, purchase_state, product_name):
    home_page.click_product(product_name)
    purchase_state["expected_product"] = product_name


@then(parsers.parse('I see the product detail page with name "{expected_name}"'))
@log_step
def verify_product_page(traced_page, purchase_state, expected_name):
    product = ProductPage(traced_page)
    purchase_state["product_page"] = product
    assert product.product_name() == expected_name


@when("I add the product to the cart")
@log_step
def add_to_cart(purchase_state):
    purchase_state["product_page"].add_to_cart()


@when("I navigate to the cart")
@log_step
def navigate_to_cart(traced_page, purchase_state):
    cart_page = CartPage(traced_page)
    cart_page.navigate_to_cart()
    cart_page.wait_for_cart_loaded()
    purchase_state["cart"] = cart_page


@then(parsers.parse('the cart contains "{product_name}"'))
@log_step
def verify_cart_contents(purchase_state, product_name):
    cart = purchase_state["cart"]
    items = cart.item_names()
    assert product_name in items, f"Expected '{product_name}' in cart, got {items}"


@when("I place an order with my details")
@log_step
def place_order(traced_page, purchase_state):
    modal = PlaceOrderModal(traced_page)
    modal.open()
    modal.fill(
        name="Test Buyer",
        country="USA",
        city="San Francisco",
        card="4111111111111111",
        month="12",
        year="2025",
    )
    modal.submit()
    purchase_state["order_modal"] = modal


@then("I see a purchase confirmation message")
@log_step
def verify_confirmation(purchase_state):
    modal = purchase_state["order_modal"]
    title = modal.confirmation_title()
    assert "Thank you" in title, f"Expected thank you message, got: {title}"
    modal.dismiss_confirmation()
