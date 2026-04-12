"""Negative test demo -- intentionally fails. See the feature file for details."""

import pytest
from pytest_bdd import scenarios, when, then, parsers

from support.aop import log_step


scenarios("api/negative_demo.feature")


@pytest.fixture
def negative_state():
    return {}


@when(parsers.parse('I get the contact with ID "{contact_id}"'))
@log_step
def get_nonexistent_contact(api_client, negative_state, contact_id):
    ep = api_client.registry.by_name("Get Contact")
    response = api_client.call_endpoint(ep, path_params={"id": contact_id})
    negative_state["response"] = response


@then("the response contains the contact details")
@log_step
def verify_contact_details(negative_state):
    # intentionally wrong -- will 404
    response = negative_state["response"]
    assert response.status == 200, (
        f"Expected 200 but got {response.status}: {response.text()}"
    )
