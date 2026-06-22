#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$commands = @(
    @("rtk", "err", "python", "../scripts/check_okf.py"),
    @("rtk", "ruff", "format", "."),
    @("rtk", "ruff", "check", ".", "--fix"),
    @("rtk", "mypy", "app/", "tests/"),
    @("rtk", "err", "pyright", "app/", "tests/"),
    @("rtk", "pytest")
)

foreach ($args in $commands) {
    uv run @args
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
