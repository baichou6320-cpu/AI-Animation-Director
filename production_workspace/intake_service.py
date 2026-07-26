from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from .models import ApprovalStatus, utc_now
from .preproduction_models import (
    ArtifactStatus,
    ConceptArtifact,
    FieldValue,
    InteractionPolicy,
    IntakeQuestionRecord,
    IntakeState,
    IntakeStatus,
    ProjectBlueprint,
    ProjectConstraints,
    StructuredProjectManifest,
    StructuredStage,
)
from .preproduction_storage import (
    StructuredProjectError,
    load_structured_artifact,
    load_structured_manifest,
    save_structured_artifact,
    save_structured_manifest,
)


@dataclass(frozen=True)
class QuestionSpec:
    id: str
    fields: tuple[str, ...]
    question: str
    options: tuple[str, ...]
    reason: str
    priority: int


QUESTION_SPECS = (
    QuestionSpec(
        id="creative_direction",
        fields=("emotional_target", "visual_style"),
        question="你希望观众获得什么情绪，以及画面更接近哪种视觉方向？",
        options=(
            "治愈 + 温暖手绘",
            "热血 + 电影感科幻",
            "轻松 + 像素游戏",
            "悬疑 + 写实暗调",
            "上传参考图",
        ),
        reason="情绪和视觉方向决定美术、光影与镜头语言。",
        priority=10,
    ),
    QuestionSpec(
        id="format_scope",
        fields=("duration_seconds", "aspect_ratio", "shot_count"),
        question="成片需要多长、什么画幅、多少个镜头？",
        options=(
            "10 秒 / 9:16 / 3 镜",
            "15 秒 / 16:9 / 4 镜",
            "30 秒 / 16:9 / 6 镜",
            "自定义",
        ),
        reason="时长和镜头规模直接决定故事节拍与生成成本。",
        priority=20,
    ),
    QuestionSpec(
        id="project_goal",
        fields=("video_type", "purpose"),
        question="这条视频属于什么类型，主要准备拿来做什么？",
        options=("动画短片", "广告", "MV", "角色测试", "世界观预告"),
        reason="用途决定叙事结构、信息密度和结尾方式。",
        priority=30,
    ),
    QuestionSpec(
        id="platform_delivery",
        fields=("platform", "deliverable"),
        question="你准备在哪个平台制作，需要画布执行包还是只要提示词？",
        options=("即梦画布", "即梦提示词", "通用平台", "暂未确定"),
        reason="平台和交付方式决定后续提示词与操作结构。",
        priority=40,
    ),
    QuestionSpec(
        id="visual_references",
        fields=("has_visual_references",),
        question="你现在是否有参考图、角色图或场景素材？",
        options=("有，稍后上传", "没有，需要从零生成"),
        reason="已有素材应优先复用，避免重复生成和角色漂移。",
        priority=50,
    ),
)


INTAKE_DEFAULTS: dict[str, FieldValue] = {
    "video_type": "animation_short",
    "purpose": "short_form_story",
    "duration_seconds": 15,
    "aspect_ratio": "16:9",
    "shot_count": 4,
    "emotional_target": "warm",
    "visual_style": "cinematic_animation",
    "platform": "jimeng",
    "deliverable": "jimeng_quick_package",
    "has_visual_references": False,
}


REQUIRED_INTAKE_FIELDS = (
    "core_idea",
    "video_type",
    "purpose",
    "duration_seconds",
    "aspect_ratio",
    "shot_count",
    "emotional_target",
    "visual_style",
    "platform",
    "deliverable",
    "has_visual_references",
)


BLUEPRINT_FIELD_LABELS = {
    "core_idea": "核心主题",
    "video_type": "视频类型",
    "purpose": "主要用途",
    "duration_seconds": "片长（秒）",
    "aspect_ratio": "画幅",
    "shot_count": "镜头数",
    "emotional_target": "情绪目标",
    "visual_style": "视觉方向",
    "platform": "制作平台",
    "deliverable": "交付方式",
    "has_visual_references": "已有参考素材",
    "language": "语言",
}


