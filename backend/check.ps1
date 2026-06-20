#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$commands = @(
    @("rtk", "err", "python", "../scripts/check_okf.py"),
    @("rtk", "ruff", "format", "."),
    @("rtk", "ruff", "check", ".", "--fix"),
    @("rtk", "mypy", "app/"),
    @("rtk", "err", "pyright", "app/"),
    @("rtk", "pytest")
)

foreach ($args in $commands) {
    uv run @args
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
