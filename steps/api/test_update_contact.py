"""PUT vs PATCH update semantics for contacts."""

from pytest_bdd import scenarios, when, then

from support.aop import log_step


scenarios("api/update_contact.feature")


@when("I PUT the contact with modified data and fewer optional fields")
@log_step
def put_contact(api_client, contact_ref):
    # fields omitted from PUT should become null on the server
    put_data = {
        "firstName": "Robert",
        "lastName": "Weir",
        "email": "robert@dead.net",
        # phone, city, country intentionally omitted
    }
    contact_id = contact_ref["contact_id"]
    ep = api_client.registry.by_name("Update Contact (PUT)")
    response = api_client.call_endpoint(ep, data=put_data, path_params={"id": contact_id})
    assert response.status == 200
    contact_ref["put_response"] = response.json()
    contact_ref["put_data"] = put_data


@then("all sent fields are updated")
@log_step
def verify_put_fields(contact_ref):
    result = contact_ref["put_response"]
    for field, expected in contact_ref["put_data"].items():
        assert result[field] == expected, (
            f"PUT field '{field}': expected '{expected}', got '{result[field]}'"
        )


@then("omitted optional fields are null")
@log_step
def verify_omitted_fields_null(contact_ref):
    result = contact_ref["put_response"]
    for field in ["phone", "city", "country"]:
        assert result.get(field) is None, (
            f"Omitted field '{field}' should be null, got '{result.get(field)}'"
        )


@when("I PATCH the contact with only a new first name")
@log_step
def patch_contact(api_client, contact_ref):
    contact_id = contact_ref["contact_id"]
    ep = api_client.registry.by_name("Update Contact (PATCH)")
    response = api_client.call_endpoint(ep, data={"firstName": "Bobby"}, path_params={"id": contact_id})
    assert response.status == 200
    contact_ref["patch_response"] = response.json()


@then("the first name is updated")
@log_step
def verify_patch_first_name(contact_ref):
    assert contact_ref["patch_response"]["firstName"] == "Bobby"


@then("other fields remain unchanged")
@log_step
def verify_other_fields_unchanged(contact_ref):
    # PATCH should preserve fields not in the payload
    result = contact_ref["patch_response"]
    assert result["lastName"] == "Weir"
    assert result["email"] == "robert@dead.net"
