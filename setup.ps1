<#
.SYNOPSIS
    Windows PowerShell entry point for setup and test execution.

.DESCRIPTION
    Bootstraps the test environment (installs dependencies and Playwright browsers)
    and optionally runs tests. Tries uv first, falls back to pip + venv.

.PARAMETER Run
    Run tests after setup.

.PARAMETER Suite
    Which test suite to run: "all" (default), "ui", or "api".

.PARAMETER Headed
    Show the browser window during UI tests.

.PARAMETER Slow
    Slow down browser actions by N milliseconds (useful for demos).

.PARAMETER AllBrowsers
    Run UI tests on Chromium, Firefox, and WebKit.

.PARAMETER Report
    Generate an HTML test report (report.html).

.PARAMETER Clean
    Remove .venv, caches, reports, and logs.

.EXAMPLE
    .\setup.ps1                              # Setup only
    .\setup.ps1 -Run                         # Setup + run all tests (headless)
    .\setup.ps1 -Run -Headed                 # Run with visible browser
    .\setup.ps1 -Run -Headed -Slow 500       # Run with visible browser, slowed down
    .\setup.ps1 -Run -Suite ui               # Run UI tests only
    .\setup.ps1 -Run -Suite api              # Run API tests only
    .\setup.ps1 -Run -AllBrowsers            # Run UI tests on all browsers
    .\setup.ps1 -Run -Report                 # Run all tests with HTML report
    .\setup.ps1 -Clean                       # Clean up

    # Environment variables (take priority over switch params):
    $env:HEADED=1; .\setup.ps1 -Run                          # same as -Headed
    $env:SLOW=500; .\setup.ps1 -Run                          # same as -Slow 500
    $env:CONFIG_FILE="config.staging.yaml"; .\setup.ps1 -Run  # custom config
    .\setup.ps1 -Run -ConfigFile config.staging.yaml          # same via param

    Logs are always written to: logs\test_run.log
#>

param(
    [switch]$Help,
    [switch]$Run,
    [ValidateSet("all", "ui", "api")]
    [string]$Suite = "all",
    [switch]$Headed,
    [int]$Slow = 0,
    [string]$ConfigFile = "",
    [switch]$AllBrowsers,
    [switch]$Report,
    [switch]$Clean
)

if ($Help) {
    Write-Host @"

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
"@
    exit 0
}

$ErrorActionPreference = "Stop"
$MinPythonVersion = [version]"3.12"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

function Find-Python {
    # Try common Python command names on Windows
    foreach ($cmd in @("python", "python3", "py")) {
        $found = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($found) { return $found.Source }
    }
    return $null
}

function Test-PythonVersion {
    param([string]$PythonPath)
    $versionOutput = & $PythonPath --version 2>&1
    if ($versionOutput -match "(\d+\.\d+\.\d+)") {
        $version = [version]$Matches[1]
        return $version -ge $MinPythonVersion
    }
    return $false
}

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------

if ($Clean) {
    Write-Host "==> Cleaning..."
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .venv, __pycache__, .pytest_cache, report.html, logs
    Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
    Write-Host "==> Cleaned."
    exit 0
}

# ---------------------------------------------------------------------------
# Check Python
# ---------------------------------------------------------------------------

$Python = Find-Python
if (-not $Python) {
    Write-Error @"
ERROR: Python not found.
Install from: https://www.python.org/downloads/
  Windows: winget install Python.Python.3.12
"@
    exit 1
}

if (-not (Test-PythonVersion $Python)) {
    $currentVersion = & $Python --version 2>&1
    Write-Error @"
ERROR: Python >= $MinPythonVersion is required. Found: $currentVersion
Install from: https://www.python.org/downloads/
  Windows: winget install Python.Python.3.12
"@
    exit 1
}

Write-Host "==> Python: $(& $Python --version)"

# ---------------------------------------------------------------------------
# Install dependencies
# ---------------------------------------------------------------------------

$UseUv = Test-Command "uv"

if ($UseUv) {
    Write-Host "==> Using uv to install dependencies"
    uv sync
    $PytestCmd = "uv run pytest"
    $PlaywrightCmd = "uv run playwright"
} else {
    Write-Host "==> Using pip + venv to install dependencies"
    & $Python -m venv .venv
    & .\.venv\Scripts\pip install --upgrade pip
    & .\.venv\Scripts\pip install -r requirements.txt
    $PytestCmd = ".\.venv\Scripts\pytest"
    $PlaywrightCmd = ".\.venv\Scripts\playwright"
}

# ---------------------------------------------------------------------------
# Install Playwright browsers
# ---------------------------------------------------------------------------

# Install all browsers listed in config.yaml
$BrowserCmd = if ($UseUv) { "uv run python3" } else { ".\.venv\Scripts\python" }
$ConfigBrowsers = (Invoke-Expression "$BrowserCmd -c `"import yaml; print(' '.join(yaml.safe_load(open('config.yaml'))['ui']['browsers']))`"" 2>$null) -split ' '
if (-not $ConfigBrowsers) { $ConfigBrowsers = @("chromium") }
foreach ($b in $ConfigBrowsers) {
    Write-Host "==> Installing Playwright browser: $b"
    Invoke-Expression "$PlaywrightCmd install --with-deps $b"
}

Write-Host "==> Setup complete."

# ---------------------------------------------------------------------------
# Run tests (if requested)
# ---------------------------------------------------------------------------

if (-not $Run) { exit 0 }

# Build pytest arguments
$PytestArgs = @("-v")

switch ($Suite) {
    "ui"  { $PytestArgs += "steps/ui/" }
    "api" { $PytestArgs += "steps/api/" }
}

# Env vars take priority, switch params are fallback
$ConfigValue = if ($env:CONFIG_FILE) { $env:CONFIG_FILE } else { $ConfigFile }
if ($ConfigValue) {
    $env:CONFIG_FILE = $ConfigValue
    Write-Host "==> Using config: $ConfigValue"
}

if ($env:HEADED -or $Headed) {
    $PytestArgs += "--headed"
}

$SlowValue = if ($env:SLOW) { [int]$env:SLOW } else { $Slow }
if ($SlowValue -gt 0) {
    $PytestArgs += "--slowmo", $SlowValue
}

if ($AllBrowsers) {
    Write-Host "==> Installing additional browsers (Firefox, WebKit)"
    Invoke-Expression "$PlaywrightCmd install --with-deps firefox webkit"
    $PytestArgs += "--browser", "chromium", "--browser", "firefox", "--browser", "webkit"
}

if ($Report) {
    $PytestArgs += "--html=report.html", "--self-contained-html"
}

Write-Host "==> Running: $PytestCmd $($PytestArgs -join ' ')"
Invoke-Expression "$PytestCmd $($PytestArgs -join ' ')"

Write-Host "==> Logs: logs\test_run.log"
if ($Report) {
    Write-Host "==> Report: report.html"
}