BLUEPRINT_VALUE_LABELS = {
    "animation_short": "动画短片",
    "short_form_story": "短篇叙事",
    "jimeng_quick_package": "即梦轻量执行包",
    "jimeng_canvas_package": "即梦画布执行包",
    "zh-CN": "中文",
}


def _has_value(value: FieldValue) -> bool:
    return value is not None and value != "" and value != []


def _known_values(
    intake: IntakeState,
    manifest: StructuredProjectManifest,
) -> dict[str, FieldValue]:
    known: dict[str, FieldValue] = {
        "core_idea": intake.raw_input,
    }
    constraint_defaults = ProjectConstraints().model_dump(mode="python")
    for key, value in manifest.constraints.model_dump(mode="python").items():
        if _has_value(value) and value != constraint_defaults.get(key):
            known[key] = value
    for source in (
        intake.extracted_fields,
        intake.assumptions,
        intake.confirmed_fields,
    ):
        for key, value in source.items():
            if _has_value(value):
                known[key] = value
    return known


def _missing_fields(known: dict[str, FieldValue]) -> list[str]:
    return [field for field in REQUIRED_INTAKE_FIELDS if not _has_value(known.get(field))]


def _sync_constraints(
    manifest: StructuredProjectManifest,
    known: dict[str, FieldValue],
) -> None:
    payload = manifest.constraints.model_dump(mode="python")
    for field in ProjectConstraints.model_fields:
        if field in known and _has_value(known[field]):
            payload[field] = known[field]
    try:
        manifest.constraints = ProjectConstraints.model_validate(payload)
    except ValidationError as exc:
        raise StructuredProjectError(f"Intake 回答不符合项目约束：{exc}") from exc
    manifest.updated_at = utc_now()


def _apply_defaults(
    intake: IntakeState,
    manifest: StructuredProjectManifest,
) -> None:
    known = _known_values(intake, manifest)
    for field in _missing_fields(known):
        if field == "core_idea":
            continue
        default = INTAKE_DEFAULTS[field]
        intake.assumptions[field] = default
        known[field] = default
    intake.missing_required = _missing_fields(known)
    if intake.missing_required:
        intake.status = IntakeStatus.AWAITING_ANSWERS
        intake.next_action = "clarify_core_idea"
    else:
        intake.status = IntakeStatus.READY_FOR_BLUEPRINT
        intake.next_action = "build_project_blueprint"
    intake.updated_at = utc_now()
    _sync_constraints(manifest, known)


def plan_intake_questions(
    project_root: str | Path,
    *,
    limit: int = 3,
) -> list[IntakeQuestionRecord]:
    if not 1 <= limit <= 3:
        raise StructuredProjectError("每轮 Intake 只能提出 1-3 个问题")
    manifest = load_structured_manifest(project_root)
    intake = load_structured_artifact(project_root, manifest.files.intake)
    if not isinstance(intake, IntakeState):
        raise StructuredProjectError("input/intake.json 类型错误")
    if intake.status in {IntakeStatus.READY_FOR_BLUEPRINT, IntakeStatus.BLUEPRINT_PENDING}:
        return []

    policy = manifest.approvals.interaction_policy
    if policy == InteractionPolicy.DIRECT_RUN:
        manifest.approvals.qa_confirmation = ApprovalStatus.BYPASSED
        manifest.approvals.approval_override = True
        _apply_defaults(intake, manifest)
        save_structured_artifact(project_root, manifest.files.intake, intake)
        save_structured_manifest(project_root, manifest)
        return []

    pending = [question for question in intake.questions_asked if question.answer is None]
    if pending:
        return pending
    max_rounds = (
        2
        if manifest.approvals.interaction_policy == InteractionPolicy.STRICT_REVIEW
        else 1
    )
    if intake.qa_round >= max_rounds:
        _apply_defaults(intake, manifest)
        save_structured_artifact(project_root, manifest.files.intake, intake)
        save_structured_manifest(project_root, manifest)
        return []

    known = _known_values(intake, manifest)
    missing = set(_missing_fields(known))
    asked_ids = {question.id for question in intake.questions_asked}
    candidates = [
        spec
        for spec in QUESTION_SPECS
        if spec.id not in asked_ids and any(field in missing for field in spec.fields)
    ]
    candidates.sort(key=lambda item: item.priority)
    selected = candidates[:limit]
    if not selected:
        if policy == InteractionPolicy.SINGLE_CONFIRM:
            manifest.approvals.qa_confirmation = ApprovalStatus.APPROVED
        _apply_defaults(intake, manifest)
        save_structured_artifact(project_root, manifest.files.intake, intake)
        save_structured_manifest(project_root, manifest)
        return []

    intake.qa_round += 1
    questions = [
        IntakeQuestionRecord(
            id=spec.id,
            field=spec.fields[0],
            fields=list(spec.fields),
            question=spec.question,
            options=list(spec.options),
            reason=spec.reason,
            required=True,
        )
        for spec in selected
    ]
    intake.questions_asked.extend(questions)
    intake.missing_required = sorted(missing)
    intake.status = IntakeStatus.AWAITING_ANSWERS
    intake.next_action = "collect_intake_answers"
    intake.updated_at = utc_now()
    save_structured_artifact(project_root, manifest.files.intake, intake)
    return questions


