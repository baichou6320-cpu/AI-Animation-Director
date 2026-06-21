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
    SKILL / "prompts/output_composer.md",
    SKILL / "prompts/quick_package_router.md",
    SKILL / "prompts/canvas_workflow_builder.md",
    SKILL / "prompts/image_prompt_builder.md",
    SKILL / "prompts/platform_adapter.md",
    SKILL / "prompts/qa_reviewer.md",
    SKILL / "prompts/revision_patch_builder.md",
    SKILL / "templates/jimeng-quick-package.md",
    SKILL / "templates/jimeng-canvas-package.md",
    SKILL / "templates/jimeng-continue-card.md",
    SKILL / "templates/project-state.json",
    SKILL / "templates/failure-diagnosis-card.md",
    SKILL / "templates/revision-patch-card.md",
    SKILL / "references/workflow.md",
    SKILL / "references/jimeng-canvas.md",
    SKILL / "references/prompt-templates.md",
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
        is_prompts_only = example.name == "prompts-only-jimeng.md"
        is_state_example = example.name.startswith("state-save-")
        is_revision_example = example.name.startswith("revision-")

        if is_jimeng and "IMG-REF" not in text:
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
        elif is_jimeng and not is_revision_example:
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
                "shots",
                "completed_steps",
                "current_step",
                "next_action",
            ]:
                if key not in state:
                    failures.append(f"project-state.json missing key: {key}")
            if state.get("state_type") != "ai_animation_director_project_state":
                failures.append("project-state.json has wrong state_type.")

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
        ]:
            if term not in text:
                failures.append(f"quick_package_router.md missing routing guard: {term}")

    if composer.is_file():
        text = read_text(composer)
        for term in [
            "本模块不负责判断交付模式",
            "路由结果是唯一事实来源",
            "Revision Mode",
            "Continue Mode",
            "逐镜头执行卡",
            "project_state",
            "revision-patch-card",
            "failure-diagnosis-card",
            "canvas_mode",
            "```text",
        ]:
            if term not in text:
                failures.append(f"output_composer.md missing delivery guard: {term}")
        if "## 默认判定规则" in text:
            failures.append(
                "output_composer.md must not contain a second delivery-mode decision table."
            )

    canvas_builder = SKILL / "prompts/canvas_workflow_builder.md"
    if canvas_builder.is_file():
        text = read_text(canvas_builder)
        for term in [
            "canvas_plan",
            "CV-MASTER",
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
            "高质量画面提示词规则",
            "前景",
            "中景",
            "背景",
            "Moebius / Jean Giraud",
            "大师杰作",
            "production-ready keyframe",
        ]:
            if term not in text:
                failures.append(f"image_prompt_builder.md missing term: {term}")

    prompt_templates = SKILL / "references/prompt-templates.md"
    if prompt_templates.is_file():
        text = read_text(prompt_templates)
        for term in [
            "Rich Visual Image Prompt",
            "Rich Prompt Quality Stack",
            "Weak Prompt Anti-Pattern",
            "Reference Style Translation",
            "Moebius / Jean Giraud",
            "visible nouns",
        ]:
            if term not in text:
                failures.append(f"prompt-templates.md missing term: {term}")

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
            "生成前自检",
            "project_state",
            "character_drift",
            "lighting_error",
            "Project Packet Updates",
            "to_output_composer",
        ]:
            if term not in text:
                failures.append(f"qa_reviewer.md missing term: {term}")

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
