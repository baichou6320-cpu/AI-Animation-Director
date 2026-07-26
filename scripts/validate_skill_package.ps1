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
Require-File (Join-Path $skill "prompts/creative_intake_interviewer.md")
Require-File (Join-Path $skill "prompts/creative_research_builder.md")
Require-File (Join-Path $skill "prompts/concept_pitch_builder.md")
Require-File (Join-Path $skill "prompts/approval_gate_manager.md")
Require-File (Join-Path $skill "prompts/output_composer.md")
Require-File (Join-Path $skill "prompts/quick_package_router.md")
Require-File (Join-Path $skill "prompts/canvas_workflow_builder.md")
Require-File (Join-Path $skill "prompts/director_scene_translation_builder.md")
Require-File (Join-Path $skill "prompts/asset_library_builder.md")
Require-File (Join-Path $skill "prompts/image_prompt_builder.md")
Require-File (Join-Path $skill "prompts/visual_reference_analyzer.md")
Require-File (Join-Path $skill "prompts/pixel_style_bible_builder.md")
Require-File (Join-Path $skill "prompts/animatic_builder.md")
Require-File (Join-Path $skill "prompts/platform_adapter.md")
Require-File (Join-Path $skill "prompts/prompt_quality_reviewer.md")
Require-File (Join-Path $skill "prompts/qa_reviewer.md")
Require-File (Join-Path $skill "prompts/revision_patch_builder.md")
Require-File (Join-Path $skill "prompts/seedance_storyboard_adapter.md")
Require-File (Join-Path $skill "prompts/seedance_motion_prompt_builder.md")
Require-File (Join-Path $skill "prompts/storyboard_panel_builder.md")
Require-File (Join-Path $skill "prompts/stage_gate_reviewer.md")
Require-File (Join-Path $skill "prompts/video_prompt_builder.md")
Require-File (Join-Path $skill "prompts/video_result_reviewer.md")
Require-File (Join-Path $skill "prompts/web_background_builder.md")
Require-File (Join-Path $skill "templates/jimeng-quick-package.md")
Require-File (Join-Path $skill "templates/jimeng-canvas-package.md")
Require-File (Join-Path $skill "templates/jimeng-continue-card.md")
Require-File (Join-Path $skill "templates/project-state.json")
Require-File (Join-Path $skill "templates/failure-diagnosis-card.md")
Require-File (Join-Path $skill "templates/revision-patch-card.md")
Require-File (Join-Path $skill "templates/concept-review-card.md")
Require-File (Join-Path $skill "templates/project-blueprint.md")
Require-File (Join-Path $skill "templates/keyframe-review-card.md")
Require-File (Join-Path $skill "templates/script-pipeline-project-structure.md")
Require-File (Join-Path $skill "templates/reference-index.md")
Require-File (Join-Path $skill "templates/project-progress-report.md")
Require-File (Join-Path $skill "templates/evolution-signal-card.md")
Require-File (Join-Path $skill "templates/director-analysis-template.md")
Require-File (Join-Path $skill "templates/asset-library-template.md")
Require-File (Join-Path $skill "templates/seedance-prompts-template.md")
Require-File (Join-Path $skill "templates/seedance-motion-prompts-template.md")
Require-File (Join-Path $skill "templates/storyboard-panel-template.md")
Require-File (Join-Path $skill "templates/render-sample-plan.md")
Require-File (Join-Path $skill "templates/stage-review-template.md")
Require-File (Join-Path $skill "templates/style-dna-card.md")
Require-File (Join-Path $skill "templates/pixel-style-bible.md")
Require-File (Join-Path $skill "templates/animatic-plan.json")
Require-File (Join-Path $skill "templates/learning-card.md")
Require-File (Join-Path $skill "templates/web-background-package.md")
Require-File (Join-Path $skill "templates/web-background-spec.json")
Require-File (Join-Path $skill "references/workflow.md")
Require-File (Join-Path $skill "references/styles.md")
Require-File (Join-Path $skill "references/jimeng-canvas.md")
Require-File (Join-Path $skill "references/prompt-templates.md")
Require-File (Join-Path $skill "examples/single-confirm-jimeng.md")
Require-File (Join-Path $skill "references/seedance-methodology.md")
Require-File (Join-Path $skill "references/pixel-animation-production.md")
$schemaNames = @(
    "project.schema.json",
    "intake.schema.json",
    "concept.schema.json",
    "style.schema.json",
    "assets.schema.json",
    "shots.schema.json",
    "prompt-pack.schema.json",
    "execution.schema.json",
    "reviews.schema.json",
    "web-background.schema.json"
)
foreach ($schemaName in $schemaNames) {
    Require-File (Join-Path $skill "schemas/$schemaName")
}
Require-File (Join-Path $skill "examples/pixel-cinematic-15s-4shots-jimeng.md")
Require-File (Join-Path $skill "examples/website-background-canyon-jimeng.md")
Require-File (Join-Path $root "examples/workspace/dew-light-pixel-15s-manifest.json")
Require-File (Join-Path $root "production_workspace/media.py")
Require-File (Join-Path $root "pyproject.toml")
Require-Dir (Join-Path $skill "examples")

