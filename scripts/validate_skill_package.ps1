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
Require-File (Join-Path $root "SECURITY.md")
Require-File (Join-Path $root ".gitignore")
Require-File (Join-Path $root "docs/repository-metadata.md")
Require-File (Join-Path $root "docs/release-notes-v0.1.0.md")
Require-File (Join-Path $root "docs/improvement-backlog.md")
Require-File (Join-Path $root "docs/issue-seeds.md")
Require-File (Join-Path $root "scripts/create_github_repo.ps1")
Require-File (Join-Path $root "scripts/publish_to_github.ps1")
Require-File (Join-Path $root "scripts/validate_skill_package.py")
Require-File (Join-Path $skill "SKILL.md")
Require-File (Join-Path $skill "agents/openai.yaml")
Require-File (Join-Path $skill "prompts/output_composer.md")
Require-File (Join-Path $skill "prompts/quick_package_router.md")
Require-File (Join-Path $skill "prompts/canvas_workflow_builder.md")
Require-File (Join-Path $skill "templates/jimeng-quick-package.md")
Require-File (Join-Path $skill "templates/jimeng-canvas-package.md")
Require-File (Join-Path $skill "templates/jimeng-continue-card.md")
Require-File (Join-Path $skill "references/workflow.md")
Require-File (Join-Path $skill "references/jimeng-canvas.md")
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

    $videoHeadings = [regex]::Matches($text, '(?m)^### VID-S').Count
    $copyBlocks = [regex]::Matches($text, '(?m)^```text\r?$').Count
    if ($copyBlocks -lt $videoHeadings) {
        $failures.Add("$($example.Name): missing non-empty text code blocks.")
    }

    if ($example.Name -eq 'prompts-only-jimeng.md') {
        if ($text.Contains('CV-OP-')) {
            $failures.Add('prompts-only-jimeng.md must not include canvas operation cards.')
        }
    }
    elseif ($example.Name -match 'jimeng') {
        foreach ($term in @('CV-MASTER', 'CV-OP-', 'Z-S01 -> IMG-S01 -> VID-S01')) {
            if (-not $text.Contains($term)) {
                $failures.Add("$($example.Name): missing canvas term $term.")
            }
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

$quickTemplate = Join-Path $skill 'templates/jimeng-quick-package.md'
if (Test-Path -LiteralPath $quickTemplate -PathType Leaf) {
    $text = Get-Content -LiteralPath $quickTemplate -Encoding UTF8 -Raw
    if (-not $text.Contains('jimeng-canvas-package.md')) {
        $failures.Add('jimeng-quick-package.md must point to the canonical canvas template.')
    }
}

$canvasTemplate = Join-Path $skill 'templates/jimeng-canvas-package.md'
if (Test-Path -LiteralPath $canvasTemplate -PathType Leaf) {
    $text = Get-Content -LiteralPath $canvasTemplate -Encoding UTF8 -Raw
    foreach ($term in @('layout: per-shot-execution-cards', 'CV-MASTER', 'Z-ASSET', 'Z-S01 -> IMG-S01 -> VID-S01', 'CV-OP-01', 'IMG-S01', 'VID-S01', '```text')) {
        if (-not $text.Contains($term)) {
            $failures.Add("jimeng-canvas-package.md missing term: $term")
        }
    }
}

$continueTemplate = Join-Path $skill 'templates/jimeng-continue-card.md'
if (Test-Path -LiteralPath $continueTemplate -PathType Leaf) {
    $text = Get-Content -LiteralPath $continueTemplate -Encoding UTF8 -Raw
    foreach ($term in @('delivery_mode: continue', 'next_action: single', '```text')) {
        if (-not $text.Contains($term)) {
            $failures.Add("jimeng-continue-card.md missing term: $term")
        }
    }
}

$continueExamples = Get-ChildItem -Path (Join-Path $skill 'examples') -Filter 'continue-*.md' -File -ErrorAction SilentlyContinue
if ($continueExamples.Count -lt 2) {
    $failures.Add('Expected at least 2 Continue Mode examples.')
}
foreach ($continueExample in $continueExamples) {
    $text = Get-Content -LiteralPath $continueExample.FullName -Encoding UTF8 -Raw
    foreach ($term in @('delivery_mode: continue', 'next_action: single')) {
        if (-not $text.Contains($term)) {
            $failures.Add("$($continueExample.Name) missing term: $term")
        }
    }
    $vidIds = [regex]::Matches($text, 'VID-S\d{2}') | ForEach-Object { $_.Value } | Select-Object -Unique
    $imgIds = [regex]::Matches($text, 'IMG-S\d{2}') | ForEach-Object { $_.Value } | Select-Object -Unique
    if ($vidIds.Count -gt 1 -or $imgIds.Count -gt 1) {
        $failures.Add("$($continueExample.Name) must contain only one current shot.")
    }
}

$router = Join-Path $skill 'prompts/quick_package_router.md'
if (Test-Path -LiteralPath $router -PathType Leaf) {
    $text = Get-Content -LiteralPath $router -Encoding UTF8 -Raw
    foreach ($term in @('delivery_mode', 'Continue Mode', 'execution_state', 'canvas_mode', 'prompt_assets_only', 'routing_reason', 'handoff_notes.to_output_composer')) {
        if (-not $text.Contains($term)) {
            $failures.Add("quick_package_router.md missing routing guard: $term")
        }
    }
}

$composer = Join-Path $skill 'prompts/output_composer.md'
if (Test-Path -LiteralPath $composer -PathType Leaf) {
    $text = Get-Content -LiteralPath $composer -Encoding UTF8 -Raw
    foreach ($term in @('quick_package_router', 'delivery_mode', 'Continue Mode', 'Z-S01 -> IMG-S01 -> VID-S01', 'canvas_mode', 'prompts_only', 'CV-OP-01', '```text')) {
        if (-not $text.Contains($term)) {
            $failures.Add("output_composer.md missing delivery guard: $term")
        }
    }
}

$canvasBuilder = Join-Path $skill 'prompts/canvas_workflow_builder.md'
if (Test-Path -LiteralPath $canvasBuilder -PathType Leaf) {
    $text = Get-Content -LiteralPath $canvasBuilder -Encoding UTF8 -Raw
    foreach ($term in @('canvas_plan', 'CV-MASTER', 'master_plus_sequences', 'prompt_assets_only', 'generate/import', 'user_upload', 'export')) {
        if (-not $text.Contains($term)) {
            $failures.Add("canvas_workflow_builder.md missing term: $term")
        }
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
