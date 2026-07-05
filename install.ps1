<#
.SYNOPSIS
    acqnav installer for Windows (PowerShell).

.DESCRIPTION
    Creates a local virtual environment (.venv), installs acqnav in editable
    mode with its dev extras, and verifies the CLI runs. Idempotent: re-running
    reuses an existing .venv.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\install.ps1
#>
$ErrorActionPreference = "Stop"

# Resolve the repo root (directory containing this script) so the installer
# works regardless of the caller's current working directory.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# --- Locate a Python 3.10+ interpreter ----------------------------------------
function Find-Python {
    foreach ($cmd in @("python", "python3", "py")) {
        $exe = (Get-Command $cmd -ErrorAction SilentlyContinue)
        if ($null -ne $exe) {
            try {
                & $cmd -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
                if ($LASTEXITCODE -eq 0) { return $cmd }
            } catch {}
        }
    }
    return $null
}

$Python = Find-Python
if ($null -eq $Python) {
    Write-Error "Python 3.10+ is required but was not found on PATH. Install it from https://www.python.org/downloads/ and retry."
    exit 1
}

$PyVersion = & $Python --version
Write-Host ">> Using $PyVersion"

# --- Create / reuse the virtual environment -----------------------------------
$VenvDir = Join-Path $ScriptDir ".venv"
if (Test-Path $VenvDir) {
    Write-Host ">> Reusing existing virtual environment at .venv"
} else {
    Write-Host ">> Creating virtual environment at .venv"
    & $Python -m venv $VenvDir
}

$Activate = Join-Path $VenvDir "Scripts\Activate.ps1"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (Test-Path $Activate) {
    & $Activate
}

# --- Install ------------------------------------------------------------------
Write-Host ">> Upgrading pip"
& $VenvPython -m pip install --upgrade pip | Out-Null

Write-Host ">> Installing acqnav (editable) with dev extras"
& $VenvPython -m pip install -e ".[dev]"

# --- Verify -------------------------------------------------------------------
Write-Host ">> Verifying the CLI"
& $VenvPython -m acqnav --version

Write-Host @"

============================================================
 acqnav is installed. Next steps:

   1. Activate the environment:
        .\.venv\Scripts\Activate.ps1

   2. Run the CLI:
        acqnav --help
        acqnav transition --trl 6 --sponsor-identified --funding-line-identified

   3. Run the demos:
        python demos\run_all.py

   4. Run the tests:
        python -m pytest -q
============================================================
"@
