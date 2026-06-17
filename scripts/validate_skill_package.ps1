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
Require-File (Join-Path $skill "prompts/qa_reviewer.md")
Require-File (Join-Path $skill "prompts/revision_patch_builder.md")
Require-File (Join-Path $skill "templates/jimeng-quick-package.md")
Require-File (Join-Path $skill "templates/jimeng-canvas-package.md")
Require-File (Join-Path $skill "templates/jimeng-continue-card.md")
Require-File (Join-Path $skill "templates/project-state.json")
Require-File (Join-Path $skill "templates/failure-diagnosis-card.md")
Require-File (Join-Path $skill "templates/revision-patch-card.md")
Require-File (Join-Path $skill "references/workflow.md")
Require-File (Join-Path $skill "references/jimeng-canvas.md")
Require-Dir (Join-Path $skill "examples")

$examples = Get-ChildItem -Path (Join-Path $skill "examples") -Filter "*.md" -File -ErrorAction SilentlyContinue
if ($examples.Count -lt 3) {
    $failures.Add("Expected at least 3 markdown examples.")
}

foreach ($example in $examples) {
    $text = Get-Content -LiteralPath $example.FullName -Encoding UTF8 -Raw
    $isStateExample = $example.Name.StartsWith('state-save-')
    $isRevisionExample = $example.Name.StartsWith('revision-')

    if ($example.Name -match "jimeng" -and $text -notmatch "IMG-REF") {
        $failures.Add("$($example.Name): Jimeng example missing IMG-REF.")
    }

    if (-not $isStateExample -and -not $isRevisionExample) {
        $vidMatches = [regex]::Matches($text, "VID-S(\d{2})")
        foreach ($match in $vidMatches) {
            $shot = $match.Groups[1].Value
            $requiredImage = [char]96 + "IMG-S" + $shot + [char]96
            if (-not $text.Contains($requiredImage)) {
                $failures.Add("$($example.Name): VID-S$shot does not reference IMG-S$shot.")
            }
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
        if ($text.Contains('ai_animation_director_project_state')) {
            $failures.Add('prompts-only-jimeng.md must not default to project state.')
        }
    }
    elseif ($example.Name -match 'jimeng' -and -not $isRevisionExample) {
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

$stateTemplate = Join-Path $skill 'templates/project-state.json'
if (Test-Path -LiteralPath $stateTemplate -PathType Leaf) {
    try {
        $state = Get-Content -LiteralPath $stateTemplate -Encoding UTF8 -Raw | ConvertFrom-Json
        foreach ($property in @('schema_version', 'state_type', 'project', 'shots', 'completed_steps', 'current_step', 'next_action')) {
            if (-not ($state.PSObject.Properties.Name -contains $property)) {
                $failures.Add("project-state.json missing key: $property")
            }
        }
        if ($state.state_type -ne 'ai_animation_director_project_state') {
            $failures.Add('project-state.json has wrong state_type.')
        }
    }
    catch {
        $failures.Add('project-state.json is not valid JSON.')
    }
}

$failureTemplate = Join-Path $skill 'templates/failure-diagnosis-card.md'
if (Test-Path -LiteralPath $failureTemplate -PathType Leaf) {
    $text = Get-Content -LiteralPath $failureTemplate -Encoding UTF8 -Raw
    foreach ($term in @('template: failure-diagnosis-card', 'continue_submode: failure_repair', 'character_drift', 'lighting_error', 'generation_blocked', '```json')) {
        if (-not $text.Contains($term)) {
            $failures.Add("failure-diagnosis-card.md missing term: $term")
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

$stateExample = Join-Path $skill 'examples/state-save-pixel-project.md'
if (Test-Path -LiteralPath $stateExample -PathType Leaf) {
    $text = Get-Content -LiteralPath $stateExample -Encoding UTF8 -Raw
    if (-not $text.Contains('ai_animation_director_project_state')) {
        $failures.Add('state-save-pixel-project.md missing state marker.')
    }
}

$failureExample = Join-Path $skill 'examples/failure-diagnosis-character-drift.md'
if (Test-Path -LiteralPath $failureExample -PathType Leaf) {
    $text = Get-Content -LiteralPath $failureExample -Encoding UTF8 -Raw
    foreach ($term in @('continue_submode: failure_repair', 'VID-S02', 'character_drift', 'retry VID-S02', '```json')) {
        if (-not $text.Contains($term)) {
            $failures.Add("failure-diagnosis-character-drift.md missing term: $term")
        }
    }
}

$revisionExample = Join-Path $skill 'examples/revision-change-shot-s02-jimeng.md'
if (Test-Path -LiteralPath $revisionExample -PathType Leaf) {
    $text = Get-Content -LiteralPath $revisionExample -Encoding UTF8 -Raw
    foreach ($term in @('delivery_mode: revision', 'revision_mode: shot_patch', 'IMG-S02', 'VID-S02', 'regenerate IMG-S02', '```json')) {
        if (-not $text.Contains($term)) {
            $failures.Add("revision-change-shot-s02-jimeng.md missing term: $term")
        }
    }
}

$router = Join-Path $skill 'prompts/quick_package_router.md'
if (Test-Path -LiteralPath $router -PathType Leaf) {
    $text = Get-Content -LiteralPath $router -Encoding UTF8 -Raw
    foreach ($term in @('delivery_mode', 'Revision Mode', 'Continue Mode', 'execution_state', 'project_state', 'revision_state', 'failure_repair', 'canvas_mode', 'prompt_assets_only', 'routing_reason', 'handoff_notes.to_output_composer')) {
        if (-not $text.Contains($term)) {
            $failures.Add("quick_package_router.md missing routing guard: $term")
        }
    }
}

$composer = Join-Path $skill 'prompts/output_composer.md'
if (Test-Path -LiteralPath $composer -PathType Leaf) {
    $text = Get-Content -LiteralPath $composer -Encoding UTF8 -Raw
    foreach ($term in @('quick_package_router', 'delivery_mode', 'Revision Mode', 'Continue Mode', 'project_state', 'revision-patch-card', 'failure-diagnosis-card', 'Z-S01 -> IMG-S01 -> VID-S01', 'canvas_mode', 'prompts_only', 'CV-OP-01', '```text')) {
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

$qaReviewer = Join-Path $skill 'prompts/qa_reviewer.md'
if (Test-Path -LiteralPath $qaReviewer -PathType Leaf) {
    $text = Get-Content -LiteralPath $qaReviewer -Encoding UTF8 -Raw
    foreach ($term in @('preflight_check', 'prompt_patch', 'failure_repair', 'continuity_review', 'qa_output: preflight_card', 'project_state', 'character_drift', 'lighting_error', 'Project Packet Updates', 'to_output_composer')) {
        if (-not $text.Contains($term)) {
            $failures.Add("qa_reviewer.md missing term: $term")
        }
    }
}

$revisionBuilder = Join-Path $skill 'prompts/revision_patch_builder.md'
if (Test-Path -LiteralPath $revisionBuilder -PathType Leaf) {
    $text = Get-Content -LiteralPath $revisionBuilder -Encoding UTF8 -Raw
    foreach ($term in @('shot_patch', 'style_tune', 'duration_resize', 'aspect_ratio_change', 'platform_switch', 'asset_replace', 'affected_ids', 'preserved_ids', 'invalidated_ids', 'revision_state', 'to_output_composer')) {
        if (-not $text.Contains($term)) {
            $failures.Add("revision_patch_builder.md missing term: $term")
        }
    }
}

$revisionTemplate = Join-Path $skill 'templates/revision-patch-card.md'
if (Test-Path -LiteralPath $revisionTemplate -PathType Leaf) {
    $text = Get-Content -LiteralPath $revisionTemplate -Encoding UTF8 -Raw
    foreach ($term in @('template: revision-patch-card', 'delivery_mode: revision', '```json')) {
        if (-not $text.Contains($term)) {
            $failures.Add("revision-patch-card.md missing term: $term")
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
