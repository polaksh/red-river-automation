"""Root fixtures -- the DI container for the test framework."""

import logging
import uuid

import pytest

from support.config import CONFIG
from support.traced import TracedPage, TracedAPIClient
from support.api_discovery import EndpointRegistry


def pytest_configure(config):
    import os
    import platform
    os.makedirs(CONFIG.log_dir, exist_ok=True)

    file_handler = logging.FileHandler(CONFIG.log_file, mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)-14s %(message)s", datefmt="%H:%M:%S")
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)-14s %(message)s",
        datefmt="%H:%M:%S",
    )

    # Log execution config at the top of every run
    session_log = logging.getLogger("session")
    browser = (config.getoption("--browser", default=None) or [None])[0] or CONFIG.ui_browsers[0]
    headed = config.getoption("--headed", default=False)
    session_log.info("\n%s", "\n".join([
        "=" * 70,
        "  RED RIVER TEST AUTOMATION",
        f"  Browser:  {browser}",
        f"  Headed:   {headed}",
        f"  Platform: {platform.system()} {platform.release()}",
        f"  Python:   {platform.python_version()}",
        f"  Config:   {CONFIG.ui_base_url} (UI) / {CONFIG.api_base_url} (API)",
        "=" * 70,
    ]))


_scenario_logger = logging.getLogger("scenario")


def pytest_bdd_before_scenario(request, feature, scenario):
    banner = f"{'=' * 70}\n  FEATURE:  {feature.name}\n  SCENARIO: {scenario.name}\n{'=' * 70}"
    _scenario_logger.info("\n%s", banner)


def pytest_bdd_after_scenario(request, feature, scenario):
    _scenario_logger.info("--- END: %s / %s ---\n", feature.name, scenario.name)


@pytest.fixture
def traced_page(page):
    page.set_default_timeout(CONFIG.ui_default_timeout_ms)
    return TracedPage(page)


@pytest.fixture(scope="session")
def api_registry():
    return EndpointRegistry.discover()


@pytest.fixture
def api_client(playwright, api_registry):
    """Starts unauthenticated; set .token or use registered_user fixture."""
    context = playwright.request.new_context(base_url=CONFIG.api_base_url)
    client = TracedAPIClient(context, registry=api_registry)
    yield client
    client.dispose()


@pytest.fixture
def registered_user(api_client):
    """Throwaway user -- auto-auths the api_client, cleaned up after test."""
    unique = uuid.uuid4().hex[:8]
    user_data = {
        "firstName": "Test",
        "lastName": f"User{unique}",
        "email": f"test_{unique}@example.com",
        "password": "TestPass123!",
    }

    reg = api_client.registry
    response = api_client.call_endpoint(reg.by_name("Add User"), data=user_data)
    assert response.status == 201, f"User signup failed: {response.text()}"
    body = response.json()

    api_client.token = body["token"]

    credentials = {
        "first_name": user_data["firstName"],
        "last_name": user_data["lastName"],
        "email": user_data["email"],
        "password": user_data["password"],
        "token": body["token"],
    }

    yield credentials

    api_client.call_endpoint(reg.by_name("Delete User"))
