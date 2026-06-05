param(
    [string]$Repository = "baichou6320-cpu/AI-Animation-Director",
    [string]$RemoteName = "origin",
    [string]$Branch = "main",
    [string]$Tag = "",
    [switch]$UseSsh,
    [switch]$SkipValidation
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Run-Git($Arguments) {
    & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed."
    }
}

if (-not $SkipValidation) {
    & powershell -ExecutionPolicy Bypass -File (Join-Path $root "scripts/validate_skill_package.ps1")
    if ($LASTEXITCODE -ne 0) {
        throw "Package validation failed."
    }
}

$status = & git status --porcelain
$uncommitted = $status | Where-Object { $_ -notmatch "^\!\!" }
if ($uncommitted) {
    throw "Working tree has uncommitted changes. Commit or discard them before publishing."
}

$remoteUrl = if ($UseSsh) {
    "git@github.com:$Repository.git"
} else {
    "https://github.com/$Repository.git"
}

$existingRemote = & git remote
if ($existingRemote -contains $RemoteName) {
    Run-Git @("remote", "set-url", $RemoteName, $remoteUrl)
} else {
    Run-Git @("remote", "add", $RemoteName, $remoteUrl)
}

Run-Git @("branch", "-M", $Branch)
Run-Git @("push", "-u", $RemoteName, $Branch)

if ($Tag) {
    $existingTags = & git tag --list $Tag
    if (-not $existingTags) {
        Run-Git @("tag", $Tag)
    }
    Run-Git @("push", $RemoteName, $Tag)
}

Write-Host "Published to $remoteUrl" -ForegroundColor Green
if ($Tag) {
    Write-Host "Pushed tag $Tag" -ForegroundColor Green
}