def answer_intake(
    project_root: str | Path,
    answers: dict[str, FieldValue],
) -> IntakeState:
    manifest = load_structured_manifest(project_root)
    intake = load_structured_artifact(project_root, manifest.files.intake)
    if not isinstance(intake, IntakeState):
        raise StructuredProjectError("input/intake.json 类型错误")
    if not answers:
        raise StructuredProjectError("至少需要一个有效回答")

    allowed = set(REQUIRED_INTAKE_FIELDS) | {"delivery_profile"}
    unknown = sorted(set(answers) - allowed)
    if unknown:
        raise StructuredProjectError(f"未知 Intake 字段：{unknown}")
    for field, value in answers.items():
        if _has_value(value):
            intake.confirmed_fields[field] = value
    answered_fields = set(answers)
    pending_questions = [
        question for question in intake.questions_asked if question.answer is None
    ]
    for question in pending_questions:
        if answered_fields.intersection(question.fields):
            question.answer = "; ".join(
                f"{field}={answers[field]}"
                for field in question.fields
                if field in answers and _has_value(answers[field])
            )
        else:
            question.answer = "__skipped__"

    known = _known_values(intake, manifest)
    intake.missing_required = _missing_fields(known)
    _sync_constraints(manifest, known)
    policy = manifest.approvals.interaction_policy
    if policy == InteractionPolicy.SINGLE_CONFIRM:
        manifest.approvals.qa_confirmation = ApprovalStatus.APPROVED
        _apply_defaults(intake, manifest)
    elif policy == InteractionPolicy.DIRECT_RUN:
        manifest.approvals.qa_confirmation = ApprovalStatus.BYPASSED
        manifest.approvals.approval_override = True
        _apply_defaults(intake, manifest)
    elif not intake.missing_required:
        manifest.approvals.qa_confirmation = ApprovalStatus.APPROVED
        intake.status = IntakeStatus.READY_FOR_BLUEPRINT
        intake.next_action = "build_project_blueprint"
    elif intake.qa_round >= 2:
        _apply_defaults(intake, manifest)
    else:
        intake.status = IntakeStatus.AWAITING_ANSWERS
        intake.next_action = "plan_next_intake_questions"
        intake.updated_at = utc_now()

    save_structured_artifact(project_root, manifest.files.intake, intake)
    save_structured_manifest(project_root, manifest)
    return intake


