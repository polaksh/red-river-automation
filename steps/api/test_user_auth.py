"""Auth lifecycle: register -> login -> profile -> logout."""

import uuid

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from support.aop import log_step


scenarios("api/user_auth.feature")


@pytest.fixture
def auth_state():
    return {}


@given("I register a new user via the API", target_fixture="auth_state")
@log_step
def register_new_user(api_client):
    unique = uuid.uuid4().hex[:8]
    user_data = {
        "firstName": "Auth",
        "lastName": f"Test{unique}",
        "email": f"authtest_{unique}@example.com",
        "password": "SecurePass123!",
    }
    reg = api_client.registry
    response = api_client.call_endpoint(reg.by_name("Add User"), data=user_data)
    assert response.status == 201, f"Signup failed: {response.text()}"

    body = response.json()
    return {
        "user_data": user_data,
        "signup_token": body["token"],
        "user_id": body["user"]["_id"],
    }


@when("I login with those credentials")
@log_step
def login_with_credentials(api_client, auth_state):
    reg = api_client.registry
    response = api_client.call_endpoint(reg.by_name("Log In User"), data={
        "email": auth_state["user_data"]["email"],
        "password": auth_state["user_data"]["password"],
    })
    assert response.status == 200, f"Login failed: {response.text()}"

    body = response.json()
    auth_state["login_token"] = body["token"]
    api_client.token = body["token"]


@then("I receive a valid auth token")
@log_step
def verify_auth_token(auth_state):
    assert auth_state["login_token"], "Token should not be empty"


@when("I request my user profile")
@log_step
def request_user_profile(api_client, auth_state):
    reg = api_client.registry
    response = api_client.call_endpoint(reg.by_name("Get User Profile"))
    assert response.status == 200, f"Get profile failed: {response.text()}"
    auth_state["profile"] = response.json()


@then("the profile matches my registration data")
@log_step
def verify_profile_matches(auth_state):
    profile = auth_state["profile"]
    user_data = auth_state["user_data"]
    assert profile["firstName"] == user_data["firstName"]
    assert profile["lastName"] == user_data["lastName"]
    assert profile["email"] == user_data["email"]


@when("I logout")
@log_step
def logout(api_client, auth_state):
    reg = api_client.registry
    response = api_client.call_endpoint(reg.by_name("Log Out User"))
    assert response.status == 200


@then("the token is invalidated")
@log_step
def verify_token_invalidated(api_client):
    # same token should now 401
    reg = api_client.registry
    response = api_client.call_endpoint(reg.by_name("Get User Profile"))
    assert response.status == 401, "Token should be invalidated after logout"
