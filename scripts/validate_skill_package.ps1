$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$skill = Join-Path $root "ai-animation-director"
$failures = New-Object System.Collections.Generic.List[string]

function Require-File($path) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $failures.Add("Missing file: $path")
    }
}

function Require-Dir($path) {
    if (-not (Test-Path -LiteralPath $path -PathType Container)) {
        $failures.Add("Missing directory: $path")
    }
}

Require-File (Join-Path $root "README.md")
Require-File (Join-Path $root "README.zh-CN.md")
Require-File (Join-Path $root "LICENSE")
Require-File (Join-Path $root ".gitignore")
Require-File (Join-Path $root "docs/repository-metadata.md")
Require-File (Join-Path $root "docs/release-notes-v0.1.0.md")
Require-File (Join-Path $skill "SKILL.md")
Require-File (Join-Path $skill "agents/openai.yaml")
Require-File (Join-Path $skill "prompts/output_composer.md")
Require-File (Join-Path $skill "prompts/quick_package_router.md")
Require-File (Join-Path $skill "templates/jimeng-quick-package.md")
Require-File (Join-Path $skill "references/workflow.md")
Require-Dir (Join-Path $skill "examples")

$examples = Get-ChildItem -Path (Join-Path $skill "examples") -Filter "*.md" -File -ErrorAction SilentlyContinue
if ($examples.Count -lt 3) {
    $failures.Add("Expected at least 3 markdown examples.")
}

foreach ($example in $examples) {
    $text = Get-Content -LiteralPath $example.FullName -Encoding UTF8 -Raw

    if ($example.Name -match "jimeng" -and $text -notmatch "IMG-REF") {
        $failures.Add("$($example.Name): Jimeng example missing IMG-REF.")
    }

    $vidMatches = [regex]::Matches($text, "VID-S(\d{2})")
    foreach ($match in $vidMatches) {
        $shot = $match.Groups[1].Value
        $requiredImage = [char]96 + "IMG-S" + $shot + [char]96
        if (-not $text.Contains($requiredImage)) {
            $failures.Add("$($example.Name): VID-S$shot does not reference IMG-S$shot.")
        }
    }
}

$promptsOnly = Join-Path $skill 'examples/prompts-only-jimeng.md'
if (Test-Path -LiteralPath $promptsOnly -PathType Leaf) {
    $text = Get-Content -LiteralPath $promptsOnly -Encoding UTF8 -Raw
    if ($text.Contains('## 2.') -or $text.Contains('## 4.')) {
        $failures.Add('prompts-only-jimeng.md should not include one-line setup or shot table sections.')
    }
}

$outputFiles = Get-ChildItem -Path (Join-Path $skill "outputs") -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -ne ".gitkeep" }
if ($outputFiles.Count -gt 0) {
    $failures.Add('outputs/ contains generated files that should not be published: ' + $outputFiles.Count)
}

if ($failures.Count -gt 0) {
    Write-Host 'Skill package validation failed:' -ForegroundColor Red
    foreach ($failure in $failures) {
        Write-Host "- $failure" -ForegroundColor Red
    }
    exit 1
}

Write-Host 'Skill package validation passed.' -ForegroundColor Green
