"""Category filtering on the product grid."""

import pytest
from pytest_bdd import scenarios, when, then, parsers

from support.aop import log_step


scenarios("ui/browse_products.feature")

# known products per category -- subset, just enough to verify filtering works
KNOWN_PHONES = {"Samsung galaxy s6", "Nokia lumia 1520", "Nexus 6",
                "Samsung galaxy s7", "Iphone 6 32gb", "Sony xperia z5",
                "HTC One M9"}
KNOWN_LAPTOPS = {"Sony vaio i5", "Sony vaio i7", "MacBook air",
                 "Dell i7 8gb", "2017 Dell 15.6 Inch", "MacBook Pro"}
KNOWN_MONITORS = {"Apple monitor 24", "ASUS Full HD"}


@pytest.fixture
def browse_state():
    return {}


@when(parsers.parse('I select the "{category}" category'))
@log_step
def select_category(home_page, browse_state, category):
    home_page.select_category(category)
    browse_state["current_products"] = home_page.product_names()


@then("only phone products are displayed")
@log_step
def verify_phones(browse_state):
    products = set(browse_state["current_products"])
    assert products, "Product list should not be empty"
    assert products.issubset(KNOWN_PHONES), (
        f"Non-phone products found: {products - KNOWN_PHONES}"
    )


@then("only laptop products are displayed")
@log_step
def verify_laptops(browse_state):
    products = set(browse_state["current_products"])
    assert products, "Product list should not be empty"
    assert products.issubset(KNOWN_LAPTOPS), (
        f"Non-laptop products found: {products - KNOWN_LAPTOPS}"
    )


@then("only monitor products are displayed")
@log_step
def verify_monitors(browse_state):
    products = set(browse_state["current_products"])
    assert products, "Product list should not be empty"
    assert products.issubset(KNOWN_MONITORS), (
        f"Non-monitor products found: {products - KNOWN_MONITORS}"
    )
