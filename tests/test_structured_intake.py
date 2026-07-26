from __future__ import annotations

import json

import pytest

from production_workspace.intake_service import (
    answer_intake,
    approve_project_blueprint,
    build_project_blueprint,
    plan_intake_questions,
    request_blueprint_revision,
)
from production_workspace.models import ApprovalStatus
from production_workspace.preproduction_models import (
    ArtifactStatus,
    InteractionPolicy,
    IntakeStatus,
    ProjectBlueprint,
    ProjectConstraints,
    PromptKind,
    PromptPackArtifact,
    StructuredPrompt,
)
from production_workspace.preproduction_storage import (
    StructuredProjectError,
    create_draft_project,
    load_structured_artifact,
    load_structured_manifest,
    save_structured_artifact,
    save_structured_manifest,
    validate_structured_project,
)


def _blueprint() -> ProjectBlueprint:
    return ProjectBlueprint(
        one_sentence_understanding="一段温馨的异世界晨间生活短片。",
        structured_summary={
            "video_type": "animation_short",
            "duration_seconds": 15,
            "shot_count": 4,
            "has_visual_references": False,
        },
        recommended_story_direction="主角醒来、准备早餐、推窗看见浮岛晨光。",
        ending_direction="以热茶蒸汽和远处钟声收束。",
        style_direction="温暖手绘幻想动画，生活化细节。",
        color_lighting_direction="清晨金色侧光，低对比柔和阴影。",
        camera_direction="固定镜头和缓慢推近，每镜只承担一个动作。",
        assumptions=["无对白"],
        editable_fields=["主角物种", "房间陈设", "结尾景别"],
    )


def test_dynamic_intake_only_asks_missing_question_groups(tmp_path):
    project_root = create_draft_project(
        tmp_path,
        project_id="known-visuals",
        title="已知审美项目",
        raw_input="我想做一段温馨异世界早晨动画",
        extracted_fields={
            "platform": "jimeng",
            "deliverable": "jimeng_quick_package",
            "has_visual_references": False,
        },
        constraints=ProjectConstraints(
            duration_seconds=15,
            aspect_ratio="16:9",
            shot_count=4,
            emotional_target="warm",
            visual_style="hand_drawn_fantasy",
            platform="jimeng",
            deliverable="jimeng_quick_package",
        ),
    )

    questions = plan_intake_questions(project_root)

    assert 1 <= len(questions) <= 3
    assert {question.id for question in questions} == {"project_goal"}
    assert all(question.options for question in questions)


def test_two_qa_rounds_apply_defaults_without_repeating_questions(tmp_path):
    project_root = create_draft_project(
        tmp_path,
        project_id="partial-answers",
        title="部分回答项目",
        raw_input="我想做一个异世界动画",
        interaction_policy=InteractionPolicy.STRICT_REVIEW,
    )

    first_questions = plan_intake_questions(project_root)
    assert len(first_questions) == 3
    answer_intake(
        project_root,
        {
            "emotional_target": "warm",
            "visual_style": "hand_drawn_fantasy",
        },
    )
    second_questions = plan_intake_questions(project_root)

    assert second_questions
    assert not {question.id for question in first_questions}.intersection(
        {question.id for question in second_questions}
    )
    final_intake = answer_intake(
        project_root,
        {"has_visual_references": False},
    )

    assert final_intake.qa_round == 2
    assert final_intake.status == IntakeStatus.READY_FOR_BLUEPRINT
    assert final_intake.missing_required == []
    assert final_intake.assumptions["duration_seconds"] == 15
    assert final_intake.assumptions["video_type"] == "animation_short"


