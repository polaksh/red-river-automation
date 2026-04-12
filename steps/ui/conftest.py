"""Shared UI steps and cross-browser support.

Browser selection is config-driven (config.yaml: ui.browsers).
When multiple browsers are listed, the Makefile/PowerShell script runs
pytest once per browser. Within a single run, browser_name is a plain
fixture that reads from config or the --browser CLI flag.
"""

import pytest
from pytest_bdd import given

from support.config import CONFIG
from support.aop import log_step
from pages.home_page import HomePage


@pytest.fixture(scope="session")
def browser_name(pytestconfig):
    """Which browser to use — CLI flag takes priority, then config default."""
    cli_browsers = pytestconfig.getoption("--browser", default=[])
    if cli_browsers:
        return cli_browsers[0]
    return CONFIG.ui_browsers[0]


@given("I am on the home page", target_fixture="home_page")
@log_step
def on_home_page(traced_page):
    home = HomePage(traced_page)
    home.navigate_home()
    return home
