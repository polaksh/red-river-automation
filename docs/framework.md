# Automation Framework

- [Automation Framework](#automation-framework)
  - [Overview](#overview)
    - [Stack](#stack)
  - [Key Design Decisions](#key-design-decisions)
    - [Single framework for UI + API](#single-framework-for-ui--api)
    - [Cross-browser support](#cross-browser-support)
    - [Page Object Model for UI](#page-object-model-for-ui)
    - [Traced Wrappers - Automatic Interaction Logging](#traced-wrappers---automatic-interaction-logging)
    - [Browser Factory - Controlled Instantiation](#browser-factory---controlled-instantiation)
    - [API Client - Controlled Instantiation](#api-client---controlled-instantiation)
    - [API Discovery - Self-Documenting Client](#api-discovery---self-documenting-client)
    - [AOP: Decorators for Step-Level Concerns](#aop-decorators-for-step-level-concerns)
    - [IoC: Dependency Injection via Fixtures](#ioc-dependency-injection-via-fixtures)
    - [Fixture strategy](#fixture-strategy)
    - [Minimal arbitrary sleeps](#minimal-arbitrary-sleeps)


## Overview

With a heuristic approach to this assignment, a capable automation framework should provide for testing any layer of the application it meant to test.
It is not uncommon for an application to expose both a front-facing UI layer and a RESTful API underneath, which means a capable automation framework should support both UI automation and API testing,
Eventhough the assignment separates API testing from UI autoamtion, I took the liberty to support both in the same automation framework as if the API can server the UI layer.
Had this was an application with both layers, and not 2 separate testing sites, the same framework could:
1. leverage the API layer for bootstrapping the required state for UI tests
2. test the API layer iteslf, 
3. cover any given feature of the application to the depth of both layers, thus providing reports for all layers from the same test suite and same execution, as opposed to implementing test suites for the API with one framework/tool separated from the UI tests that are implemented with another framework/tool and have to consolidated reports and status from both

### Stack

| Component            | Choice                          | Why                                                              |
|----------------------|---------------------------------|------------------------------------------------------------------|
| Language             | Python 3.12+                    | Readable, strong ecosystem for testing                           |
| Dependency mgmt      | uv                              | Fast, modern Python package manager                              |
| Browser/API automation | Playwright                    | Single library for both UI and API testing                       |
| BDD framework        | pytest-bdd                      | Native pytest integration (fixtures, plugins, parallel, reports) |
| Assertions           | Python `assert` + pytest introspection | Clean, no extra dependency                                |
| Reporting            | pytest-html (or similar)        | Simple HTML report for review                                    |


## Key Design Decisions

### Single framework for UI + API
Playwright provides both `Browser` (UI) and `APIRequestContext` (HTTP). No need for a separate `requests`/`httpx` dependency. This keeps the framework unified - same fixtures, same config, same runner.

### Cross-browser support
Playwright supports Chromium, Firefox, and WebKit. The `pytest-playwright` plugin provides this out of the box - no code changes needed:
```bash
# single browser (default: chromium)
pytest

# multiple browsers in one run
pytest --browser chromium --browser firefox --browser webkit
```
All UI tests are browser-agnostic by design. Page objects use Playwright's standard API which works identically across engines.

### Page Object Model for UI
Demoblaze is heavily JS-driven: products load dynamically, all auth/contact forms are Bootstrap modals, pagination is JS-based.

Page objects contain **only behavior** (actions, waits). All CSS selectors live in `pages/locators.py` - frozen dataclasses, one per page. This separation means:
- **One file to edit**: when the UI changes, no hunting through page objects
- **IDE autocomplete**: `self.locators.username`, not a string key lookup
- **Typo detection**: misspell `self.locators.usernme` and the IDE catches it immediately
- **No runtime config parsing**: plain Python, zero magic

For example:
```python
# locators.py - the UI map, single source of truth
@dataclass(frozen=True)
class LoginModalLocators:
    username: str = "#loginusername"
    password: str = "#loginpassword"
    submit_btn: str = "#logInModal .btn-primary"

# modals.py - pure behavior, no selectors
class LoginModal:
    locators = LoginModalLocators()
    def fill(self, username, password):
        self._page.fill(self.locators.username, username)
```

Step definitions stay thin - they describe *what*, page objects handle *how*.

### Traced Wrappers - Automatic Interaction Logging

Inspired by the dynamic proxy pattern (Java/C#): a thin wrapper intercepts every browser/API call, logs it, and delegates to the real object. No manual log statements needed, the full call chain is visible automatically.

**Call chain:**
```
step definition → page object → TracedPage → Playwright Page
step definition → api_client  → TracedAPIClient → Playwright APIRequestContext
```

**`TracedPage`** - wraps Playwright `Page` via `__getattr__`. Intercepts action methods (`click`, `fill`, `goto`, `wait_for_selector`, etc.), logs before/after with args and timing, delegates to the real page. Steps and page objects use it exactly like a normal `Page` - same API, zero new abstractions.

```
[TracedPage] goto('https://www.demoblaze.com')
[TracedPage] click('#login2')
[TracedPage] fill('#loginusername', 'testuser')
[TracedPage] click('button:text("Log in")')
[TracedPage] wait_for_selector('#nameofuser') → 120ms
```

**`TracedAPIClient`** - same pattern for `APIRequestContext`. Logs method, URL, status code, timing:

```
[TracedAPI] POST /users → 201 (85ms)
[TracedAPI] GET /contacts → 200 (42ms)
[TracedAPI] DELETE /contacts/abc123 → 200 (38ms)
```

Both wrappers also handle error logging, without any explicit exception handling, they log the failure context (selector, URL, response body) before re-raising. This replaces the need for separate `@handle_errors` decorators on every step.

Both live in `support/traced.py`.

### Browser Factory - Controlled Instantiation

Browser creation is centralized in a factory fixture, not scattered across tests. The factory controls:
- **Browser type** - Chromium/Firefox/WebKit (cross-browser is controlled by the framework's [configuration file](../config.yaml)
- **Context options** - viewport size, locale, timezone, ignore HTTPS errors
- **Tracing** - wraps the raw `Page` in `TracedPage` before handing it out
- **Screenshot on failure** - captured automatically via fixture teardown

```python
# conftest.py (simplified)
@pytest.fixture
def traced_page(page) -> TracedPage:
    """Wraps pytest-playwright's page fixture with tracing."""
    return TracedPage(page)
```

Page objects receive `TracedPage`, never raw `Page`. Tests never instantiate browsers directly.

### API Client - Controlled Instantiation

Same pattern for API. A factory fixture creates the `TracedAPIClient`, manages auth token lifecycle:

```python
@pytest.fixture
def api_client(playwright) -> TracedAPIClient:
    """Creates a traced API client for the contact list API."""
    context = playwright.request.new_context(base_url=CONFIG.api_base_url)
    return TracedAPIClient(context)
```

### API Discovery - Self-Documenting Client

The API client dynamically discovers available endpoints from the live Postman collection at startup. This gives the framework self-awareness - it knows what calls exist, what parameters they expect, and what responses to anticipate, without hardcoding any of it.

**How it works:**
1. On session start, `EndpointRegistry.discover()` fetches the Postman collection JSON
2. Parses each request into an `Endpoint` dataclass (name, method, path, auth, body fields, status)
3. Logs a summary of all discovered endpoints
4. If the fetch fails (network, format change), falls back to a bundled `api_spec_fallback.json`

**What the registry provides:**
- **Enriched logging**: `[TracedAPI] POST /contacts [Add Contact] -> 201 (85ms)` instead of just the raw URL
- **Call validation**: warns when a test hits an unknown endpoint not in the spec
- **Self-documentation**: the registry summary is logged at startup, showing every available endpoint

```
API Spec loaded from: Postman collection (remote)
Discovered 12 endpoints:
  POST   /contacts            [auth] -> 201 body: [firstName, lastName, ...]  # Add Contact
  GET    /contacts             [auth] -> 200  # Get Contact List
  ...
```

### AOP: Decorators for Step-Level Concerns

The traced wrappers handle interaction-level logging automatically. For step-level cross-cutting concerns, we use decorators in `support/aop.py`:

**`@log_step`** - applied to step definitions:
- Logs step entry with Gherkin text ("Given I am logged in")
- Logs step exit with duration
- Provides the high-level view that complements the traced wrapper's low-level view

Log output reads naturally - the step layer shows *what*, the traced layer shows *how*:
```
[Step] Given I am logged in
  [TracedPage] goto('https://www.demoblaze.com')
  [TracedPage] click('#login2')
  [TracedPage] fill('#loginusername', 'testuser')
  [TracedPage] fill('#loginpassword', '***')
  [TracedPage] click('button:text("Log in")')
  [TracedPage] wait_for_selector('#nameofuser') → 120ms
[Step] Given I am logged in → OK (450ms)
```

### IoC: Dependency Injection via Fixtures

Pytest fixtures are our IoC container. Components declare their dependencies, the framework resolves and injects them - no manual wiring.

- Steps declare what they need: `traced_page`, `api_client`, `registered_user`
- Fixtures can depend on other fixtures (composition)
- Scoping controls lifecycle: `function` (per-scenario), `session` (once per run)

Page objects, API clients, traced wrappers, and test data are all injected - never constructed directly by step definitions.

### Fixture strategy
- `browser_context` - fresh per scenario (isolated cookies/storage)
- `page` - from browser_context, injected into UI steps
- `api_client` - fresh per scenario, with lazy auth (signup/login on first use)
- `registered_user` - creates a throwaway user for scenarios that need auth as a precondition

### Minimal arbitrary sleeps
Playwright's auto-wait handles most timing. For demoblaze's dynamic JS (modal animations, product grid loading), page objects use explicit `wait_for_selector` conditions rather than `time.sleep`.

> [!NOTE]
> There are a few `wait_for_timeout` calls in the codebase, all for the same reason: demoblaze fires `window.alert()` dialogs asynchronously (on signup, login failure, add to cart), and there is no DOM element to wait for. We register a dialog handler and give the alert a brief window to fire. This is a known Playwright pattern for sites that use browser-native dialogs rather than DOM-based modals.

---