def test_single_confirm_applies_defaults_and_auto_opens_prompt_stages(tmp_path):
    project_root = create_draft_project(
        tmp_path,
        project_id="single-confirm",
        title="单次确认项目",
        raw_input="我想做一个温馨异世界动画",
    )

    questions = plan_intake_questions(project_root)
    assert 1 <= len(questions) <= 3

    intake = answer_intake(
        project_root,
        {
            "emotional_target": "warm",
            "visual_style": "hand_drawn_fantasy",
        },
    )
    assert intake.qa_round == 1
    assert intake.status == IntakeStatus.READY_FOR_BLUEPRINT
    assert intake.missing_required == []
    assert intake.assumptions["duration_seconds"] == 15

    build_project_blueprint(project_root, _blueprint())
    manifest = load_structured_manifest(project_root)
    assert manifest.approvals.interaction_policy == InteractionPolicy.SINGLE_CONFIRM
    assert manifest.approvals.qa_confirmation == ApprovalStatus.APPROVED
    assert manifest.approvals.concept_approval == ApprovalStatus.APPROVED
    assert manifest.approvals.keyframe_approval == ApprovalStatus.BYPASSED
    assert manifest.approvals.approval_override is False
    assert manifest.next_action == "build_style_artifact"

    image_pack = PromptPackArtifact(
        project_id=manifest.project_id,
        kind=PromptKind.IMAGE,
        prompts=[StructuredPrompt(id="IMG-S01", shot_id="S01", prompt="image")],
    )
    video_pack = PromptPackArtifact(
        project_id=manifest.project_id,
        kind=PromptKind.VIDEO,
        prompts=[StructuredPrompt(id="VID-S01", shot_id="S01", prompt="video")],
    )
    save_structured_artifact(project_root, manifest.files.image_prompts, image_pack)
    save_structured_artifact(project_root, manifest.files.video_prompts, video_pack)


def test_direct_run_skips_questions_and_records_override(tmp_path):
    project_root = create_draft_project(
        tmp_path,
        project_id="direct-run",
        title="直接执行项目",
        raw_input="直接做一个 15 秒异世界动画",
        interaction_policy=InteractionPolicy.DIRECT_RUN,
    )

    assert plan_intake_questions(project_root) == []
    manifest = load_structured_manifest(project_root)
    intake = load_structured_artifact(project_root, manifest.files.intake)
    assert intake.status == IntakeStatus.READY_FOR_BLUEPRINT
    assert manifest.approvals.qa_confirmation == ApprovalStatus.BYPASSED
    assert manifest.approvals.approval_override is True

    build_project_blueprint(project_root, _blueprint())
    manifest = load_structured_manifest(project_root)
    assert manifest.approvals.concept_approval == ApprovalStatus.BYPASSED
    assert manifest.approvals.keyframe_approval == ApprovalStatus.BYPASSED
    assert manifest.approvals.approval_override is True


def test_blueprint_cannot_be_built_before_intake_is_ready(tmp_path):
    project_root = create_draft_project(
        tmp_path,
        project_id="unfinished-intake",
        title="未完成 Intake",
        raw_input="一个动画想法",
    )

    with pytest.raises(StructuredProjectError, match="Intake 尚未完成"):
        build_project_blueprint(project_root, _blueprint())


def test_complete_answers_are_synced_to_project_constraints(tmp_path):
    project_root = create_draft_project(
        tmp_path,
        project_id="complete-intake",
        title="完整回答",
        raw_input="网站背景动画",
        constraints=ProjectConstraints(
            duration_seconds=15,
            aspect_ratio="16:9",
            shot_count=1,
        ),
    )

    answer_intake(
        project_root,
        {
            "video_type": "website_background",
            "purpose": "website_hero_background",
            "emotional_target": "calm_epic",
            "visual_style": "painted_environment",
            "platform": "jimeng",
            "deliverable": "jimeng_canvas_package",
            "has_visual_references": True,
        },
    )
    manifest = load_structured_manifest(project_root)

    assert manifest.constraints.video_type == "website_background"
    assert manifest.constraints.purpose == "website_hero_background"
    assert manifest.constraints.has_visual_references is True
    assert manifest.constraints.deliverable == "jimeng_canvas_package"