def finalize_intake_with_defaults(project_root: str | Path) -> IntakeState:
    manifest = load_structured_manifest(project_root)
    intake = load_structured_artifact(project_root, manifest.files.intake)
    if not isinstance(intake, IntakeState):
        raise StructuredProjectError("input/intake.json 类型错误")
    if manifest.approvals.interaction_policy == InteractionPolicy.DIRECT_RUN:
        manifest.approvals.qa_confirmation = ApprovalStatus.BYPASSED
        manifest.approvals.approval_override = True
    elif manifest.approvals.interaction_policy == InteractionPolicy.SINGLE_CONFIRM:
        manifest.approvals.qa_confirmation = ApprovalStatus.APPROVED
    _apply_defaults(intake, manifest)
    save_structured_artifact(project_root, manifest.files.intake, intake)
    save_structured_manifest(project_root, manifest)
    return intake


def _render_blueprint(manifest: StructuredProjectManifest, blueprint: ProjectBlueprint) -> str:
    summary_lines = [
        f"- {BLUEPRINT_FIELD_LABELS.get(key, key)}：{_display_blueprint_value(value)}"
        for key, value in blueprint.structured_summary.items()
        if _has_value(value)
    ]
    assumption_lines = [
        f"- {_display_assumption(item)}" for item in blueprint.assumptions
    ] or ["- 无"]
    editable_lines = [f"- {item}" for item in blueprint.editable_fields] or ["- 暂无"]
    if manifest.approvals.interaction_policy == InteractionPolicy.STRICT_REVIEW:
        continuation = (
            "回复 `确认蓝图` 后进入正式生产；确认前不会生成 IMG-* 或 VID-*。"
        )
    else:
        continuation = (
            "本蓝图已由本轮 QA 确认，系统将继续生成镜头、图片提示词和视频提示词；"
            "你仍可随时要求局部修改。"
        )
    return "\n".join(
        [
            f"# 项目蓝图：{manifest.title}",
            "",
            "## 一句话理解",
            blueprint.one_sentence_understanding,
            "",
            "## 结构化需求",
            *summary_lines,
            "",
            "## 推荐故事方向",
            blueprint.recommended_story_direction,
            "",
            "## 结尾方向",
            blueprint.ending_direction or "待创作阶段细化。",
            "",
            "## 视觉与镜头方向",
            f"- 风格：{blueprint.style_direction}",
            f"- 色彩与光影：{blueprint.color_lighting_direction or '待风格阶段细化。'}",
            f"- 镜头：{blueprint.camera_direction}",
            "",
            "## 默认假设",
            *assumption_lines,
            "",
            "## 仍可修改",
            *editable_lines,
            "",
            "## 确认后开始",
            blueprint.next_stage_description,
            "",
            continuation,
            "",
        ]
    )


def _display_blueprint_value(value: FieldValue) -> str:
    if isinstance(value, bool):
        return "有" if value else "无"
    if isinstance(value, list):
        return "、".join(value)
    return BLUEPRINT_VALUE_LABELS.get(str(value), str(value))


def _display_assumption(item: str) -> str:
    key, separator, value = item.partition("=")
    if not separator:
        return item
    return (
        f"{BLUEPRINT_FIELD_LABELS.get(key, key)}采用默认值："
        f"{BLUEPRINT_VALUE_LABELS.get(value, value)}"
    )


