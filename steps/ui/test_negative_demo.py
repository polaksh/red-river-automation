"""Negative test demo -- intentionally asserts the wrong price."""

import pytest
from pytest_bdd import scenarios, when, then, parsers

from support.aop import log_step
from pages.home_page import HomePage
from pages.product_page import ProductPage


scenarios("ui/negative_demo.feature")


@when(parsers.parse('I click on the product "{product_name}"'))
@log_step
def click_product(home_page, product_name):
    home_page.click_product(product_name)


@then(parsers.parse('the product price is "{expected_price}"'))
@log_step
def verify_wrong_price(traced_page, expected_price):
    # intentionally wrong -- actual price is $360
    product = ProductPage(traced_page)
    actual_price = product.product_price()
    assert expected_price in actual_price, (
        f"Expected price '{expected_price}' but got '{actual_price}'"
    )
