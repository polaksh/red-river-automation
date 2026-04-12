"""Negative test demo -- intentionally fails. See the feature file for details."""

from pytest_bdd import scenarios, when, parsers

from support.aop import log_step


scenarios("api/negative_demo.feature")


@when(parsers.parse('I get the contact with ID "{contact_id}"'),
      target_fixture="api_response")
@log_step
def get_nonexistent_contact(api_client, contact_id):
    ep = api_client.registry.by_name("Get Contact")
    response = api_client.call_endpoint(ep, path_params={"id": contact_id})
    return {
        "response": response,
        "sent_data": {},
        "endpoint": ep,
        "body": response.json() if response.status < 400 else None,
    }
