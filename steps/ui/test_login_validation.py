"""Login validation — wrong and empty credentials."""

import pytest
from pytest_bdd import scenarios, when, then, parsers

from support.aop import log_step
from pages.modals import LoginModal


scenarios("ui/login_validation.feature")


@pytest.fixture
def login_state():
    return {}


def _attempt_login(traced_page, login_state, username, password):
    """Shared helper — try to log in and capture any alert dialogs."""
    dialog_messages = []

    def handle_dialog(dialog):
        dialog_messages.append(dialog.message)
        dialog.accept()

    traced_page.on("dialog", handle_dialog)

    modal = LoginModal(traced_page)
    modal.open()
    modal.fill(username, password)
    modal.submit()

    traced_page.wait_for_timeout(2000)
    traced_page.remove_listener("dialog", handle_dialog)
    login_state["messages"] = dialog_messages


@when(parsers.parse('I attempt to log in with username "{username}" and password "{password}"'))
@log_step
def attempt_login_with_creds(traced_page, login_state, username, password):
    _attempt_login(traced_page, login_state, username, password)


@when("I attempt to log in with empty credentials")
@log_step
def attempt_login_empty(traced_page, login_state):
    _attempt_login(traced_page, login_state, "", "")


@then("I see a login failure alert")
@log_step
def verify_login_failure(login_state):
    messages = login_state["messages"]
    assert len(messages) > 0, "Expected an error alert for invalid credentials"
    # demoblaze shows "Wrong password." or "User does not exist."
    msg = messages[0].lower()
    assert "wrong" in msg or "not exist" in msg or "please" in msg, (
        f"Expected login error, got: {messages[0]}"
    )