def build_project_blueprint(
    project_root: str | Path,
    blueprint: ProjectBlueprint,
) -> Path:
    manifest = load_structured_manifest(project_root)
    intake = load_structured_artifact(project_root, manifest.files.intake)
    concept = load_structured_artifact(project_root, manifest.files.concept)
    if not isinstance(intake, IntakeState) or not isinstance(concept, ConceptArtifact):
        raise StructuredProjectError("Intake 或 Concept 阶段文件类型错误")
    if intake.status != IntakeStatus.READY_FOR_BLUEPRINT:
        raise StructuredProjectError("Intake 尚未完成，不能生成项目蓝图")

    policy = manifest.approvals.interaction_policy
    auto_advance = policy != InteractionPolicy.STRICT_REVIEW
    concept.status = ArtifactStatus.APPROVED if auto_advance else ArtifactStatus.PENDING_REVIEW
    concept.logline = blueprint.one_sentence_understanding
    concept.story_direction = blueprint.recommended_story_direction
    concept.ending_direction = blueprint.ending_direction
    concept.visual_direction = blueprint.style_direction
    concept.blueprint = blueprint
    intake.status = IntakeStatus.APPROVED if auto_advance else IntakeStatus.BLUEPRINT_PENDING
    intake.next_action = "build_style_artifact" if auto_advance else "await_blueprint_approval"
    intake.updated_at = utc_now()
    if auto_advance:
        direct_run = policy == InteractionPolicy.DIRECT_RUN
        manifest.current_stage = StructuredStage.STYLE
        manifest.status = "active"
        manifest.approvals.concept_approval = (
            ApprovalStatus.BYPASSED if direct_run else ApprovalStatus.APPROVED
        )
        manifest.approvals.keyframe_approval = ApprovalStatus.BYPASSED
        manifest.approvals.approval_override = direct_run
        manifest.next_action = "build_style_artifact"
    else:
        manifest.current_stage = StructuredStage.BLUEPRINT_REVIEW
        manifest.approvals.concept_approval = ApprovalStatus.PENDING
        manifest.next_action = "await_blueprint_approval"
    manifest.updated_at = utc_now()

    output = Path(project_root) / manifest.files.blueprint
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(
        _render_blueprint(manifest, blueprint),
        encoding="utf-8",
        newline="\n",
    )
    save_structured_artifact(project_root, manifest.files.concept, concept)
    save_structured_artifact(project_root, manifest.files.intake, intake)
    save_structured_manifest(project_root, manifest)
    temporary.replace(output)
    return output


def approve_project_blueprint(
    project_root: str | Path,
    *,
    bypass: bool = False,
) -> StructuredProjectManifest:
    manifest = load_structured_manifest(project_root)
    intake = load_structured_artifact(project_root, manifest.files.intake)
    concept = load_structured_artifact(project_root, manifest.files.concept)
    if not isinstance(intake, IntakeState) or not isinstance(concept, ConceptArtifact):
        raise StructuredProjectError("Intake 或 Concept 阶段文件类型错误")
    if concept.blueprint is None or concept.status != ArtifactStatus.PENDING_REVIEW:
        raise StructuredProjectError("没有等待确认的项目蓝图")

    approval = ApprovalStatus.BYPASSED if bypass else ApprovalStatus.APPROVED
    concept.status = ArtifactStatus.APPROVED
    intake.status = IntakeStatus.APPROVED
    intake.next_action = "build_style_artifact"
    intake.updated_at = utc_now()
    manifest.approvals.concept_approval = approval
    manifest.approvals.approval_override = bypass
    manifest.current_stage = StructuredStage.STYLE
    manifest.status = "active"
    manifest.next_action = "build_style_artifact"
    manifest.updated_at = utc_now()

    save_structured_artifact(project_root, manifest.files.concept, concept)
    save_structured_artifact(project_root, manifest.files.intake, intake)
    save_structured_manifest(project_root, manifest)
    return manifest


def request_blueprint_revision(project_root: str | Path) -> StructuredProjectManifest:
    manifest = load_structured_manifest(project_root)
    intake = load_structured_artifact(project_root, manifest.files.intake)
    concept = load_structured_artifact(project_root, manifest.files.concept)
    if (
        not isinstance(intake, IntakeState)
        or not isinstance(concept, ConceptArtifact)
        or concept.blueprint is None
    ):
        raise StructuredProjectError("没有可以返修的项目蓝图")
    concept.status = ArtifactStatus.DRAFT
    intake.status = IntakeStatus.READY_FOR_BLUEPRINT
    intake.next_action = "revise_project_blueprint"
    intake.updated_at = utc_now()
    manifest.approvals.concept_approval = ApprovalStatus.REVISION_REQUESTED
    manifest.current_stage = StructuredStage.BLUEPRINT_REVIEW
    manifest.next_action = "revise_project_blueprint"
    manifest.updated_at = utc_now()
    save_structured_artifact(project_root, manifest.files.concept, concept)
    save_structured_artifact(project_root, manifest.files.intake, intake)
    save_structured_manifest(project_root, manifest)
    return manifest
