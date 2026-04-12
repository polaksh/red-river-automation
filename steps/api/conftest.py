"""Shared API steps and the contact_factory fixture."""

import pytest
from pytest_bdd import given, when, then, parsers

from support.aop import log_step


_CONTACT_DEFAULTS = {
    "firstName": "Test",
    "lastName": "Contact",
}

_CONTACT_FULL = {
    "firstName": "Jerry",
    "lastName": "Garcia",
    "birthdate": "1942-08-01",
    "email": "jerry@grateful.dead",
    "phone": "8005550001",
    "street1": "710 Ashbury St",
    "street2": "Apt 2",
    "city": "San Francisco",
    "stateProvince": "CA",
    "postalCode": "94117",
    "country": "USA",
}


@pytest.fixture
def contact_factory(api_client):
    """Creates a contact and returns {contact_id, response, contact, sent_data}."""
    def _create(full: bool = False, **overrides) -> dict:
        base = dict(_CONTACT_FULL if full else _CONTACT_DEFAULTS)
        base.update(overrides)

        ep = api_client.registry.by_name("Add Contact")
        response = api_client.call_endpoint(ep, data=base)
        assert response.status == 201, f"Create contact failed: {response.text()}"
        body = response.json()

        return {
            "contact_id": body["_id"],
            "response": response,
            "contact": body,
            "sent_data": base,
        }

    return _create


# -- Shared state for generic steps -------------------------------------------

@pytest.fixture
def api_response():
    """Mutable holder for the last API response — used by generic steps."""
    return {}


# -- Auth step -----------------------------------------------------------------

@given("I am an authenticated API user")
@log_step
def authenticated_user(registered_user):
    # registered_user fixture (root conftest) handles signup + auth
    pass


# -- Contact creation steps (specific) ----------------------------------------

@given("I create a contact", target_fixture="contact_ref")
@log_step
def given_create_contact(contact_factory):
    return contact_factory()


@when("I create a contact", target_fixture="contact_ref")
@log_step
def when_create_contact(contact_factory):
    return contact_factory()


@given("I create a contact with full details", target_fixture="contact_ref")
@log_step
def given_create_contact_full(contact_factory):
    return contact_factory(full=True)


@when("I create a contact with full details", target_fixture="contact_ref")
@log_step
def when_create_contact_full(contact_factory):
    return contact_factory(full=True)


# -- Contact lookup (find-or-create) -------------------------------------------
# The feature file specifies fields, the step searches the API for a match.
# If no match, creates one. Either way, contact_ref is populated.

def _find_contact(api_client, match_fields: dict) -> dict | None:
    """Search the contact list for one matching all provided fields."""
    ep = api_client.registry.by_name("Get Contact List")
    response = api_client.call_endpoint(ep)
    if response.status != 200:
        return None
    for contact in response.json():
        if all(contact.get(k) == v for k, v in match_fields.items()):
            return contact
    return None


@given("a contact exists with:", target_fixture="contact_ref")
@log_step
def ensure_contact_exists(api_client, datatable):
    fields = _table_to_dict(datatable)
    existing = _find_contact(api_client, fields)
    if existing:
        return {
            "contact_id": existing["_id"],
            "contact": existing,
            "sent_data": fields,
        }
    # not found — create it
    ep = api_client.registry.by_name("Add Contact")
    response = api_client.call_endpoint(ep, data=fields)
    assert response.status == 201, f"Create contact failed: {response.text()}"
    body = response.json()
    return {
        "contact_id": body["_id"],
        "contact": body,
        "sent_data": fields,
    }


# -- Generic data-driven steps ------------------------------------------------
# These let feature files drive API calls by endpoint name + data table,
# using the discovery registry to resolve method/path/fields.
#
# Example feature usage:
#   When I call "Add Contact" with:
#     | firstName | Jerry          |
#     | lastName  | Garcia         |
#   Then the response status is 201

def _table_to_dict(datatable) -> dict:
    """Convert a pytest-bdd vertical datatable ([[key, val], ...]) to a dict."""
    return {row[0]: row[1] for row in datatable}


@when(parsers.parse('I call "{endpoint_name}" with:'),
      target_fixture="api_response")
