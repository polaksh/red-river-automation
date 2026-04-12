# Test Scenarios

- [Test Scenarios](#test-scenarios)
  - [Coverage Strategy](#coverage-strategy)
  - [API Scenarios](#api-scenarios)
    - [User Authentication Lifecycle](#user-authentication-lifecycle)
    - [Create and Read Contact](#create-and-read-contact)
    - [Update Contact (PUT and PATCH)](#update-contact-put-and-patch)
    - [Delete Contact and Authorization](#delete-contact-and-authorization)
    - [Contact Validation](#contact-validation)
  - [UI Scenarios](#ui-scenarios)
    - [Authentication Lifecycle](#authentication-lifecycle)
    - [Browse Products by Category](#browse-products-by-category)
    - [Purchase Flow](#purchase-flow)
    - [Login Validation](#login-validation)
  - [Expected-Failure Demos](#expected-failure-demos)
  - [Writing New Tests](#writing-new-tests)
    - [Generic Data-Driven Steps](#generic-data-driven-steps)
    - [Available Generic Steps](#available-generic-steps)
    - [Contact Factory and Find-or-Create](#contact-factory-and-find-or-create)
    - [Shared Steps](#shared-steps)


## Coverage Strategy

The assignment asks for "key user flows with error handling." Rather than maximizing the number of scenarios, the goal was meaningful coverage across both positive and negative paths:

- **Positive**: full lifecycle flows that mirror real user behavior (signup through checkout, CRUD through delete)
- **Negative**: input validation, wrong credentials, unauthorized access — where real bugs tend to live
- **Behavioral**: PUT vs PATCH semantics, token invalidation after logout — testing API *contracts*, not just status codes

Each scenario was chosen to test something distinct. No two scenarios overlap in what they prove.


## API Scenarios

### User Authentication Lifecycle
**Feature**: [`user_auth.feature`](../features/api/user_auth.feature)

Tests the full state machine: register → login → use token → get profile → logout → verify token is dead.

This catches a common class of bugs: tokens that survive logout, profile data that doesn't match registration, login responses that return malformed tokens.

### Create and Read Contact
**Feature**: [`create_contact.feature`](../features/api/create_contact.feature)

Creates a contact with all fields via a **data-driven** Gherkin table, then reads it back by ID and verifies field-by-field. Also checks the contact appears in the list endpoint.

This scenario uses the generic step `When I call "Add Contact" with:` — the feature file contains all the data, the step definition is zero lines of custom Python. See [Writing New Tests](#writing-new-tests) below.

### Update Contact (PUT and PATCH)
**Feature**: [`update_contact.feature`](../features/api/update_contact.feature)

Tests a real semantic distinction that many APIs get wrong:
- **PUT** replaces the entire resource — omitted optional fields should become `null`
- **PATCH** modifies only the sent fields — other fields should be untouched

This is a behavioral test, not just a status code check. It verifies the API honors HTTP method semantics.

### Delete Contact and Authorization
**Feature**: [`delete_contact.feature`](../features/api/delete_contact.feature)

Two scenarios in one feature:
1. Delete a contact, verify it's gone (GET returns 404)
2. Hit a protected endpoint without a token, verify 401 with the correct error body

The second scenario is the assignment's "error handling" requirement — testing that the API rejects unauthorized access with a meaningful response.

### Contact Validation
**Feature**: [`contact_validation.feature`](../features/api/contact_validation.feature)

Negative API tests:
- Missing required fields (`firstName`, `lastName`) → 400
- Invalid phone number format → 400

These are fully data-driven using generic steps — no custom Python. Adding a new validation test means adding a Gherkin scenario, nothing else.


## UI Scenarios

### Authentication Lifecycle
**Feature**: [`auth.feature`](../features/ui/auth.feature)

Signup with a unique username → login → verify navbar shows the username → logout → verify login/signup links reappear.

Tests the full UI state machine. Each test run generates a unique username to avoid collision on the shared demo site.

### Browse Products by Category
**Feature**: [`browse_products.feature`](../features/ui/browse_products.feature)

Clicks each category (Phones, Laptops, Monitors) and verifies the product grid shows only products from that category.

Uses known product names as a verification set. This is a deliberate tradeoff: if the site's inventory changes, the test breaks. In a real project you'd verify against a database or API; here the demo site's inventory is static.

### Purchase Flow
**Feature**: [`purchase.feature`](../features/ui/purchase.feature)

The end-to-end happy path: browse → select product → verify detail page → add to cart → navigate to cart → verify item in cart → fill order form → purchase → verify confirmation.

This is the most valuable UI scenario — it mirrors the core user journey that, if broken, means the site is down.

### Login Validation
**Feature**: [`login_validation.feature`](../features/ui/login_validation.feature)

Two negative scenarios:
- Login with wrong credentials → error alert
- Login with empty credentials → error alert

Tests that the UI provides clear feedback on bad input. This replaced an earlier contact form test that was essentially a smoke test with no meaningful assertions.


## Expected-Failure Demos

Two scenarios are tagged `@expected_failure` and are **intentionally broken** to demonstrate how the framework reports failures:

| Feature | What fails | How to fix |
|---|---|---|
| [`ui/negative_demo.feature`](../features/ui/negative_demo.feature) | Asserts Samsung Galaxy S6 costs $999.99 (it's $360) | Change `"$999.99"` to `"$360"` in the feature file |
| [`api/negative_demo.feature`](../features/api/negative_demo.feature) | Fetches a nonexistent contact ID, asserts 200 (it's 404) | Change the Then step to assert 404 instead of expecting contact details |

These are excluded from the main test run (`-m "not expected_failure"`) and from the CI pass/fail gate. They exist so reviewers can see:
- How the log file captures the full step + interaction trace on failure
- How the HTML report displays failed scenarios
- That the framework produces actionable error messages


## Writing New Tests

### Generic Data-Driven Steps

For straightforward API tests, no Python is needed. The framework provides generic steps that resolve endpoints by name from the Postman collection:

```gherkin
# This is a complete test — no custom step code required
Scenario: Create a contact with minimal fields
  Given I am an authenticated API user
  When I call "Add Contact" with:
    | firstName | Jane |
    | lastName  | Doe  |
  Then the response status is 201
  And the response has an ID
```

The step `When I call "Add Contact" with:` looks up "Add Contact" in the endpoint registry, knows it's a `POST /contacts`, sends the data table as the request body, and stores the response. The feature file author only needs to know the endpoint name and the fields.

### Available Generic Steps

| Step | Description |
|---|---|
| `When I call "{endpoint}" with:` | Send a data table as the request body |
| `When I call "{endpoint}"` | No-body call (GET, DELETE) |
| `When I call "{endpoint}" for that contact` | Call with the contact ID from a previous step |
| `Given a contact exists with:` | Find-or-create (see below) |
| `Then the response status is {N}` | Assert HTTP status code |
| `Then the response has an ID` | Assert `_id` field exists |
| `Then the response fields match what I sent` | Field-by-field comparison |

Endpoint names come from the Postman collection: `"Add Contact"`, `"Get Contact"`, `"Get Contact List"`, `"Update Contact (PUT)"`, `"Update Contact (PATCH)"`, `"Delete Contact"`, `"Add User"`, `"Log In User"`, `"Log Out User"`, `"Get User Profile"`, `"Delete User"`.

### Contact Factory and Find-or-Create

For scenarios that need a contact as a precondition, two approaches:

**Create explicitly** (always creates a new one):
```gherkin
Given I create a contact
Given I create a contact with full details
```

**Find-or-create** (searches first, creates only if missing):
```gherkin
Given a contact exists with:
  | firstName | Jerry  |
  | lastName  | Garcia |
```

The find-or-create step searches the user's contact list for a match on the provided fields. If found, it uses the existing contact. If not, it creates one. Either way, subsequent steps can reference "that contact."

This pattern uses the API as the state store — no in-memory dictionaries to manage between steps.

### Shared Steps

Steps that appear across multiple features are defined once in `conftest.py` files:

| Step | Where | Used by |
|---|---|---|
| `Given I am an authenticated API user` | `steps/api/conftest.py` | All API features |
| `Given I am on the home page` | `steps/ui/conftest.py` | All UI features |
| `Given I create a contact` | `steps/api/conftest.py` | update, delete features |
| All generic `When I call...` / `Then the response...` steps | `steps/api/conftest.py` | Any API feature |

Adding a new feature that needs auth or a contact as a precondition requires zero new step code — just reference the shared steps in the Gherkin file.