def test_blueprint_waits_for_confirmation_and_blocks_image_prompts(tmp_path):
    project_root = create_draft_project(
        tmp_path,
        project_id="blueprint-pending",
        title="等待蓝图确认",
        raw_input="温馨异世界早晨",
        interaction_policy=InteractionPolicy.STRICT_REVIEW,
    )
    plan_intake_questions(project_root)
    answer_intake(
        project_root,
        {
            "video_type": "animation_short",
            "purpose": "short_form_story",
            "duration_seconds": 15,
            "aspect_ratio": "16:9",
            "shot_count": 4,
            "emotional_target": "warm",
            "visual_style": "hand_drawn_fantasy",
            "platform": "jimeng",
            "deliverable": "jimeng_quick_package",
            "has_visual_references": False,
        },
    )

    blueprint_path = build_project_blueprint(project_root, _blueprint())
    manifest = load_structured_manifest(project_root)
    image_pack = PromptPackArtifact(
        project_id=manifest.project_id,
        kind=PromptKind.IMAGE,
        prompts=[StructuredPrompt(id="IMG-S01", shot_id="S01", prompt="test")],
    )

    assert blueprint_path.is_file()
    blueprint_text = blueprint_path.read_text(encoding="utf-8")
    assert "确认前不会生成 IMG-* 或 VID-*" in blueprint_text
    assert "视频类型：动画短片" in blueprint_text
    assert "已有参考素材：无" in blueprint_text
    assert manifest.approvals.concept_approval == ApprovalStatus.PENDING
    assert manifest.next_action == "await_blueprint_approval"
    with pytest.raises(StructuredProjectError, match="蓝图未确认"):
        save_structured_artifact(
            project_root,
            manifest.files.image_prompts,
            image_pack,
        )


def test_approving_blueprint_opens_images_but_not_video(tmp_path):
    project_root = create_draft_project(
        tmp_path,
        project_id="approved-blueprint",
        title="已确认蓝图",
        raw_input="温馨异世界早晨",
        interaction_policy=InteractionPolicy.STRICT_REVIEW,
    )
    plan_intake_questions(project_root)
    answer_intake(
        project_root,
        {
            "video_type": "animation_short",
            "purpose": "short_form_story",
            "duration_seconds": 15,
            "aspect_ratio": "16:9",
            "shot_count": 4,
            "emotional_target": "warm",
            "visual_style": "hand_drawn_fantasy",
            "platform": "jimeng",
            "deliverable": "jimeng_quick_package",
            "has_visual_references": False,
        },
    )
    build_project_blueprint(project_root, _blueprint())

    manifest = approve_project_blueprint(project_root)
    image_pack = PromptPackArtifact(
        project_id=manifest.project_id,
        kind=PromptKind.IMAGE,
        status=ArtifactStatus.DRAFT,
        prompts=[StructuredPrompt(id="IMG-S01", shot_id="S01", prompt="image")],
    )
    video_pack = PromptPackArtifact(
        project_id=manifest.project_id,
        kind=PromptKind.VIDEO,
        status=ArtifactStatus.DRAFT,
        prompts=[StructuredPrompt(id="VID-S01", shot_id="S01", prompt="video")],
    )

    save_structured_artifact(project_root, manifest.files.image_prompts, image_pack)
    with pytest.raises(StructuredProjectError, match="关键帧未确认"):
        save_structured_artifact(project_root, manifest.files.video_prompts, video_pack)

    manifest.approvals.keyframe_approval = ApprovalStatus.APPROVED
    save_structured_manifest(project_root, manifest)
    save_structured_artifact(project_root, manifest.files.video_prompts, video_pack)
    validate_structured_project(project_root)


def test_blueprint_revision_only_changes_concept_gate(tmp_path):
    project_root = create_draft_project(
        tmp_path,
        project_id="blueprint-revision",
        title="蓝图返修",
        raw_input="温馨异世界早晨",
        interaction_policy=InteractionPolicy.STRICT_REVIEW,
    )
    plan_intake_questions(project_root)
    answer_intake(
        project_root,
        {
            "video_type": "animation_short",
            "purpose": "short_form_story",
            "duration_seconds": 15,
            "aspect_ratio": "16:9",
            "shot_count": 4,
            "emotional_target": "warm",
            "visual_style": "hand_drawn_fantasy",
            "platform": "jimeng",
            "deliverable": "jimeng_quick_package",
            "has_visual_references": False,
        },
    )
    build_project_blueprint(project_root, _blueprint())

    manifest = request_blueprint_revision(project_root)
    concept = load_structured_artifact(project_root, manifest.files.concept)
    intake = load_structured_artifact(project_root, manifest.files.intake)

    assert manifest.approvals.concept_approval == ApprovalStatus.REVISION_REQUESTED
    assert manifest.next_action == "revise_project_blueprint"
    assert concept.status == ArtifactStatus.DRAFT
    assert intake.status == IntakeStatus.READY_FOR_BLUEPRINT
    assert json.loads(
        (project_root / "prompts/image-prompts.json").read_text(encoding="utf-8")
    )["prompts"] == []

    rebuilt = build_project_blueprint(project_root, _blueprint())
    assert rebuilt.is_file()
