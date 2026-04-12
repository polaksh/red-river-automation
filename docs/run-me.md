# Execution

- [Execution](#execution)
  - [Assumptions and Constraints](#assumptions-and-constraints)
    - [Disclaimer](#disclaimer)
    - [Pre-Requisites](#pre-requisites)
    - [Local Automation](#local-automation)
      - [Makefile](#makefile)
      - [setup.ps1](#setupps1)
    - [Python](#python)
    - [CI](#ci)




## Assumptions and Constraints

### Disclaimer
This Assignment was developed on MacOS, however the review can be on any platform, therefore I didn't dockerized it, so that the browser can be visible via `Playwright`'s `--headed` argument, running this inside a docker will be silent by definition

### Pre-Requisites
- Python 3.12 is a must
- `uv` is optional
- Playwright requires the instalation of its browser binaries, if not manually installed it can be taken care of using either of the local automation scripts [below](#local-automation)

### Local Automation
#### Makefile 
For MacOS and Unix one can use targets from the [Makefile](../Makefile)
  running `make help` will list all make targets available:
  ```shell
    Red River Test Automation Framework

    Targets:
    help                   Show this help
    setup                  Install dependencies + Playwright browsers
    test                   Run all tests
    test-ui                Run UI tests only
    test-api               Run API tests only
    test-all-browsers      Run UI tests on every browser in config.yaml
    report                 Run all tests and generate report.html
    clean                  Remove .venv, caches, reports, logs

    Options (env vars, combinable with any target):
    HEADED=1               Show the browser window
    SLOW=<ms>              Slow down browser actions (e.g., SLOW=500)
    PYTEST_OPTS="..."      Extra pytest flags (e.g., --browser firefox)
    CONFIG_FILE=<path>     Use a different config file

    Examples:
    make test                                         Run all tests
    HEADED=1 make test-ui                             UI tests, visible browser
    HEADED=1 make test-ui PYTEST_OPTS="--browser firefox"  Firefox, headed
    make test-all-browsers                            All browsers from config.yaml
  ```
#### [setup.ps1](../setup.ps1)
For Windows, a powershell script that is equivalent to the Makrfile, (granted was not tested due to a lack of a Windows OS)
running `./setup.ps1 -Help` should produce:
```poweshell
Red River Test Automation Framework

Parameters:
-Help                  Show this help
-Run                   Run tests after setup
-Suite <all|ui|api>    Which test suite to run (default: all)
-Headed                Show the browser window
-Slow <ms>             Slow down browser actions (e.g., -Slow 500)
-ConfigFile <path>     Use a different config file
-AllBrowsers           Run UI tests on every browser in config.yaml
-Report                Generate HTML report
-Clean                 Remove .venv, caches, reports, logs

Environment variables (take priority over parameters):
HEADED=1               Same as -Headed
SLOW=500               Same as -Slow 500
CONFIG_FILE=<path>     Same as -ConfigFile

Examples:
.\setup.ps1                                    Setup only
.\setup.ps1 -Run                               Run all tests
.\setup.ps1 -Run -Headed                       Visible browser
.\setup.ps1 -Run -Suite ui -Headed -Slow 500   UI tests, slowed down
.\setup.ps1 -Run -AllBrowsers                  All browsers from config.yaml
.\setup.ps1 -Run -Report                       Generate report.html
.\setup.ps1 -Clean                             Clean up
```

### Python
Python should be platform agnostic, this implementation requires `Python 3.12` and is managed by [uv](https://docs.astral.sh/uv/), that said, since I can't be sure that [uv](https://docs.astral.sh/uv/) will be available during the review, there is a [requirements.txt](../requirements.txt) file for PyPi and running in a `venv` as follows:
  ```shell
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  playwright install chromium
  pytest -v
  ```
  > [!NOTE]
  Both [`Makefile`](#makefile) and [`setup.ps1`](#setupps1) should identify if uv exists and fallback to plain python
  However, should one want to explicitly run pure python and `venv` he can using the commands above

### CI
An alternative to the above [local automation](#local-automation), Github workflow is [provided](../.github/workflows/tests.yml) to run this in a "CI-like" environemnt
- this is a `manual_dispatch` trigger - i.e manual - it can only be triggered by users with `Write` permissions to the repo
- the CI runs the tests cross-browser 
- all reports are available for download in 1 zip file
- to fix the intentionally failing tests a commit with a fix is required