$examples = Get-ChildItem -Path (Join-Path $skill "examples") -Filter "*.md" -File -ErrorAction SilentlyContinue
if ($examples.Count -lt 3) {
    $failures.Add("Expected at least 3 markdown examples.")
}

foreach ($example in $examples) {
    $text = Get-Content -LiteralPath $example.FullName -Encoding UTF8 -Raw
    $isStateExample = $example.Name.StartsWith('state-save-')
    $isRevisionExample = $example.Name.StartsWith('revision-')
    $isWebBackground = $example.Name.StartsWith('website-background-')

    if ($example.Name -match "jimeng" -and -not $isWebBackground -and $text -notmatch "IMG-REF") {
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
    elseif ($example.Name -match 'jimeng' -and -not $isRevisionExample -and -not $isWebBackground) {
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
        foreach ($property in @('schema_version', 'state_type', 'project', 'research_state', 'approval_state', 'generation_capabilities', 'approved_assets', 'script_state', 'reference_index', 'hero_image_state', 'shots', 'storyboard_requirements', 'render_plan', 'sample_review', 'progress_report', 'evolution_signals', 'video_execution', 'shot_tasks', 'completed_steps', 'current_step', 'next_action')) {
            if (-not ($state.PSObject.Properties.Name -contains $property)) {
                $failures.Add("project-state.json missing key: $property")
            }
        }
        if ($state.state_type -ne 'ai_animation_director_project_state') {
            $failures.Add('project-state.json has wrong state_type.')
        }
        if (@('single_confirm', 'strict_review', 'direct_run') -notcontains $state.approval_state.interaction_policy) {
            $failures.Add('project-state.json has invalid interaction_policy.')
        }
        if (@('not_started', 'pending', 'approved', 'bypassed') -notcontains $state.approval_state.qa_confirmation) {
            $failures.Add('project-state.json has invalid qa_confirmation.')
        }
        if (@('pending', 'approved', 'revision_requested', 'bypassed') -notcontains $state.approval_state.concept_approval) {
            $failures.Add('project-state.json has invalid concept_approval.')
        }
        if (@('not_started', 'pending', 'approved', 'revision_requested', 'bypassed') -notcontains $state.approval_state.keyframe_approval) {
            $failures.Add('project-state.json has invalid keyframe_approval.')
        }
        if (@('single_image_per_shot', 'first_last_frame', 'multi_reference_single_scene') -notcontains $state.video_execution.generation_strategy) {
            $failures.Add('project-state.json has invalid generation_strategy.')
        }
        foreach ($task in $state.shot_tasks.PSObject.Properties) {
            if ($task.Name -notmatch '^VID-S\d{2}$') {
                $failures.Add("project-state.json has invalid shot task id: $($task.Name)")
            }
            if ($task.Value.source_image -notmatch '^IMG-S\d{2}$') {
                $failures.Add("project-state.json $($task.Name) must reference one IMG-Sxx.")
            }
        }
    }
    catch {
        $failures.Add('project-state.json is not valid JSON.')
    }
}

$failureTemplate = Join-Path $skill 'templates/failure-diagnosis-card.md'
if (Test-Path -LiteralPath $failureTemplate -PathType Leaf) {
    $text = Get-Content -LiteralPath $failureTemplate -Encoding UTF8 -Raw
    foreach ($term in @('template: failure-diagnosis-card', 'continue_submode: failure_repair', 'character_drift', 'under_motion', 'reference_confusion', 'lighting_error', 'generation_blocked', '```json')) {
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
    foreach ($term in @('delivery_mode', 'target_delivery_mode', 'pipeline_mode', 'pixel_short_mode', 'pixel_stage', 'animatic_state', 'motion_contracts', 'finishing_state', 'seedance_harness_mode', 'seedance_harness', 'script_pipeline', 'script_state', 'reference_index', 'progress_report', 'storyboard_requirements', 'render_plan', 'sample_review', 'evolution_signals', 'Guided Intake', 'guided_intake', 'guided_intake_state', 'direct_assumption_mode', 'batch_window', 'Revision Mode', 'Continue Mode', 'Concept Review Mode', 'Keyframe Review Mode', 'concept_approval', 'keyframe_approval', 'approval_override', 'interaction_policy', 'qa_confirmation', 'single_confirm', 'strict_review', 'direct_run', 'generation_capabilities', 'execution_state', 'project_state', 'revision_state', 'failure_repair', 'canvas_mode', 'prompt_assets_only', 'routing_reason', 'handoff_notes.to_output_composer')) {
        if (-not $text.Contains($term)) {
            $failures.Add("quick_package_router.md missing routing guard: $term")
        }
    }
}

$composer = Join-Path $skill 'prompts/output_composer.md'
if (Test-Path -LiteralPath $composer -PathType Leaf) {
    $text = Get-Content -LiteralPath $composer -Encoding UTF8 -Raw
    foreach ($term in @('quick_package_router', 'delivery_mode', 'target_delivery_mode', 'pipeline_mode', 'Pixel Short Mode', 'pixel_stage', 'Motion Contract', '字符数不作为提示词通过标准', 'Seedance Harness Mode', 'Script Pipeline Mode', 'Concept Review Mode', 'Keyframe Review Mode', 'concept-review-card.md', 'keyframe-review-card.md', 'approval_override', 'interaction_policy', 'qa_confirmation', 'single_confirm', 'strict_review', 'direct_run', 'approved_assets', 'director_scene_book', 'asset_library', 'reference_index', 'reference_map', 'seedance_constraints', 'storyboard_requirements', 'render_plan', 'sample_review', 'evolution_signals', 'stage_reviews', 'SD-S01', 'SB-S', 'Seedance Motion Prompts', 'Guided Intake Mode', 'guided_intake_state', 'direct_assumption_mode', 'batch_window', 'Revision Mode', 'Continue Mode', 'project_state', 'revision-patch-card', 'failure-diagnosis-card', 'Z-S01 -> IMG-S01 -> VID-S01', 'canvas_mode', 'prompts_only', 'CV-OP-01', '```text')) {
        if (-not $text.Contains($term)) {
            $failures.Add("output_composer.md missing delivery guard: $term")
        }
    }
}

$directorSceneBuilder = Join-Path $skill 'prompts/director_scene_translation_builder.md'
if (Test-Path -LiteralPath $directorSceneBuilder -PathType Leaf) {
    $text = Get-Content -LiteralPath $directorSceneBuilder -Encoding UTF8 -Raw
    foreach ($term in @('Director Scene Translation Builder Prompt', 'BEAT-01', 'script_state', 'director_scene_book', 'seedance_constraints', 'Project Packet Updates', '0.5')) {
        if (-not $text.Contains($term)) {
            $failures.Add("director_scene_translation_builder.md missing term: $term")
        }
    }
}

$assetLibraryBuilder = Join-Path $skill 'prompts/asset_library_builder.md'
if (Test-Path -LiteralPath $assetLibraryBuilder -PathType Leaf) {
    $text = Get-Content -LiteralPath $assetLibraryBuilder -Encoding UTF8 -Raw
    foreach ($term in @('CHAR-A', 'SCENE-A', 'PROP-A', 'REF-CHAR-A', 'new', 'reuse', 'variant', 'reference_index', 'reference_map')) {
        if (-not $text.Contains($term)) {
            $failures.Add("asset_library_builder.md missing term: $term")
        }
    }
}

$seedanceAdapter = Join-Path $skill 'prompts/seedance_storyboard_adapter.md'
if (Test-Path -LiteralPath $seedanceAdapter -PathType Leaf) {
    $text = Get-Content -LiteralPath $seedanceAdapter -Encoding UTF8 -Raw
    foreach ($term in @('Seedance Storyboard Adapter Prompt', 'references/seedance-methodology.md', 'reference_map', 'seedance_constraints', 'prompt_assets.seedance_prompts', 'SD-S01', '0.5')) {
        if (-not $text.Contains($term)) {
            $failures.Add("seedance_storyboard_adapter.md missing term: $term")
        }
    }
}

$seedanceMotion = Join-Path $skill 'prompts/seedance_motion_prompt_builder.md'
if (Test-Path -LiteralPath $seedanceMotion -PathType Leaf) {
    $text = Get-Content -LiteralPath $seedanceMotion -Encoding UTF8 -Raw
    foreach ($term in @('Seedance Motion Prompt Builder Prompt', 'reference_index', 'Motion Prompt', 'storyboard_required=true', 'storyboard_requirements', 'render_plan.candidate_units', 'SD-S01')) {
        if (-not $text.Contains($term)) {
            $failures.Add("seedance_motion_prompt_builder.md missing term: $term")
        }
    }
}

$storyboardBuilder = Join-Path $skill 'prompts/storyboard_panel_builder.md'
if (Test-Path -LiteralPath $storyboardBuilder -PathType Leaf) {
    $text = Get-Content -LiteralPath $storyboardBuilder -Encoding UTF8 -Raw
    foreach ($term in @('Storyboard Panel Builder Prompt', 'storyboard_requirements', 'SB-S05', 'SD-S05', 'render_plan.storyboard_units', 'reference_index')) {
        if (-not $text.Contains($term)) {
            $failures.Add("storyboard_panel_builder.md missing term: $term")
        }
    }
}

$stageGateReviewer = Join-Path $skill 'prompts/stage_gate_reviewer.md'
if (Test-Path -LiteralPath $stageGateReviewer -PathType Leaf) {
    $text = Get-Content -LiteralPath $stageGateReviewer -Encoding UTF8 -Raw
    foreach ($term in @('Stage Gate Reviewer Prompt', 'director_scene', 'asset_library', 'reference_index', 'seedance_motion_prompt', 'storyboard_panel', 'sample_plan', 'seedance_prompt', 'PASS', 'FAIL', 'stage_reviews', 'evolution_signals')) {
        if (-not $text.Contains($term)) {
            $failures.Add("stage_gate_reviewer.md missing term: $term")
        }
    }
}

$creativeResearch = Join-Path $skill 'prompts/creative_research_builder.md'
if (Test-Path -LiteralPath $creativeResearch -PathType Leaf) {
    $text = Get-Content -LiteralPath $creativeResearch -Encoding UTF8 -Raw
    foreach ($term in @('Creative Research Builder Prompt', 'research_state.policy', 'required', 'recommended', 'skip', 'Research Brief', 'build_concept_pitch')) {
        if (-not $text.Contains($term)) {
            $failures.Add("creative_research_builder.md missing term: $term")
        }
    }
}

$conceptPitch = Join-Path $skill 'prompts/concept_pitch_builder.md'
if (Test-Path -LiteralPath $conceptPitch -PathType Leaf) {
    $text = Get-Content -LiteralPath $conceptPitch -Encoding UTF8 -Raw
    foreach ($term in @('Concept Pitch Builder Prompt', 'concept_pitch', 'concept_approval', 'keyframe_approval', 'await_concept_approval', 'REF-*', 'IMG-Sxx', 'VID-Sxx')) {
        if (-not $text.Contains($term)) {
            $failures.Add("concept_pitch_builder.md missing term: $term")
        }
    }
}

$approvalGate = Join-Path $skill 'prompts/approval_gate_manager.md'
if (Test-Path -LiteralPath $approvalGate -PathType Leaf) {
    $text = Get-Content -LiteralPath $approvalGate -Encoding UTF8 -Raw
    foreach ($term in @('Approval Gate Manager Prompt', 'interaction_policy', 'qa_confirmation', 'single_confirm', 'strict_review', 'direct_run', 'concept_approval', 'keyframe_approval', 'pending', 'approved', 'revision_requested', 'bypassed', 'approval_override', 'generation_capabilities', 'Project Packet Updates')) {
        if (-not $text.Contains($term)) {
            $failures.Add("approval_gate_manager.md missing term: $term")
        }
    }
}

$canvasBuilder = Join-Path $skill 'prompts/canvas_workflow_builder.md'
if (Test-Path -LiteralPath $canvasBuilder -PathType Leaf) {
    $text = Get-Content -LiteralPath $canvasBuilder -Encoding UTF8 -Raw
    foreach ($term in @('canvas_plan', 'CV-MASTER', 'layout_map', 'repair_ops', 'master_plus_sequences', 'prompt_assets_only', 'generate/import', 'Rich Visual Image Prompt', 'user_upload', 'export')) {
        if (-not $text.Contains($term)) {
            $failures.Add("canvas_workflow_builder.md missing term: $term")
        }
    }
}

$imageBuilder = Join-Path $skill 'prompts/image_prompt_builder.md'
if (Test-Path -LiteralPath $imageBuilder -PathType Leaf) {
    $text = Get-Content -LiteralPath $imageBuilder -Encoding UTF8 -Raw
    foreach ($term in @('Rich Visual Image Prompt', 'Prompt Density Tiers', 'Copy-Ready Rich Image Pattern', 'Prompt QA', 'Moebius / Jean Giraud', 'production-ready keyframe', 'direct_assumption_mode', 'approval_state.concept_approval', 'generation_capabilities.image_generation', 'keyframe_approval=pending')) {
        if (-not $text.Contains($term)) {
            $failures.Add("image_prompt_builder.md missing term: $term")
        }
    }
}

$promptTemplates = Join-Path $skill 'references/prompt-templates.md'
if (Test-Path -LiteralPath $promptTemplates -PathType Leaf) {
    $text = Get-Content -LiteralPath $promptTemplates -Encoding UTF8 -Raw
    foreach ($term in @('Rich Visual Image Prompt', 'Prompt Density Tiers', 'Copy-Ready Rich Image Pattern', 'Copy-Ready Rich Video Pattern', 'Rich Prompt Quality Stack', 'Prompt Quality Rubric', 'Video Motion Recipes', 'Visual Style Recipes', 'Aesthetic Calibration Presets', 'Weak Prompt Anti-Pattern', 'Reference Style Translation', 'Moebius / Jean Giraud', 'visible nouns')) {
        if (-not $text.Contains($term)) {
            $failures.Add("prompt-templates.md missing term: $term")
        }
    }
}

$platformAdapter = Join-Path $skill 'prompts/platform_adapter.md'
if (Test-Path -LiteralPath $platformAdapter -PathType Leaf) {
    $text = Get-Content -LiteralPath $platformAdapter -Encoding UTF8 -Raw
    foreach ($term in @('rich_image_prompt_adapter')) {
        if (-not $text.Contains($term)) {
            $failures.Add("platform_adapter.md missing rich image prompt term: $term")
        }
    }
}

$videoBuilder = Join-Path $skill 'prompts/video_prompt_builder.md'
if (Test-Path -LiteralPath $videoBuilder -PathType Leaf) {
    $text = Get-Content -LiteralPath $videoBuilder -Encoding UTF8 -Raw
    foreach ($term in @('Duration', 'Subject motion', 'Camera motion', 'Motion Contract', 'Copy-Ready Motion Pattern', '字符数不是质量指标', 'Prompt QA', 'VID-Sxx', 'approval_state.keyframe_approval', 'approved_assets', 'generation_capabilities.video_generation', 'single_image_per_shot', 'multi_reference_single_scene', 'split_first', 'execution_state.video_execution', 'execution_state.shot_tasks', 'pixel_style_bible', 'animatic_state', 'sample_review')) {
        if (-not $text.Contains($term)) {
            $failures.Add("video_prompt_builder.md missing term: $term")
        }
    }
}

$qaReviewer = Join-Path $skill 'prompts/qa_reviewer.md'
if (Test-Path -LiteralPath $qaReviewer -PathType Leaf) {
    $text = Get-Content -LiteralPath $qaReviewer -Encoding UTF8 -Raw
    foreach ($term in @('preflight_check', 'prompt_patch', 'failure_repair', 'continuity_review', 'prompt_quality_review', 'qa_output: preflight_card', 'project_state', 'character_drift', 'under_motion', 'reference_confusion', 'lighting_error', 'Project Packet Updates', 'to_output_composer')) {
        if (-not $text.Contains($term)) {
            $failures.Add("qa_reviewer.md missing term: $term")
        }
    }
}

$videoResultReviewer = Join-Path $skill 'prompts/video_result_reviewer.md'
if (Test-Path -LiteralPath $videoResultReviewer -PathType Leaf) {
    $text = Get-Content -LiteralPath $videoResultReviewer -Encoding UTF8 -Raw
    foreach ($term in @('Video Result Reviewer Prompt', 'requested_duration_seconds', 'actual_duration_seconds', 'under_motion', 'reference_confusion', 'single_image_per_shot', 'split_first', 'shot_tasks')) {
        if (-not $text.Contains($term)) {
            $failures.Add("video_result_reviewer.md missing term: $term")
        }
    }
}

$videoRetryExample = Join-Path $skill 'examples/video-retry-scifi-drone-30s.md'
if (Test-Path -LiteralPath $videoRetryExample -PathType Leaf) {
    $text = Get-Content -LiteralPath $videoRetryExample -Encoding UTF8 -Raw
    foreach ($term in @('duration_mismatch', 'under_motion', 'reference_confusion', 'single_image_per_shot', 'VID-S01', 'VID-S02', 'VID-S03', '"actual_duration_seconds": 10')) {
        if (-not $text.Contains($term)) {
            $failures.Add("video-retry-scifi-drone-30s.md missing term: $term")
        }
    }
}

$creativeInterviewer = Join-Path $skill 'prompts/creative_intake_interviewer.md'
if (Test-Path -LiteralPath $creativeInterviewer -PathType Leaf) {
    $text = Get-Content -LiteralPath $creativeInterviewer -Encoding UTF8 -Raw
    foreach ($term in @('动态提问规则', '每轮只选择 1-3 个', '最多两轮', 'input/intake.json', 'ready_for_blueprint', 'build_project_blueprint', 'guided_intake_state', 'collect_guided_intake_answers', 'direct_assumption_mode', 'video_type', 'emotional_target', 'visual_style')) {
        if (-not $text.Contains($term)) {
            $failures.Add("creative_intake_interviewer.md missing term: $term")
        }
    }
}

$stylesRef = Join-Path $skill 'references/styles.md'
if (Test-Path -LiteralPath $stylesRef -PathType Leaf) {
    $text = Get-Content -LiteralPath $stylesRef -Encoding UTF8 -Raw
    foreach ($term in @('Famous Animation Reference Translation', 'Warm Isekai Morning', 'Aesthetic Scene Presets', 'sky_island_morning', 'Do not over-police')) {
        if (-not $text.Contains($term)) {
            $failures.Add("styles.md missing term: $term")
        }
    }
}

$warmExample = Join-Path $skill 'examples/warm-isekai-30s-direct-batch-jimeng.md'
if (Test-Path -LiteralPath $warmExample -PathType Leaf) {
    $text = Get-Content -LiteralPath $warmExample -Encoding UTF8 -Raw
    foreach ($term in @('batch_window', 'S01-S02', 'pending_shots')) {
        if (-not $text.Contains($term)) {
            $failures.Add("warm-isekai-30s-direct-batch-jimeng.md missing term: $term")
        }
    }
}

$promptQuality = Join-Path $skill 'prompts/prompt_quality_reviewer.md'
if (Test-Path -LiteralPath $promptQuality -PathType Leaf) {
    $text = Get-Content -LiteralPath $promptQuality -Encoding UTF8 -Raw
    foreach ($term in @('Prompt QA', 'Project Packet Updates', 'IMG-Sxx', 'VID-Sxx', 'quality_scores', 'patch')) {
        if (-not $text.Contains($term)) {
            $failures.Add("prompt_quality_reviewer.md missing term: $term")
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

$seedanceMethodology = Join-Path $skill 'references/seedance-methodology.md'
if (Test-Path -LiteralPath $seedanceMethodology -PathType Leaf) {
    $text = Get-Content -LiteralPath $seedanceMethodology -Encoding UTF8 -Raw
    foreach ($term in @('Seedance Methodology Reference', 'seedance_constraints', 'SD-Sxx', '2.5', '0.5', '10')) {
        if (-not $text.Contains($term)) {
            $failures.Add("seedance-methodology.md missing term: $term")
        }
    }
}

$seedanceTemplates = @{
    'script-pipeline-project-structure.md' = @('script/ep01', 'assets/reference-index.md', 'assets/character-prompts.md', 'outputs/ep01/01-director-analysis.md', 'outputs/ep01/02-seedance-motion-prompts.md', 'outputs/ep01/03-storyboard-panels.md', 'outputs/ep01/05-sample-review.md')
    'reference-index.md' = @('template: reference-index', 'REF-HERO', 'REF-CHAR-A', 'REF-AUD-A', 'assets/images/storyboards', 'new', 'reuse', 'variant')
    'project-progress-report.md' = @('template: project-progress-report', 'pipeline_mode: `seedance_harness_mode`', 'delivery_mode: continue')
    'evolution-signal-card.md' = @('template: evolution-signal-card', 'pending_user_approval', 'evolution_signals', 'EV-001')
    'director-analysis-template.md' = @('01-director-analysis.md', 'BEAT-01', 'director_scene_book')
    'asset-library-template.md' = @('CHAR-A', 'SCENE-A', 'PROP-A', 'new / reuse / variant')
    'seedance-prompts-template.md' = @('02-seedance-prompts.md', 'REF-CHAR-A', 'SD-S01', '2.5', '0.5')
    'seedance-motion-prompts-template.md' = @('template: seedance-motion-prompts-template', 'SD-S01', 'storyboard', 'SB-S05')
    'storyboard-panel-template.md' = @('template: storyboard-panel-template', 'SB-S05', 'SD-S05', 'motion prompt')
    'render-sample-plan.md' = @('template: render-sample-plan', 'SAMPLE-01', 'sample_first', 'batch_allowed')
    'stage-review-template.md' = @('03-stage-review.md', 'director_scene', 'asset_library', 'seedance_prompt', 'PASS', 'FAIL')
}
foreach ($filename in $seedanceTemplates.Keys) {
    $path = Join-Path $skill ("templates/" + $filename)
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $text = Get-Content -LiteralPath $path -Encoding UTF8 -Raw
        foreach ($term in $seedanceTemplates[$filename]) {
            if (-not $text.Contains($term)) {
                $failures.Add("$filename missing term: $term")
            }
        }
    }
}

$seedanceExample = Join-Path $skill 'examples/seedance-script-pipeline-ep01.md'
if (Test-Path -LiteralPath $seedanceExample -PathType Leaf) {
    $text = Get-Content -LiteralPath $seedanceExample -Encoding UTF8 -Raw
    foreach ($term in @('delivery_mode: seedance_harness', 'pipeline_mode: seedance_harness_mode', 'script_pipeline', 'BEAT-01', 'CHAR-A', 'SCENE-A', 'PROP-A', 'Reference Index', 'REF-HERO', 'REF-SB-S02', 'SD-S01', 'SB-S02', 'SAMPLE-01', 'sample_first', 'stage_reviews', '```json')) {
        if (-not $text.Contains($term)) {
            $failures.Add("seedance-script-pipeline-ep01.md missing term: $term")
        }
    }
}

$conceptReviewTemplate = Join-Path $skill 'templates/concept-review-card.md'
if (Test-Path -LiteralPath $conceptReviewTemplate -PathType Leaf) {
    $text = Get-Content -LiteralPath $conceptReviewTemplate -Encoding UTF8 -Raw
    foreach ($term in @('template: concept-review-card', 'delivery_mode: concept_review', 'approval_gate: concept_approval')) {
        if (-not $text.Contains($term)) {
            $failures.Add("concept-review-card.md missing term: $term")
        }
    }
}

$keyframeReviewTemplate = Join-Path $skill 'templates/keyframe-review-card.md'
if (Test-Path -LiteralPath $keyframeReviewTemplate -PathType Leaf) {
    $text = Get-Content -LiteralPath $keyframeReviewTemplate -Encoding UTF8 -Raw
    foreach ($term in @('template: keyframe-review-card', 'delivery_mode: keyframe_review', 'approval_gate: keyframe_approval', 'REF-CHAR-A', 'IMG-S01')) {
        if (-not $text.Contains($term)) {
            $failures.Add("keyframe-review-card.md missing term: $term")
        }
    }
}

$conceptExample = Join-Path $skill 'examples/progressive-concept-review-historical.md'
if (Test-Path -LiteralPath $conceptExample -PathType Leaf) {
    $text = Get-Content -LiteralPath $conceptExample -Encoding UTF8 -Raw
    foreach ($term in @('delivery_mode: concept_review', 'Research Brief', 'https://', 'concept_approval', 'await_concept_approval')) {
        if (-not $text.Contains($term)) {
            $failures.Add("progressive-concept-review-historical.md missing term: $term")
        }
    }
    foreach ($forbidden in @('IMG-S01', 'VID-S01', 'REF-CHAR-A')) {
        if ($text.Contains($forbidden)) {
            $failures.Add("progressive-concept-review-historical.md crosses concept gate: $forbidden")
        }
    }
}

$keyframeExample = Join-Path $skill 'examples/progressive-keyframe-review.md'
if (Test-Path -LiteralPath $keyframeExample -PathType Leaf) {
    $text = Get-Content -LiteralPath $keyframeExample -Encoding UTF8 -Raw
    foreach ($term in @('delivery_mode: keyframe_review', 'concept_approval: approved', 'keyframe_approval: pending', 'REF-CHAR-A', 'IMG-S01', 'approved_assets', 'await_keyframe_approval')) {
        if (-not $text.Contains($term)) {
            $failures.Add("progressive-keyframe-review.md missing term: $term")
        }
    }
    if ($text.Contains('VID-S')) {
        $failures.Add('progressive-keyframe-review.md crosses keyframe gate.')
    }
}

$pixelBibleBuilder = Join-Path $skill 'prompts/pixel_style_bible_builder.md'
if (Test-Path -LiteralPath $pixelBibleBuilder -PathType Leaf) {
    $text = Get-Content -LiteralPath $pixelBibleBuilder -Encoding UTF8 -Raw
    foreach ($term in @('REF-HERO', '320x180', '1920x1080', '12fps', '24fps', '48', 'nearest-neighbor', '8%-15%', '学习卡')) {
        if (-not $text.Contains($term)) {
            $failures.Add("pixel_style_bible_builder.md missing term: $term")
        }
    }
}

$animaticBuilder = Join-Path $skill 'prompts/animatic_builder.md'
if (Test-Path -LiteralPath $animaticBuilder -PathType Leaf) {
    $text = Get-Content -LiteralPath $animaticBuilder -Encoding UTF8 -Raw
    foreach ($term in @('15 秒', 'S01=4s', 'S02=3s', 'S03=4s', 'S04=4s', 'animatic_state', 'build-animatic', '学习卡')) {
        if (-not $text.Contains($term)) {
            $failures.Add("animatic_builder.md missing term: $term")
        }
    }
}

$animaticTemplate = Join-Path $skill 'templates/animatic-plan.json'
if (Test-Path -LiteralPath $animaticTemplate -PathType Leaf) {
    try {
        $animatic = Get-Content -LiteralPath $animaticTemplate -Encoding UTF8 -Raw | ConvertFrom-Json
        $durations = @($animatic.shots | ForEach-Object { [double]$_.duration_seconds })
        if (($durations -join ',') -ne '4,3,4,4' -or (($durations | Measure-Object -Sum).Sum -ne 15)) {
            $failures.Add('animatic-plan.json must define 4/3/4/4 seconds totaling 15.')
        }
    }
    catch {
        $failures.Add('animatic-plan.json is not valid JSON.')
    }
}

$goldenManifest = Join-Path $root 'examples/workspace/dew-light-pixel-15s-manifest.json'
if (Test-Path -LiteralPath $goldenManifest -PathType Leaf) {
    try {
        $golden = Get-Content -LiteralPath $goldenManifest -Encoding UTF8 -Raw | ConvertFrom-Json
        if ($golden.project.pipeline_mode -ne 'pixel_short') {
            $failures.Add('golden pixel manifest must use pixel_short pipeline.')
        }
        if ($golden.project.sample_shot_id -ne 'S03') {
            $failures.Add('golden pixel manifest must use S03 as sample shot.')
        }
        $imageTasks = @($golden.tasks | Where-Object { $_.type -eq 'image' })
        $videoTasks = @($golden.tasks | Where-Object { $_.type -like 'video_*' })
        $duration = ($videoTasks | ForEach-Object { [double](($_.duration_hint -replace 's$', '')) } | Measure-Object -Sum).Sum
        if ($imageTasks.Count -ne 4 -or $videoTasks.Count -ne 4 -or $duration -ne 15) {
            $failures.Add('golden pixel manifest must contain four image and four video tasks totaling 15 seconds.')
        }
    }
    catch {
        $failures.Add('golden pixel manifest is not valid JSON.')
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
