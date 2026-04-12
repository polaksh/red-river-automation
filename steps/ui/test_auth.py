"""Signup -> login -> logout flow on demoblaze."""

import uuid

import pytest
from pytest_bdd import scenarios, when, then

from support.aop import log_step
from pages.modals import SignupModal, LoginModal


scenarios("ui/auth.feature")


@pytest.fixture
def auth_state():
    return {}


@when("I sign up with a unique username and password")
@log_step
def sign_up(traced_page, auth_state):
    unique = uuid.uuid4().hex[:8]
    username = f"testuser_{unique}"
    password = "TestPass123!"
    auth_state["username"] = username
    auth_state["password"] = password

    # demoblaze shows a browser alert on signup
    dialog_messages = []

    def handle_dialog(dialog):
        dialog_messages.append(dialog.message)
        dialog.accept()

    traced_page.on("dialog", handle_dialog)

    modal = SignupModal(traced_page)
    modal.open()
    modal.fill(username, password)
    modal.submit()

    traced_page.wait_for_timeout(2000)
    traced_page.remove_listener("dialog", handle_dialog)
    auth_state["signup_messages"] = dialog_messages


@then("I see a signup success alert")
@log_step
def verify_signup_success(auth_state):
    messages = auth_state["signup_messages"]
    assert len(messages) > 0, "Expected a signup alert"
    assert "Sign up successful" in messages[0] or "successful" in messages[0].lower()


@when("I log in with those credentials")
@log_step
def log_in(traced_page, auth_state):
    modal = LoginModal(traced_page)
    modal.open()
    modal.fill(auth_state["username"], auth_state["password"])
    modal.submit()
    modal.wait_for_logged_in()


@then("I see my username in the navbar")
@log_step
def verify_username_in_navbar(traced_page, auth_state):
    welcome_text = traced_page.text_content("#nameofuser")
    assert auth_state["username"] in welcome_text


@then("the logout link is visible")
@log_step
def verify_logout_visible(traced_page):
    modal = LoginModal(traced_page)
    assert modal.is_logout_visible()


@when("I log out")
@log_step
def log_out(traced_page):
    modal = LoginModal(traced_page)
    modal.logout()


@then("the login and signup links reappear")
@log_step
def verify_login_signup_visible(traced_page):
    assert traced_page.is_visible("#login2"), "Login link should be visible"
    assert traced_page.is_visible("#signin2"), "Signup link should be visible"
