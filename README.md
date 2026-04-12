# Red River Test Automation

Test automation framework for both **UI** and **API** testing, built for the Red River QA automation assignment.

## The Assignment

> Create 2 or more scenarios per challenge using any test automation framework.
> The scenarios should cover key user flows and include intent of the test case, any pre-conditions, explicit test steps with clear expected results, and error handling.

- **Challenge 1** (UI): [demoblaze.com](https://www.demoblaze.com) — an e-commerce product store
- **Challenge 2** (API): [Contact List API](https://thinking-tester-contact-list.herokuapp.com/) — CRUD operations

Full assignment spec: [`assignment.md`](assignment.md)

## Approach

Rather than building two separate test suites with different tools, I built a single framework that handles both UI and API testing. The reasoning: in a real application these layers coexist, and a unified framework can leverage the API for test setup, share auth fixtures, and produce consolidated reports. More on this in the [framework docs](docs/framework.md#overview).

## Quick Start

```bash
# macOS/Linux
make setup    # install dependencies + browsers
make test     # run all tests

# Windows PowerShell
.\setup.ps1 -Run
```

Run `make help` or `.\setup.ps1 -Help` for all options (headed mode, browser selection, reports, etc.).

Full execution guide including CI, cross-browser, and manual Python setup: [docs/run-me.md](docs/run-me.md)

## What's Inside

### Test Scenarios (12 passing + 2 intentional failures)

| Suite | Scenarios | Coverage |
|-------|-----------|----------|
| **API** | 7 | Auth lifecycle, CRUD, PUT vs PATCH semantics, validation errors, unauthorized access |
| **UI** | 5 | Signup/login/logout, category filtering, full purchase flow, login validation |
| **Demos** | 2 | Intentionally failing tests to showcase error reporting ([how to fix](docs/tests.md#expected-failure-demos)) |

Detailed scenario descriptions, coverage rationale, and how to write new tests: [docs/tests.md](docs/tests.md)

### Framework Highlights

- **Playwright** for both browser automation and HTTP calls — one tool, one runner
- **pytest-bdd** with Gherkin features — scenarios are readable by non-developers
- **API discovery** from the Postman collection — the client knows the API shape at runtime
- **Generic data-driven steps** — new API tests need only a `.feature` file, zero Python
- **Typed locators** — all CSS selectors in one file, IDE autocomplete, typo-safe
- **Traced wrappers** — every browser click and API call is logged automatically
- **Cross-browser** — config-driven, runs on Chromium, Firefox, and WebKit
- **Cross-platform** — Makefile (macOS/Linux) + PowerShell (Windows), uv with pip fallback

Architecture details and design decisions: [docs/framework.md](docs/framework.md)

## Project Structure

```
red-river-automation/
├── config.yaml             # URLs, timeouts, browser list — single config file
├── features/               # Gherkin .feature files (what to test)
│   ├── ui/                 #   5 UI scenarios + 1 expected-failure demo
│   └── api/                #   7 API scenarios + 1 expected-failure demo
├── steps/                  # Step definitions (how to test)
│   ├── ui/                 #   UI step implementations + shared conftest
│   └── api/                #   API step implementations + generic data-driven steps
├── pages/                  # Page Object Model
│   ├── locators.py         #   All CSS selectors — edit here when UI changes
│   └── *.py                #   Page behavior (no selectors in these files)
├── support/                # Framework infrastructure
│   ├── traced.py           #   TracedPage + TracedAPIClient (logging proxies)
│   ├── api_discovery.py    #   Postman collection parser + endpoint registry
│   └── config.py           #   Loads config.yaml
├── Makefile                # macOS/Linux entry point
├── setup.ps1               # Windows entry point
└── docs/                   # You are here
```

## Documentation

| Document | What's in it |
|----------|-------------|
| [docs/run-me.md](docs/run-me.md) | How to run: setup, execution, CI, cross-browser, troubleshooting |
| [docs/framework.md](docs/framework.md) | Architecture: design decisions, patterns, tracing, IoC, AOP |
| [docs/tests.md](docs/tests.md) | Test scenarios: what they cover, why, and how to write new ones |
| [assignment.md](assignment.md) | The original assignment |
