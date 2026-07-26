from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "ai-animation-director"


REQUIRED_FILES = [
    ROOT / "README.md",
    ROOT / "README.zh-CN.md",
    ROOT / "LICENSE",
    ROOT / "SECURITY.md",
    ROOT / ".gitignore",
    ROOT / "docs/repository-metadata.md",
    ROOT / "docs/release-notes-v0.1.0.md",
    ROOT / "docs/improvement-backlog.md",
    ROOT / "docs/issue-seeds.md",
    ROOT / "scripts/create_github_repo.ps1",
    ROOT / "scripts/publish_to_github.ps1",
    SKILL / "SKILL.md",
    SKILL / "agents/openai.yaml",
    SKILL / "prompts/creative_intake_interviewer.md",
    SKILL / "prompts/creative_research_builder.md",
    SKILL / "prompts/concept_pitch_builder.md",
    SKILL / "prompts/approval_gate_manager.md",
    SKILL / "prompts/output_composer.md",
    SKILL / "prompts/quick_package_router.md",
    SKILL / "prompts/canvas_workflow_builder.md",
    SKILL / "prompts/director_scene_translation_builder.md",
    SKILL / "prompts/asset_library_builder.md",
    SKILL / "prompts/image_prompt_builder.md",
    SKILL / "prompts/visual_reference_analyzer.md",
    SKILL / "prompts/pixel_style_bible_builder.md",
    SKILL / "prompts/animatic_builder.md",
    SKILL / "prompts/platform_adapter.md",
    SKILL / "prompts/prompt_quality_reviewer.md",
    SKILL / "prompts/qa_reviewer.md",
    SKILL / "prompts/revision_patch_builder.md",
    SKILL / "prompts/seedance_storyboard_adapter.md",
    SKILL / "prompts/seedance_motion_prompt_builder.md",
    SKILL / "prompts/storyboard_panel_builder.md",
    SKILL / "prompts/stage_gate_reviewer.md",
    SKILL / "prompts/video_prompt_builder.md",
    SKILL / "prompts/video_result_reviewer.md",
    SKILL / "prompts/web_background_builder.md",
    SKILL / "templates/jimeng-quick-package.md",
    SKILL / "templates/jimeng-canvas-package.md",
    SKILL / "templates/jimeng-continue-card.md",
    SKILL / "templates/project-state.json",
    SKILL / "templates/failure-diagnosis-card.md",
    SKILL / "templates/revision-patch-card.md",
    SKILL / "templates/concept-review-card.md",
    SKILL / "templates/project-blueprint.md",
    SKILL / "templates/keyframe-review-card.md",
    SKILL / "templates/script-pipeline-project-structure.md",
    SKILL / "templates/reference-index.md",
    SKILL / "templates/project-progress-report.md",
    SKILL / "templates/evolution-signal-card.md",
    SKILL / "templates/director-analysis-template.md",
    SKILL / "templates/asset-library-template.md",
    SKILL / "templates/seedance-prompts-template.md",
    SKILL / "templates/seedance-motion-prompts-template.md",
    SKILL / "templates/storyboard-panel-template.md",
    SKILL / "templates/render-sample-plan.md",
    SKILL / "templates/stage-review-template.md",
    SKILL / "templates/style-dna-card.md",
    SKILL / "templates/pixel-style-bible.md",
    SKILL / "templates/animatic-plan.json",
    SKILL / "templates/learning-card.md",
    SKILL / "templates/web-background-package.md",
    SKILL / "templates/web-background-spec.json",
    SKILL / "references/workflow.md",
    SKILL / "references/styles.md",
    SKILL / "references/jimeng-canvas.md",
    SKILL / "references/prompt-templates.md",
    SKILL / "references/seedance-methodology.md",
    SKILL / "references/pixel-animation-production.md",
    SKILL / "schemas/project.schema.json",
    SKILL / "schemas/intake.schema.json",
    SKILL / "schemas/concept.schema.json",
    SKILL / "schemas/style.schema.json",
    SKILL / "schemas/assets.schema.json",
    SKILL / "schemas/shots.schema.json",
    SKILL / "schemas/prompt-pack.schema.json",
    SKILL / "schemas/execution.schema.json",
    SKILL / "schemas/reviews.schema.json",
    SKILL / "schemas/web-background.schema.json",
    SKILL / "examples/pixel-cinematic-15s-4shots-jimeng.md",
    SKILL / "examples/single-confirm-jimeng.md",
    SKILL / "examples/website-background-canyon-jimeng.md",
    ROOT / "examples/workspace/dew-light-pixel-15s-manifest.json",
    ROOT / "production_workspace/media.py",
    ROOT / "pyproject.toml",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def json_blocks(text: str) -> list[dict]:
    blocks: list[dict] = []
    for match in re.finditer(r"```json\r?\n(.*?)\r?\n```", text, re.S):
        blocks.append(json.loads(match.group(1)))
    return blocks


def main() -> int:
    failures: list[str] = []

    for path in REQUIRED_FILES:
        if not path.is_file():
            failures.append(f"Missing file: {path.relative_to(ROOT)}")

    schemas_dir = SKILL / "schemas"
    for schema_path in sorted(schemas_dir.glob("*.schema.json")):
        try:
            schema = json.loads(read_text(schema_path))
        except json.JSONDecodeError as exc:
            failures.append(f"{schema_path.name} is not valid JSON: {exc}")
            continue
        if schema.get("type") != "object":
            failures.append(f"{schema_path.name} must describe a JSON object.")

    examples_dir = SKILL / "examples"
    if not examples_dir.is_dir():
        failures.append(f"Missing directory: {examples_dir.relative_to(ROOT)}")
        examples: list[Path] = []
    else:
        examples = sorted(examples_dir.glob("*.md"))

    if len(examples) < 3:
        failures.append("Expected at least 3 markdown examples.")

    for example in examples:
        text = read_text(example)
        is_jimeng = "jimeng" in example.name
        is_web_background = example.name.startswith("website-background-")
        is_prompts_only = example.name == "prompts-only-jimeng.md"
        is_state_example = example.name.startswith("state-save-")
        is_revision_example = example.name.startswith("revision-")

        if is_jimeng and not is_web_background and "IMG-REF" not in text:
            failures.append(f"{example.name}: Jimeng example missing IMG-REF.")

        if not is_state_example and not is_revision_example:
            for match in re.finditer(r"VID-S(\d{2})", text):
                shot = match.group(1)
                required_image = f"`IMG-S{shot}`"
                if required_image not in text:
                    failures.append(f"{example.name}: VID-S{shot} does not reference IMG-S{shot}.")
                if is_jimeng and not is_prompts_only:
                    export_pattern = rf"导出为：`IMG-S{shot}`"
                    if not re.search(export_pattern, text):
                        failures.append(
                            f"{example.name}: canvas workflow does not export IMG-S{shot}."
                        )

        prompt_labels = len(
            re.findall(r"(?:复制提示词|素材提示词|操作提示词)：", text)
        )
        prompt_blocks = len(
            re.findall(
                r"(?:复制提示词|素材提示词|操作提示词)：[ \t]*\r?\n```text\r?\n(?=\S)",
                text,
            )
        )
        if prompt_labels != prompt_blocks:
            failures.append(
                f"{example.name}: every user-copyable prompt must start with a non-empty text code block."
            )

        if is_jimeng and is_prompts_only:
            if "CV-OP-" in text or "画布/区域" in text:
                failures.append(
                    "prompts-only-jimeng.md must not include canvas operation cards."
                )
        elif is_jimeng and not is_revision_example and not is_web_background:
            for term in ["逐镜头执行卡", "CV-MASTER", "CV-OP-", "Z-S01"]:
                if term not in text:
                    failures.append(f"{example.name}: missing canvas term {term}.")
            for old_section in ["画布资产与关键帧区", "即梦视频复制区"]:
                if old_section in text:
                    failures.append(
                        f"{example.name}: still uses separated legacy section {old_section}."
                    )

    prompts_only = SKILL / "examples/prompts-only-jimeng.md"
    if prompts_only.is_file():
        text = read_text(prompts_only)
        if "## 2." in text or "## 4." in text:
            failures.append(
                "prompts-only-jimeng.md should not include one-line setup or shot table sections."
            )
        if "project_state" in text or "ai_animation_director_project_state" in text:
            failures.append("prompts-only-jimeng.md must not default to project state.")

    quick_template = SKILL / "templates/jimeng-quick-package.md"
    if quick_template.is_file():
        text = read_text(quick_template)
        if "jimeng-canvas-package.md" not in text:
            failures.append(
                "jimeng-quick-package.md must point to the canonical canvas template."
            )

    canvas_template = SKILL / "templates/jimeng-canvas-package.md"
    if canvas_template.is_file():
        text = read_text(canvas_template)
        for term in [
            "CV-MASTER",
            "Z-ASSET",
            "逐镜头执行卡",
            "Z-S01 -> IMG-S01 -> VID-S01",
            "CV-OP-01",
            "操作类型：`blend`",
            "导出为：`IMG-S01`",
            "使用图片：`IMG-S01`",
        ]:
            if term not in text:
                failures.append(f"jimeng-canvas-package.md missing term: {term}")
        labels = len(re.findall(r"(?:复制提示词|素材提示词|操作提示词)：", text))
        blocks = len(
            re.findall(
                r"(?:复制提示词|素材提示词|操作提示词)：[ \t]*\r?\n```text\r?\n(?=\S)",
                text,
            )
        )
        if labels != blocks:
            failures.append(
                "jimeng-canvas-package.md: every user-copyable prompt must use a non-empty text block."
            )
        for match in re.finditer(r"使用图片：`IMG-S(\d{2})`", text):
            shot = match.group(1)
            if f"导出为：`IMG-S{shot}`" not in text:
                failures.append(
                    f"jimeng-canvas-package.md: VID-S{shot} has no matching canvas export."
                )
        for old_section in ["画布资产与关键帧区", "即梦视频复制区"]:
            if old_section in text:
                failures.append(
                    f"jimeng-canvas-package.md still uses legacy section {old_section}."
                )

    continue_template = SKILL / "templates/jimeng-continue-card.md"
    if continue_template.is_file():
        text = read_text(continue_template)
        for term in [
            "继续制作：下一步",
            "当前进度",
            "下一步",
            "完成检查",
            "失败后改法",
            "完成后回复",
        ]:
            if term not in text:
                failures.append(f"jimeng-continue-card.md missing term: {term}")

    state_template = SKILL / "templates/project-state.json"
    if state_template.is_file():
        try:
            state = json.loads(read_text(state_template))
        except json.JSONDecodeError as exc:
            failures.append(f"project-state.json is not valid JSON: {exc}")
        else:
            for key in [
                "schema_version",
                "state_type",
                "project",
                "research_state",
                "approval_state",
                "generation_capabilities",
                "approved_assets",
                "script_state",
                "reference_index",
                "hero_image_state",
                "shots",
                "storyboard_requirements",
                "render_plan",
                "sample_review",
                "progress_report",
                "evolution_signals",
                "video_execution",
                "shot_tasks",
                "completed_steps",
                "current_step",
                "next_action",
            ]:
                if key not in state:
                    failures.append(f"project-state.json missing key: {key}")
            if state.get("state_type") != "ai_animation_director_project_state":
                failures.append("project-state.json has wrong state_type.")
            approval = state.get("approval_state", {})
            if approval.get("interaction_policy") not in {
                "single_confirm",
                "strict_review",
                "direct_run",
            }:
                failures.append("project-state.json has invalid interaction_policy.")
            if approval.get("qa_confirmation") not in {
                "not_started",
                "pending",
                "approved",
                "bypassed",
            }:
                failures.append("project-state.json has invalid qa_confirmation.")
            if approval.get("concept_approval") not in {
                "pending",
                "approved",
                "revision_requested",
                "bypassed",
            }:
                failures.append("project-state.json has invalid concept_approval.")
            if approval.get("keyframe_approval") not in {
                "not_started",
                "pending",
                "approved",
                "revision_requested",
                "bypassed",
            }:
                failures.append("project-state.json has invalid keyframe_approval.")
            video_execution = state.get("video_execution", {})
            if video_execution.get("generation_strategy") not in {
                "single_image_per_shot",
                "first_last_frame",
                "multi_reference_single_scene",
            }:
                failures.append("project-state.json has invalid generation_strategy.")
            shot_tasks = state.get("shot_tasks", {})
            for task_id, task in shot_tasks.items():
                if not re.fullmatch(r"VID-S\d{2}", task_id):
                    failures.append(f"project-state.json has invalid shot task id: {task_id}")
                if not re.fullmatch(r"IMG-S\d{2}", str(task.get("source_image", ""))):
                    failures.append(f"project-state.json {task_id} must reference one IMG-Sxx.")

    failure_template = SKILL / "templates/failure-diagnosis-card.md"
    if failure_template.is_file():
        text = read_text(failure_template)
        for term in [
            "template: failure-diagnosis-card",
            "失败步骤",
            "失败类型",
            "修复策略",
            "重试提示词",
            "状态更新",
            "character_drift",
            "under_motion",
            "reference_confusion",
            "lighting_error",
            "generation_blocked",
            "```json",
        ]:
            if term not in text:
                failures.append(f"failure-diagnosis-card.md missing term: {term}")

    continue_examples = sorted((SKILL / "examples").glob("continue-*.md"))
    if len(continue_examples) < 2:
        failures.append("Expected at least 2 Continue Mode examples.")
    for continue_example in continue_examples:
        text = read_text(continue_example)
        for term in [
            "delivery_mode: continue",
            "next_action: single",
            "当前进度",
            "下一步",
            "完成后回复",
        ]:
            if term not in text:
                failures.append(f"{continue_example.name} missing term: {term}")
        vid_ids = set(re.findall(r"VID-S\d{2}", text))
        img_ids = set(re.findall(r"IMG-S\d{2}", text))
        if len(vid_ids) > 1 or len(img_ids) > 1:
            failures.append(
                f"{continue_example.name} must contain only one current shot."
            )
        for forbidden in ["项目锚点", "镜头表"]:
            if forbidden in text:
                failures.append(
                    f"{continue_example.name} must not repeat package content: {forbidden}"
                )

    state_example = SKILL / "examples/state-save-pixel-project.md"
    if state_example.is_file():
        text = read_text(state_example)
        try:
            blocks = json_blocks(text)
        except json.JSONDecodeError as exc:
            failures.append(f"state-save-pixel-project.md has invalid JSON: {exc}")
        else:
            if len(blocks) != 1:
                failures.append("state-save-pixel-project.md must have one JSON state block.")
            elif blocks[0].get("state_type") != "ai_animation_director_project_state":
                failures.append("state-save-pixel-project.md has wrong state_type.")

    failure_example = SKILL / "examples/failure-diagnosis-character-drift.md"
    if failure_example.is_file():
        text = read_text(failure_example)
        for term in [
            "continue_submode: failure_repair",
            "失败步骤：`VID-S02`",
            "失败类型：`character_drift`",
            "重试提示词",
            "状态更新",
            "retry VID-S02",
        ]:
            if term not in text:
                failures.append(f"failure-diagnosis-character-drift.md missing term: {term}")
        try:
            blocks = json_blocks(text)
        except json.JSONDecodeError as exc:
            failures.append(f"failure-diagnosis-character-drift.md has invalid JSON: {exc}")
        else:
            if not blocks or blocks[-1].get("failed_step") != "VID-S02":
                failures.append("failure-diagnosis-character-drift.md must update failed_step.")

    revision_example = SKILL / "examples/revision-change-shot-s02-jimeng.md"
    if revision_example.is_file():
        text = read_text(revision_example)
        for term in [
            "delivery_mode: revision",
            "revision_mode: shot_patch",
            "影响范围：`IMG-S02`、`VID-S02`",
            "保留不变",
            "状态更新",
            "regenerate IMG-S02",
        ]:
            if term not in text:
                failures.append(f"revision-change-shot-s02-jimeng.md missing term: {term}")
        try:
            blocks = json_blocks(text)
        except json.JSONDecodeError as exc:
            failures.append(f"revision-change-shot-s02-jimeng.md has invalid JSON: {exc}")
        else:
            if not blocks or blocks[-1].get("revision", {}).get("mode") != "shot_patch":
                failures.append("revision-change-shot-s02-jimeng.md must update revision.mode.")

    router = SKILL / "prompts/quick_package_router.md"
    composer = SKILL / "prompts/output_composer.md"
    if router.is_file():
        text = read_text(router)
        for term in [
            "唯一路由规则",
            "Guided Intake",
            "guided_intake",
            "guided_intake_state",
            "direct_assumption_mode",
            "batch_window",
            "平台不会覆盖片长和镜头规模判定",
            "delivery_mode",
            "Revision Mode",
            "Continue Mode",
            "execution_state",
            "project_state",
            "revision_state",
            "failure_repair",
            "canvas_mode",
            "prompt_assets_only",
            "pipeline_mode",
            "seedance_harness_mode",
            "seedance_harness",
            "script_pipeline",
            "script_state",
            "reference_index",
            "progress_report",
            "hero_image_state",
            "storyboard_requirements",
            "render_plan",
            "sample_review",
            "evolution_signals",
            "Seedance + 剧本/分集",
            "target_delivery_mode",
            "Concept Review Mode",
            "Keyframe Review Mode",
            "concept_approval",
            "keyframe_approval",
            "approval_override",
            "interaction_policy",
            "qa_confirmation",
            "single_confirm",
            "strict_review",
            "direct_run",
            "generation_capabilities",
            "pixel_short_mode",
            "pixel_stage",
            "animatic_state",
            "motion_contracts",
            "finishing_state",
        ]:
            if term not in text:
                failures.append(f"quick_package_router.md missing routing guard: {term}")

    if composer.is_file():
        text = read_text(composer)
        for term in [
            "本模块不负责判断交付模式",
            "路由结果是唯一事实来源",
            "Guided Intake Mode",
            "guided_intake_state",
            "Pixel Short Mode",
            "pixel_stage",
            "Motion Contract",
            "字符数不作为提示词通过标准",
            "direct_assumption_mode",
            "batch_window",
            "本版默认假设",
            "Revision Mode",
            "Continue Mode",
            "逐镜头执行卡",
            "project_state",
            "revision-patch-card",
            "failure-diagnosis-card",
            "canvas_mode",
            "Script Pipeline Mode",
            "Seedance Harness Mode",
            "director_scene_book",
            "asset_library",
            "reference_index",
            "reference_map",
            "seedance_constraints",
            "storyboard_requirements",
            "render_plan",
            "sample_review",
            "evolution_signals",
            "stage_reviews",
            "SD-S01",
            "参考设定",
            "氛围与画质",
            "画面内容",
            "SB-S",
            "样片测试",
            "@图片1",
            "Concept Review Mode",
            "Keyframe Review Mode",
            "concept-review-card.md",
            "keyframe-review-card.md",
            "approved_assets",
            "approval_override",
            "interaction_policy",
            "qa_confirmation",
            "single_confirm",
            "strict_review",
            "direct_run",
            "```text",
        ]:
            if term not in text:
                failures.append(f"output_composer.md missing delivery guard: {term}")
        if "## 默认判定规则" in text:
            failures.append(
                "output_composer.md must not contain a second delivery-mode decision table."
            )

    director_scene_builder = SKILL / "prompts/director_scene_translation_builder.md"
    if director_scene_builder.is_file():
        text = read_text(director_scene_builder)
        for term in [
            "导演讲戏本",
            "具体物理动作",
            "动作链",
            "光源位置",
            "5 秒连续镜头默认最多 2 个主要动作节拍",
            "前 0.5 秒或后 0.5 秒",
            "director_scene_book",
        ]:
            if term not in text:
                failures.append(
                    f"director_scene_translation_builder.md missing term: {term}"
                )

    asset_library_builder = SKILL / "prompts/asset_library_builder.md"
    if asset_library_builder.is_file():
        text = read_text(asset_library_builder)
        for term in [
            "CHAR-A",
            "SCENE-A",
            "PROP-A",
            "REF-CHAR-A",
            "`new`",
            "`reuse`",
            "`variant`",
            "不覆盖既有资产",
            "reference_map",
        ]:
            if term not in text:
                failures.append(f"asset_library_builder.md missing term: {term}")

    seedance_adapter = SKILL / "prompts/seedance_storyboard_adapter.md"
    if seedance_adapter.is_file():
        text = read_text(seedance_adapter)
        for term in [
            "references/seedance-methodology.md",
            "@图片/@视频/@音频",
            "引用用途",
            "10 秒以上必须分时段描述",
            "前 0.5 秒",
            "后 0.5 秒",
            "声音设计",
            "SD-S01",
        ]:
            if term not in text:
                failures.append(f"seedance_storyboard_adapter.md missing term: {term}")

    seedance_motion = SKILL / "prompts/seedance_motion_prompt_builder.md"
    if seedance_motion.is_file():
        text = read_text(seedance_motion)
        for term in [
            "Seedance Motion Prompt Builder Prompt",
            "reference_index",
            "参考设定",
            "氛围与画质",
            "画面内容",
            "storyboard_required=true",
            "storyboard_requirements",
            "render_plan.candidate_units",
            "动作类",
            "情绪类",
            "微表情",
        ]:
            if term not in text:
                failures.append(f"seedance_motion_prompt_builder.md missing term: {term}")

    storyboard_builder = SKILL / "prompts/storyboard_panel_builder.md"
    if storyboard_builder.is_file():
        text = read_text(storyboard_builder)
        for term in [
            "Storyboard Panel Builder Prompt",
            "storyboard_requirements",
            "6 宫格",
            "SB-S05",
            "SD-S05",
            "前景/中景/背景",
            "render_plan.storyboard_units",
            "reference_index",
        ]:
            if term not in text:
                failures.append(f"storyboard_panel_builder.md missing term: {term}")

    stage_gate_reviewer = SKILL / "prompts/stage_gate_reviewer.md"
    if stage_gate_reviewer.is_file():
        text = read_text(stage_gate_reviewer)
        for term in [
            "导演讲戏审核",
            "资产设计审核",
            "Reference Index 审核",
            "Seedance Motion Prompt 审核",
            "故事板审核",
            "样片计划审核",
            "Seedance 提示词审核",
            "平均分低于 8",
            "任一单项低于 6",
            "`FAIL`",
            "合规审核",
            "stage_reviews",
            "evolution_signals",
        ]:
            if term not in text:
                failures.append(f"stage_gate_reviewer.md missing term: {term}")

    canvas_builder = SKILL / "prompts/canvas_workflow_builder.md"
    if canvas_builder.is_file():
        text = read_text(canvas_builder)
        for term in [
            "canvas_plan",
            "CV-MASTER",
            "layout_map",
            "repair_ops",
            "局部修复卡规则",
            "master_plus_sequences",
            "prompt_assets_only",
            "generate/import",
            "Rich Visual Image Prompt",
            "export",
            "7-12 镜",
            "user_upload",
            "不重复生成",
        ]:
            if term not in text:
                failures.append(f"canvas_workflow_builder.md missing term: {term}")
        allowed_ops = {
            "generate/import",
            "arrange",
            "cutout",
            "blend",
            "inpaint",
            "expand",
            "remove",
            "upscale",
            "export",
        }
        used_ops = set(re.findall(r"operation_type:\s*([a-z/]+)", text))
        unknown_ops = sorted(used_ops - allowed_ops)
        if unknown_ops:
            failures.append(
                f"canvas_workflow_builder.md has unsupported operation types: {unknown_ops}"
            )

    image_builder = SKILL / "prompts/image_prompt_builder.md"
    if image_builder.is_file():
        text = read_text(image_builder)
        for term in [
            "Rich Visual Image Prompt",
            "Prompt Density Tiers",
            "Copy-Ready Rich Image Pattern",
            "高质量画面提示词规则",
            "提示词评分维度",
            "审美预设处理",
            "像素风分型规则",
            "前景",
            "中景",
            "背景",
            "Moebius / Jean Giraud",
            "大师杰作",
            "production-ready keyframe",
            "approval_state.concept_approval",
            "generation_capabilities.image_generation",
            "keyframe_approval=pending",
        ]:
            if term not in text:
                failures.append(f"image_prompt_builder.md missing term: {term}")

    prompt_templates = SKILL / "references/prompt-templates.md"
    if prompt_templates.is_file():
        text = read_text(prompt_templates)
        for term in [
            "Rich Visual Image Prompt",
            "Rich Prompt Quality Stack",
            "Copy-Ready Rich Image Pattern",
            "Copy-Ready Rich Video Pattern",
            "Prompt Quality Rubric",
            "Video Motion Recipes",
            "Visual Style Recipes",
            "Aesthetic Calibration Presets",
            "某知名动画导演",
            "Weak Prompt Anti-Pattern",
            "Reference Style Translation",
            "Moebius / Jean Giraud",
            "visible nouns",
        ]:
            if term not in text:
                failures.append(f"prompt-templates.md missing term: {term}")

    video_builder = SKILL / "prompts/video_prompt_builder.md"
    if video_builder.is_file():
        text = read_text(video_builder)
        for term in [
            "运动配方",
            "Motion Contract",
            "Copy-Ready Motion Pattern",
            "字符数不是质量指标",
            "温馨异世界日常视频",
            "什么动",
            "什么不动",
            "像素风视频默认",
            "给 Prompt QA 模块",
            "approval_state.keyframe_approval",
            "approved_assets",
            "generation_capabilities.video_generation",
            "single_image_per_shot",
            "multi_reference_single_scene",
            "split_first",
            "execution_state.video_execution",
            "execution_state.shot_tasks",
            "pixel_style_bible",
            "animatic_state",
            "sample_review",
        ]:
            if term not in text:
                failures.append(f"video_prompt_builder.md missing term: {term}")

    platform_adapter = SKILL / "prompts/platform_adapter.md"
    if platform_adapter.is_file():
        text = read_text(platform_adapter)
        for term in [
            "前景",
            "中景",
            "背景",
            "主色调",
            "大师杰作",
            "森林小屋",
        ]:
            if term not in text:
                failures.append(f"platform_adapter.md missing rich image prompt term: {term}")

    qa_reviewer = SKILL / "prompts/qa_reviewer.md"
    if qa_reviewer.is_file():
        text = read_text(qa_reviewer)
        for term in [
            "preflight_check",
            "prompt_patch",
            "failure_repair",
            "continuity_review",
            "prompt_quality_review",
            "生成前自检",
            "project_state",
            "character_drift",
            "under_motion",
            "reference_confusion",
            "lighting_error",
            "Project Packet Updates",
            "to_output_composer",
        ]:
            if term not in text:
                failures.append(f"qa_reviewer.md missing term: {term}")

    video_result_reviewer = SKILL / "prompts/video_result_reviewer.md"
    if video_result_reviewer.is_file():
        text = read_text(video_result_reviewer)
        for term in [
            "Video Result Reviewer Prompt",
            "requested_duration_seconds",
            "actual_duration_seconds",
            "under_motion",
            "reference_confusion",
            "single_image_per_shot",
            "split_first",
            "shot_tasks",
        ]:
            if term not in text:
                failures.append(f"video_result_reviewer.md missing term: {term}")

    video_retry_example = SKILL / "examples/video-retry-scifi-drone-30s.md"
    if video_retry_example.is_file():
        text = read_text(video_retry_example)
        for term in [
            "duration_mismatch",
            "under_motion",
            "reference_confusion",
            "single_image_per_shot",
            "VID-S01",
            "VID-S02",
            "VID-S03",
            '"actual_duration_seconds": 10',
        ]:
            if term not in text:
                failures.append(f"video-retry-scifi-drone-30s.md missing term: {term}")

    creative_interviewer = SKILL / "prompts/creative_intake_interviewer.md"
    if creative_interviewer.is_file():
        text = read_text(creative_interviewer)
        for term in [
            "动态提问规则",
            "每轮只选择 1-3 个",
            "最多两轮",
            "input/intake.json",
            "ready_for_blueprint",
            "build_project_blueprint",
            "direct_assumption_mode",
            "collect_guided_intake_answers",
            "IMG-*",
            "VID-*",
        ]:
            if term not in text:
                failures.append(f"creative_intake_interviewer.md missing term: {term}")

    creative_research = SKILL / "prompts/creative_research_builder.md"
    if creative_research.is_file():
        text = read_text(creative_research)
        for term in [
            "research_state.policy",
            "required",
            "recommended",
            "skip",
            "Research Brief",
            "来源",
            "未验证假设",
            "不下载或复用他人素材",
            "build_concept_pitch",
        ]:
            if term not in text:
                failures.append(f"creative_research_builder.md missing term: {term}")

    concept_pitch = SKILL / "prompts/concept_pitch_builder.md"
    if concept_pitch.is_file():
        text = read_text(concept_pitch)
        for term in [
            "2-3 个真正不同的创意方向",
            "推荐方向",
            "最多 3 个",
            "concept_approval",
            "keyframe_approval",
            "await_concept_approval",
            "不生成 `REF-*`、`IMG-Sxx`、`VID-Sxx`",
        ]:
            if term not in text:
                failures.append(f"concept_pitch_builder.md missing term: {term}")

    approval_gate = SKILL / "prompts/approval_gate_manager.md"
    if approval_gate.is_file():
        text = read_text(approval_gate)
        for term in [
            "interaction_policy",
            "qa_confirmation",
            "single_confirm",
            "strict_review",
            "direct_run",
            "concept_approval",
            "keyframe_approval",
            "pending",
            "approved",
            "revision_requested",
            "bypassed",
            "approval_override",
            "generation_capabilities",
            "Project Packet Updates",
        ]:
            if term not in text:
                failures.append(f"approval_gate_manager.md missing term: {term}")

    single_confirm_example = SKILL / "examples/single-confirm-jimeng.md"
    if single_confirm_example.is_file():
        text = read_text(single_confirm_example)
        for term in [
            "唯一一次 QA",
            "interaction_policy: single_confirm",
            "qa_confirmation: approved",
            "keyframe_approval: bypassed",
            "IMG-S01",
            "IMG-S04",
            "VID-S01",
            "VID-S04",
            "不再要求用户逐镜回复",
        ]:
            if term not in text:
                failures.append(f"single-confirm-jimeng.md missing term: {term}")

    styles_ref = SKILL / "references/styles.md"
    if styles_ref.is_file():
        text = read_text(styles_ref)
        for term in [
            "Famous Animation Reference Translation",
            "Warm Isekai Morning",
            "Aesthetic Scene Presets",
            "sky_island_morning",
            "Do not over-police",
        ]:
            if term not in text:
                failures.append(f"styles.md missing term: {term}")

    warm_example = SKILL / "examples/warm-isekai-30s-direct-batch-jimeng.md"
    if warm_example.is_file():
        text = read_text(warm_example)
        for term in [
            "本版默认假设",
            "batch_window",
            "S01-S02",
            "风格已转译",
            "pending_shots",
        ]:
            if term not in text:
                failures.append(f"warm-isekai-30s-direct-batch-jimeng.md missing term: {term}")

    prompt_quality = SKILL / "prompts/prompt_quality_reviewer.md"
    if prompt_quality.is_file():
        text = read_text(prompt_quality)
        for term in [
            "生图提示词评分维度",
            "视频提示词评分维度",
            "生图完整性检查",
            "Motion Contract 检查",
            "像素风",
            "IMG-Sxx",
            "style_dna",
            "pixel_style_bible",
            "Prompt QA",
            "Project Packet Updates",
        ]:
            if term not in text:
                failures.append(f"prompt_quality_reviewer.md missing term: {term}")

    revision_builder = SKILL / "prompts/revision_patch_builder.md"
    if revision_builder.is_file():
        text = read_text(revision_builder)
        for term in [
            "shot_patch",
            "style_tune",
            "duration_resize",
            "aspect_ratio_change",
            "platform_switch",
            "asset_replace",
            "affected_ids",
            "preserved_ids",
            "invalidated_ids",
            "revision_state",
            "to_output_composer",
        ]:
            if term not in text:
                failures.append(f"revision_patch_builder.md missing term: {term}")

    revision_template = SKILL / "templates/revision-patch-card.md"
    if revision_template.is_file():
        text = read_text(revision_template)
        for term in [
            "template: revision-patch-card",
            "delivery_mode: revision",
            "改稿类型",
            "影响范围",
            "保留不变",
            "替换内容",
            "状态更新",
            "```json",
        ]:
            if term not in text:
                failures.append(f"revision-patch-card.md missing term: {term}")

    seedance_methodology = SKILL / "references/seedance-methodology.md"
    if seedance_methodology.is_file():
        text = read_text(seedance_methodology)
        for term in [
            "@图片",
            "@视频",
            "@音频",
            "2.5 秒",
            "0.5 秒",
            "10 秒以上",
            "声音设计",
            "用途说明",
        ]:
            if term not in text:
                failures.append(f"seedance-methodology.md missing term: {term}")

    seedance_templates = {
        "script-pipeline-project-structure.md": [
            "script/ep01",
            "assets/reference-index.md",
            "assets/character-prompts.md",
            "outputs/ep01/01-director-analysis.md",
            "outputs/ep01/02-seedance-motion-prompts.md",
            "outputs/ep01/03-storyboard-panels.md",
            "outputs/ep01/05-sample-review.md",
        ],
        "reference-index.md": [
            "template: reference-index",
            "REF-HERO",
            "@图片1",
            "@音频1",
            "assets/images/storyboards",
            "new",
            "reuse",
            "variant",
        ],
        "project-progress-report.md": [
            "template: project-progress-report",
            "pipeline_mode: `seedance_harness_mode`",
            "当前阶段",
            "待审核",
            "只做下一步",
        ],
        "evolution-signal-card.md": [
            "template: evolution-signal-card",
            "进化信号待确认",
            "同意进化",
            "pending_user_approval",
            "evolution_signals",
        ],
        "director-analysis-template.md": [
            "导演讲戏本",
            "BEAT-01",
            "动作节拍数",
            "director_scene_book",
        ],
        "asset-library-template.md": [
            "CHAR-A",
            "SCENE-A",
            "PROP-A",
            "new / reuse / variant",
        ],
        "seedance-prompts-template.md": [
            "@图片1",
            "SD-S01",
            "节拍密度",
            "安全区",
            "声音",
        ],
        "seedance-motion-prompts-template.md": [
            "template: seedance-motion-prompts-template",
            "参考设定",
            "氛围与画质",
            "画面内容",
            "storyboard",
            "SB-S05",
        ],
        "storyboard-panel-template.md": [
            "template: storyboard-panel-template",
            "6 宫格",
            "SB-S05",
            "SD-S05",
            "每格必须对应 motion prompt",
        ],
        "render-sample-plan.md": [
            "template: render-sample-plan",
            "样片优先",
            "SAMPLE-01",
            "sample_first",
            "batch_allowed",
        ],
        "stage-review-template.md": [
            "PASS",
            "FAIL",
            "平均分",
            "最低单项",
            "合规审核",
        ],
    }
    for filename, terms in seedance_templates.items():
        path = SKILL / "templates" / filename
        if path.is_file():
            text = read_text(path)
            for term in terms:
                if term not in text:
                    failures.append(f"{filename} missing term: {term}")

    seedance_example = SKILL / "examples/seedance-script-pipeline-ep01.md"
    if seedance_example.is_file():
        text = read_text(seedance_example)
        for term in [
            "delivery_mode: seedance_harness",
            "pipeline_mode: seedance_harness_mode",
            "script_pipeline",
            "BEAT-01",
            "CHAR-A",
            "SCENE-A",
            "PROP-A",
            "Reference Index",
            "REF-HERO",
            "REF-SB-S02",
            "@图片1",
            "@音频1",
            "SD-S01",
            "参考设定",
            "氛围与画质",
            "画面内容",
            "SB-S02",
            "样片测试计划",
            "sample_first",
            "声音",
            "阶段审核",
            "evolution_signal",
            "stage_reviews",
        ]:
            if term not in text:
                failures.append(
                    f"seedance-script-pipeline-ep01.md missing term: {term}"
                )
        try:
            blocks = json_blocks(text)
        except json.JSONDecodeError as exc:
            failures.append(f"seedance-script-pipeline-ep01.md has invalid JSON: {exc}")
        else:
            if not blocks or blocks[-1].get("pipeline_mode") != "seedance_harness_mode":
                failures.append(
                    "seedance-script-pipeline-ep01.md must save seedance_harness_mode state."
                )
            if blocks and "script_pipeline" not in str(blocks[-1].get("legacy_pipeline_mode", "")):
                failures.append(
                    "seedance-script-pipeline-ep01.md must keep script_pipeline compatibility."
                )

    concept_review_template = SKILL / "templates/concept-review-card.md"
    if concept_review_template.is_file():
        text = read_text(concept_review_template)
        for term in [
            "template: concept-review-card",
            "delivery_mode: concept_review",
            "approval_gate: concept_approval",
            "确认方向 A",
            "不生成视频",
        ]:
            if term not in text:
                failures.append(f"concept-review-card.md missing term: {term}")

    keyframe_review_template = SKILL / "templates/keyframe-review-card.md"
    if keyframe_review_template.is_file():
        text = read_text(keyframe_review_template)
        for term in [
            "template: keyframe-review-card",
            "delivery_mode: keyframe_review",
            "approval_gate: keyframe_approval",
            "REF-CHAR-A",
            "IMG-S01",
            "关键帧确认",
            "未确认前不生成视频",
        ]:
            if term not in text:
                failures.append(f"keyframe-review-card.md missing term: {term}")

    concept_example = SKILL / "examples/progressive-concept-review-historical.md"
    if concept_example.is_file():
        text = read_text(concept_example)
        for term in [
            "delivery_mode: concept_review",
            "Research Brief",
            "https://",
            "concept_approval",
            '"pending"',
            "await_concept_approval",
        ]:
            if term not in text:
                failures.append(
                    f"progressive-concept-review-historical.md missing term: {term}"
                )
        for forbidden in ["IMG-S01", "VID-S01", "REF-CHAR-A"]:
            if forbidden in text:
                failures.append(
                    f"progressive-concept-review-historical.md crosses concept gate: {forbidden}"
                )

    keyframe_example = SKILL / "examples/progressive-keyframe-review.md"
    if keyframe_example.is_file():
        text = read_text(keyframe_example)
        for term in [
            "delivery_mode: keyframe_review",
            "concept_approval: approved",
            "keyframe_approval: pending",
            "REF-CHAR-A",
            "IMG-S01",
            "approved_assets",
            "await_keyframe_approval",
        ]:
            if term not in text:
                failures.append(f"progressive-keyframe-review.md missing term: {term}")
        if "VID-S" in text:
            failures.append("progressive-keyframe-review.md crosses keyframe gate.")

    pixel_bible_builder = SKILL / "prompts/pixel_style_bible_builder.md"
    if pixel_bible_builder.is_file():
        text = read_text(pixel_bible_builder)
        for term in [
            "REF-HERO",
            "320x180",
            "1920x1080",
            "12fps",
            "24fps",
            "48",
            "nearest-neighbor",
            "8%-15%",
            "学习卡",
        ]:
            if term not in text:
                failures.append(f"pixel_style_bible_builder.md missing term: {term}")

    animatic_builder = SKILL / "prompts/animatic_builder.md"
    if animatic_builder.is_file():
        text = read_text(animatic_builder)
        for term in [
            "15 秒",
            "S01=4s",
            "S02=3s",
            "S03=4s",
            "S04=4s",
            "animatic_state",
            "build-animatic",
            "学习卡",
        ]:
            if term not in text:
                failures.append(f"animatic_builder.md missing term: {term}")

    animatic_template = SKILL / "templates/animatic-plan.json"
    if animatic_template.is_file():
        try:
            animatic_data = json.loads(read_text(animatic_template))
        except json.JSONDecodeError as exc:
            failures.append(f"animatic-plan.json is not valid JSON: {exc}")
        else:
            durations = [shot.get("duration_seconds") for shot in animatic_data.get("shots", [])]
            if durations != [4, 3, 4, 4] or sum(durations) != 15:
                failures.append("animatic-plan.json must define 4/3/4/4 seconds totaling 15.")

    golden_manifest = ROOT / "examples/workspace/dew-light-pixel-15s-manifest.json"
    if golden_manifest.is_file():
        try:
            golden_data = json.loads(read_text(golden_manifest))
        except json.JSONDecodeError as exc:
            failures.append(f"golden pixel manifest is not valid JSON: {exc}")
        else:
            project = golden_data.get("project", {})
            tasks = golden_data.get("tasks", [])
            if project.get("pipeline_mode") != "pixel_short":
                failures.append("golden pixel manifest must use pixel_short pipeline.")
            if project.get("sample_shot_id") != "S03":
                failures.append("golden pixel manifest must use S03 as sample shot.")
            image_ids = {task.get("id") for task in tasks if task.get("type") == "image"}
            video_ids = {task.get("id") for task in tasks if str(task.get("type", "")).startswith("video_")}
            expected_ids = {f"img_shot_{index:03d}" for index in range(1, 5)}
            expected_video_ids = {f"vid_shot_{index:03d}" for index in range(1, 5)}
            if image_ids != expected_ids or video_ids != expected_video_ids:
                failures.append("golden pixel manifest must contain four image and four video shot tasks.")
            if sum(float(str(task.get("duration_hint", "0")).rstrip("s")) for task in tasks if task.get("id") in expected_video_ids) != 15:
                failures.append("golden pixel manifest video durations must total 15 seconds.")

    outputs_dir = SKILL / "outputs"
    output_files = [
        path
        for path in outputs_dir.rglob("*")
        if path.is_file() and path.name != ".gitkeep"
    ]
    if output_files:
        failures.append(
            f"outputs/ contains generated files that should not be published: {len(output_files)}"
        )

    if failures:
        print("Skill package validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Skill package validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
