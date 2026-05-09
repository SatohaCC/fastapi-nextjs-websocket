#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$commands = @(
    @("ruff", "format", "."),
    @("ruff", "check", ".", "--fix"),
    @("mypy", "app/"),
    @("pyright", "app/"),
    @("pytest")
)

foreach ($args in $commands) {
    uv run @args
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
