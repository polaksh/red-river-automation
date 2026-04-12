SHELL := /bin/bash
.DEFAULT_GOAL := help

PYTHON_MIN := 3.12
PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)
UV := $(shell command -v uv 2>/dev/null)
# Lazy — evaluated when a target actually uses it (after deps are installed)
BROWSERS = $(shell uv run python3 -c "import yaml; print(' '.join(yaml.safe_load(open('config.yaml'))['ui']['browsers']))" 2>/dev/null || echo "chromium")

ifdef UV
  PYTEST := uv run pytest
else
  PYTEST := .venv/bin/pytest
endif

# Internal flags from env vars — never overridden by PYTEST_OPTS
PYTEST_FLAGS :=
ifdef HEADED
  PYTEST_FLAGS += --headed
endif
ifdef SLOW
  PYTEST_FLAGS += --slowmo $(SLOW)
endif

# ---------------------------------------------------------------------------
# Help (auto-generated from ## comments)
# ---------------------------------------------------------------------------

.PHONY: help
help: ## Show this help
	@echo ""
	@echo "Red River Test Automation Framework"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  %-22s %s\n", $$1, $$2}'
	@echo ""
	@echo "Options (env vars, combinable with any target):"
	@echo "  HEADED=1               Show the browser window"
	@echo "  SLOW=<ms>              Slow down browser actions (e.g., SLOW=500)"
	@echo "  PYTEST_OPTS=\"...\"      Extra pytest flags (e.g., --browser firefox)"
	@echo "  CONFIG_FILE=<path>     Use a different config file"
	@echo ""
	@echo "Examples:"
	@echo "  make test                                         Run all tests"
	@echo "  HEADED=1 make test-ui                             UI tests, visible browser"
	@echo "  HEADED=1 make test-ui PYTEST_OPTS=\"--browser firefox\"  Firefox, headed"
	@echo "  make test-all-browsers                            All browsers from config.yaml"
	@echo ""
	@echo "Configured browsers: $(BROWSERS)"
	@echo ""

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

.PHONY: check-python
check-python:
	@if [ -z "$(PYTHON)" ]; then \
		echo "ERROR: Python not found."; \
		echo "Install from: https://www.python.org/downloads/"; \
		echo "  macOS: brew install python@3.12"; \
		exit 1; \
	fi
	@$(PYTHON) -c "import sys; exit(0 if sys.version_info >= (3,12) else 1)" 2>/dev/null || { \
		echo "ERROR: Python >= $(PYTHON_MIN) is required. Found: $$($(PYTHON) --version)"; \
		echo "Install from: https://www.python.org/downloads/"; \
		echo "  macOS: brew install python@3.12"; \
		exit 1; \
	}

.PHONY: install-deps
install-deps: check-python
ifdef UV
	@echo "==> Using uv to install dependencies"
	uv sync
else
	@echo "==> Using pip + venv to install dependencies"
	$(PYTHON) -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
endif

.PHONY: install-browsers
install-browsers: install-deps
ifdef UV
	@for b in $(BROWSERS); do uv run playwright install --with-deps $$b; done
else
	@for b in $(BROWSERS); do .venv/bin/playwright install --with-deps $$b; done
endif

.PHONY: setup
setup: install-browsers ## Install dependencies + Playwright browsers
	@echo "==> Setup complete. Run 'make test' to execute tests."

# ---------------------------------------------------------------------------
# Test execution
# ---------------------------------------------------------------------------

.PHONY: test
test: setup ## Run all tests
	$(PYTEST) -v $(PYTEST_FLAGS) $(PYTEST_OPTS)
	@echo "==> Logs: logs/test_run.log"

.PHONY: test-ui
test-ui: setup ## Run UI tests only
	$(PYTEST) -v steps/ui/ $(PYTEST_FLAGS) $(PYTEST_OPTS)
	@echo "==> Logs: logs/test_run.log"

.PHONY: test-api
test-api: setup ## Run API tests only
	$(PYTEST) -v steps/api/ $(PYTEST_FLAGS) $(PYTEST_OPTS)
	@echo "==> Logs: logs/test_run.log"

.PHONY: test-all-browsers
test-all-browsers: setup ## Run UI tests on every browser in config.yaml
ifdef UV
	@for b in $(BROWSERS); do uv run playwright install --with-deps $$b; done
else
	@for b in $(BROWSERS); do .venv/bin/playwright install --with-deps $$b; done
endif
	@for b in $(BROWSERS); do \
		echo "==> Running UI tests on $$b"; \
		$(PYTEST) -v steps/ui/ --browser $$b $(PYTEST_FLAGS) $(PYTEST_OPTS) \
			--html=report-$$b.html --self-contained-html \
			--junitxml=logs/results-$$b.xml \
			-o "junit_suite_name=ui-$$b" || true; \
	done
	@echo "==> Reports: $(foreach b,$(BROWSERS),report-$(b).html )"
	@echo "==> Logs: logs/test_run.log"

.PHONY: report
report: setup ## Run all tests and generate report.html
	$(PYTEST) -v --html=report.html --self-contained-html $(PYTEST_FLAGS) $(PYTEST_OPTS)
	@echo "==> Report: report.html"
	@echo "==> Logs:   logs/test_run.log"

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

.PHONY: clean
clean: ## Remove .venv, caches, reports, logs
	rm -rf .venv __pycache__ .pytest_cache report.html report-*.html logs/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "==> Cleaned."
