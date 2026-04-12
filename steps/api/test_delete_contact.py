"""Delete contact + unauthorized access scenarios."""

import pytest
from pytest_bdd import scenarios, when, then

from support.aop import log_step


scenarios("api/delete_contact.feature")


@pytest.fixture
def unauth_state():
    return {}


@when("I delete the contact")
@log_step
def delete_contact(api_client, contact_ref):
    contact_id = contact_ref["contact_id"]
    ep = api_client.registry.by_name("Delete Contact")
    response = api_client.call_endpoint(ep, path_params={"id": contact_id})
    contact_ref["delete_response"] = response


@then("the delete response confirms removal")
@log_step
def verify_delete_response(contact_ref):
    response = contact_ref["delete_response"]
    assert response.status == 200
    assert "deleted" in response.text().lower()


@when("I try to get the deleted contact")
@log_step
def get_deleted_contact(api_client, contact_ref):
    contact_id = contact_ref["contact_id"]
    ep = api_client.registry.by_name("Get Contact")
    contact_ref["get_response"] = api_client.call_endpoint(ep, path_params={"id": contact_id})


@then("I receive a 404 response")
@log_step
def verify_404(contact_ref):
    assert contact_ref["get_response"].status == 404


@when("I request contacts without an auth token", target_fixture="unauth_state")
@log_step
def request_without_auth(api_client):
    api_client.token = None
    ep = api_client.registry.by_name("Get Contact List")
    response = api_client.call_endpoint(ep)
    return {"response": response}


@then("I receive a 401 response with an authentication error")
@log_step
def verify_401(unauth_state):
    response = unauth_state["response"]
    assert response.status == 401
    body = response.json()
    assert body.get("error") == "Please authenticate."
