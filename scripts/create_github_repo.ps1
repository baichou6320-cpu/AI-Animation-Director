param(
    [string]$Owner = "baichou6320-cpu",
    [string]$Name = "ai-animation-director",
    [string]$Description = "Codex Skill for AI animation pre-production and Jimeng-ready prompt execution packages.",
    [string[]]$Topics = @(
        "codex-skill",
        "ai-animation",
        "ai-video",
        "prompt-engineering",
        "jimeng",
        "storyboard",
        "shot-list",
        "video-prompts",
        "image-prompts",
        "animation-production"
    ),
    [switch]$Private,
    [switch]$UseOrg
)

$ErrorActionPreference = "Stop"

$token = $env:GITHUB_TOKEN
if (-not $token) {
    throw "Missing GITHUB_TOKEN. Create a fine-grained GitHub token with repository creation permission, set it as GITHUB_TOKEN, then rerun."
}

$headers = @{
    Authorization          = "Bearer $token"
    Accept                 = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

$repoFullName = "$Owner/$Name"
$repoUrl = "https://api.github.com/repos/$repoFullName"

try {
    $existing = Invoke-RestMethod -Method Get -Uri $repoUrl -Headers $headers
    Write-Host "Repository already exists: $($existing.html_url)" -ForegroundColor Yellow
    exit 0
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -ne 404) {
        throw
    }
}

$body = @{
    name        = $Name
    description = $Description
    private     = [bool]$Private
    auto_init   = $false
    has_issues  = $true
    has_projects = $false
    has_wiki    = $false
} | ConvertTo-Json

$createUri = if ($UseOrg) {
    "https://api.github.com/orgs/$Owner/repos"
} else {
    "https://api.github.com/user/repos"
}

$created = Invoke-RestMethod -Method Post -Uri $createUri -Headers $headers -Body $body -ContentType "application/json"

if ($Topics.Count -gt 0) {
    $topicBody = @{ names = $Topics } | ConvertTo-Json
    Invoke-RestMethod -Method Put -Uri "$repoUrl/topics" -Headers $headers -Body $topicBody -ContentType "application/json" | Out-Null
}

Write-Host "Created repository: $($created.html_url)" -ForegroundColor Green
Write-Host "Next: powershell -ExecutionPolicy Bypass -File .\scripts\publish_to_github.ps1" -ForegroundColor Green