@log_step
def call_endpoint_with_data(api_client, endpoint_name, datatable):
    """Look up the endpoint by name, send the data from the table."""
    endpoint = api_client.registry.by_name(endpoint_name)
    data = _table_to_dict(datatable)
    response = api_client.call_endpoint(endpoint, data=data)
    return {
        "response": response,
        "sent_data": data,
        "endpoint": endpoint,
        "body": response.json() if response.status < 400 else None,
    }


@when(parsers.parse('I call "{endpoint_name}"'),
      target_fixture="api_response")
@log_step
def call_endpoint_no_data(api_client, endpoint_name):
    """Call an endpoint that takes no body (GET, DELETE, etc.)."""
    endpoint = api_client.registry.by_name(endpoint_name)
    response = api_client.call_endpoint(endpoint)
    return {
        "response": response,
        "sent_data": {},
        "endpoint": endpoint,
        "body": response.json() if response.status < 400 else None,
    }


@when(parsers.parse('I call "{endpoint_name}" for contact "{contact_id}"'),
      target_fixture="api_response")
@log_step
def call_endpoint_for_contact(api_client, endpoint_name, contact_id):
    """Call an endpoint with a path parameter (e.g., GET /contacts/:id)."""
    endpoint = api_client.registry.by_name(endpoint_name)
    response = api_client.call_endpoint(endpoint, path_params={"id": contact_id})
    return {
        "response": response,
        "sent_data": {},
        "endpoint": endpoint,
        "body": response.json() if response.status < 400 else None,
    }


@when(parsers.parse('I call "{endpoint_name}" for that contact'),
      target_fixture="api_response")
@log_step
def call_endpoint_for_that_contact(api_client, endpoint_name, request):
    """Call an endpoint for the contact from the most recent create/lookup.

    Checks contact_ref first (from Given steps), then api_response
    (from When "I call Add Contact" steps).
    """
    # find the contact ID from whichever fixture has it
    contact_ref = request.getfixturevalue("contact_ref") if "contact_ref" in request.fixturenames else None
    api_resp = request.getfixturevalue("api_response") if "api_response" in request.fixturenames else None

    if contact_ref and contact_ref.get("contact_id"):
        contact_id = contact_ref["contact_id"]
        sent_data = contact_ref.get("sent_data", {})
    elif api_resp and api_resp.get("body", {}).get("_id"):
        contact_id = api_resp["body"]["_id"]
        sent_data = api_resp.get("sent_data", {})
    else:
        raise ValueError("No contact available — use a create or lookup step first")

    endpoint = api_client.registry.by_name(endpoint_name)
    response = api_client.call_endpoint(
        endpoint, path_params={"id": contact_id}
    )
    return {
        "response": response,
        "sent_data": sent_data,
        "endpoint": endpoint,
        "body": response.json() if response.status < 400 else None,
    }


@when("I call the same endpoint for the last created contact",
      target_fixture="api_response")
@log_step
def call_endpoint_for_last_contact(api_client, api_response):
    """Re-call the previous endpoint but targeting the last created contact."""
    endpoint = api_client.registry.by_name("Get Contact")
    contact_id = api_response["body"]["_id"]
    response = api_client.call_endpoint(endpoint, path_params={"id": contact_id})
    return {
        "response": response,
        "sent_data": api_response.get("sent_data", {}),
        "endpoint": endpoint,
        "body": response.json() if response.status < 400 else None,
    }


# -- Generic response assertions -----------------------------------------------

@then(parsers.parse("the response status is {status:d}"))
@log_step
def verify_response_status(api_response, status):
    assert api_response["response"].status == status, (
        f"Expected {status}, got {api_response['response'].status}"
    )


@then("the response has an ID")
@log_step
def verify_response_has_id(api_response):
    assert api_response["body"].get("_id"), "Response should contain an _id"


@then("the response fields match what I sent")
@log_step
def verify_response_matches_sent(api_response):
    body = api_response["body"]
    for field, expected in api_response["sent_data"].items():
        assert body[field] == expected, (
            f"Field '{field}': expected '{expected}', got '{body[field]}'"
        )
