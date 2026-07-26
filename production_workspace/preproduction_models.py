from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TypeAlias

from pydantic import Field, field_validator, model_validator

from .models import ApprovalStatus, WorkspaceModel, utc_now


FieldValue: TypeAlias = str | int | float | bool | list[str] | None


class StructuredProjectStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETE = "complete"
    ARCHIVED = "archived"


class StructuredStage(StrEnum):
    INTAKE = "intake"
    BLUEPRINT_REVIEW = "blueprint_review"
    CONCEPT = "concept"
    STYLE = "style"
    ASSETS = "assets"
    SHOTS = "shots"
    IMAGE_PROMPTS = "image_prompts"
    VIDEO_PROMPTS = "video_prompts"
    PRODUCTION = "production"
    COMPLETE = "complete"


class InteractionPolicy(StrEnum):
    SINGLE_CONFIRM = "single_confirm"
    STRICT_REVIEW = "strict_review"
    DIRECT_RUN = "direct_run"


class ArtifactStatus(StrEnum):
    NOT_STARTED = "not_started"
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    INVALIDATED = "invalidated"


class IntakeStatus(StrEnum):
    AWAITING_ANSWERS = "awaiting_answers"
    READY_FOR_BLUEPRINT = "ready_for_blueprint"
    BLUEPRINT_PENDING = "blueprint_pending"
    APPROVED = "approved"


class PromptKind(StrEnum):
    IMAGE = "image"
    VIDEO = "video"


class WebBackgroundInteraction(StrEnum):
    SCROLL_SCRUB = "scroll_scrub"
    AMBIENT_LOOP = "ambient_loop"
    NORMAL_PLAYBACK = "normal_playback"


class TextSafeZone(StrEnum):
    LEFT_CENTER = "left_center"
    RIGHT_CENTER = "right_center"
    CENTER = "center"
    NONE = "none"


class ProjectConstraints(WorkspaceModel):
    core_idea: str = ""
    video_type: str = ""
    purpose: str = ""
    duration_seconds: float | None = Field(default=None, gt=0)
    aspect_ratio: str = ""
    shot_count: int | None = Field(default=None, gt=0)
    emotional_target: str = ""
    visual_style: str = ""
    platform: str = "jimeng"
    deliverable: str = "jimeng_quick_package"
    delivery_profile: str = "animation_short"
    has_visual_references: bool = False
    language: str = "zh-CN"


class StructuredApprovalState(WorkspaceModel):
    interaction_policy: InteractionPolicy = InteractionPolicy.SINGLE_CONFIRM
    qa_confirmation: ApprovalStatus = ApprovalStatus.NOT_STARTED
    concept_approval: ApprovalStatus = ApprovalStatus.NOT_STARTED
    keyframe_approval: ApprovalStatus = ApprovalStatus.NOT_STARTED
    approval_override: bool = False


class ProjectFileIndex(WorkspaceModel):
    intake: str = "input/intake.json"
    concept: str = "creative/concept.json"
    style: str = "creative/style.json"
    assets: str = "production/assets.json"
    shots: str = "production/shots.json"
    web_background: str = "production/web-background.json"
    image_prompts: str = "prompts/image-prompts.json"
    video_prompts: str = "prompts/video-prompts.json"
    execution: str = "state/execution.json"
    reviews: str = "state/reviews.json"
    blueprint: str = "deliverables/project-blueprint.md"
    quick_package: str = "deliverables/jimeng-quick-package.md"


class StructuredProjectManifest(WorkspaceModel):
    schema_version: int = 1
    state_type: str = "ai_animation_director_structured_project"
    project_id: str
    title: str
    status: StructuredProjectStatus = StructuredProjectStatus.DRAFT
    current_stage: StructuredStage = StructuredStage.INTAKE
    pipeline_mode: str = "jimeng_quick"
    constraints: ProjectConstraints = Field(default_factory=ProjectConstraints)
    approvals: StructuredApprovalState = Field(default_factory=StructuredApprovalState)
    files: ProjectFileIndex = Field(default_factory=ProjectFileIndex)
    next_action: str = "collect_intake_answers"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("project_id")
    @classmethod
    def project_id_must_be_portable(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized or any(
            character not in "abcdefghijklmnopqrstuvwxyz0123456789-"
            for character in normalized
        ):
            raise ValueError("project_id must use lowercase letters, digits, and hyphens")
        return normalized

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("title must not be empty")
        return value.strip()


class IntakeQuestionRecord(WorkspaceModel):
    id: str
    field: str
    fields: list[str] = Field(default_factory=list)
    question: str
    options: list[str] = Field(default_factory=list)
    reason: str = ""
    required: bool = False
    answer: FieldValue = None


class IntakeState(WorkspaceModel):
    schema_version: int = 1
    project_id: str
    raw_input: str
    extracted_fields: dict[str, FieldValue] = Field(default_factory=dict)
    confirmed_fields: dict[str, FieldValue] = Field(default_factory=dict)
    missing_required: list[str] = Field(default_factory=list)
    assumptions: dict[str, FieldValue] = Field(default_factory=dict)
    questions_asked: list[IntakeQuestionRecord] = Field(default_factory=list)
    qa_round: int = Field(default=0, ge=0, le=2)
    status: IntakeStatus = IntakeStatus.AWAITING_ANSWERS
    next_action: str = "ask_intake_questions"
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("raw_input")
    @classmethod
    def raw_input_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("raw_input must not be empty")
        return value.strip()


class StageHandoff(WorkspaceModel):
    decisions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    invalidates: list[str] = Field(default_factory=list)
    next_stage: StructuredStage | None = None


class WebBackgroundSpec(WorkspaceModel):
    schema_version: int = 1
    project_id: str
    status: ArtifactStatus = ArtifactStatus.NOT_STARTED
    delivery_profile: str = "website_background"
    interaction: WebBackgroundInteraction = WebBackgroundInteraction.SCROLL_SCRUB
    duration_seconds: float = Field(default=10.0, gt=0)
    text_safe_zone: TextSafeZone = TextSafeZone.LEFT_CENTER
    allowed_motion: list[str] = Field(default_factory=list)
    locked_elements: list[str] = Field(default_factory=list)
    camera_motion: str = "single_continuous_slow_push"
    audio: bool = False
    source_asset: str = ""
    desktop_asset: str = ""
    mobile_asset: str = ""
    poster_asset: str = ""
    public_release_ready: bool = False
    handoff: StageHandoff = Field(default_factory=StageHandoff)

    @field_validator("delivery_profile")
    @classmethod
    def delivery_profile_must_be_website_background(cls, value: str) -> str:
        if value != "website_background":
            raise ValueError("delivery_profile must be website_background")
        return value

    @model_validator(mode="after")
    def website_background_must_be_silent(self) -> "WebBackgroundSpec":
        if self.audio:
            raise ValueError("website background video must not contain audio")
        if self.public_release_ready and not all(
            [self.desktop_asset, self.mobile_asset, self.poster_asset]
        ):
            raise ValueError(
                "public website background requires desktop, mobile, and poster assets"
            )
        return self


class ProjectBlueprint(WorkspaceModel):
    one_sentence_understanding: str
    structured_summary: dict[str, FieldValue] = Field(default_factory=dict)
    recommended_story_direction: str
    ending_direction: str = ""
    style_direction: str
    color_lighting_direction: str = ""
    camera_direction: str
    assumptions: list[str] = Field(default_factory=list)
    editable_fields: list[str] = Field(default_factory=list)
    next_stage_description: str = "确认后进入风格设计、资产设计和镜头规划。"

    @field_validator(
        "one_sentence_understanding",
        "recommended_story_direction",
        "style_direction",
        "camera_direction",
    )
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("blueprint required text must not be empty")
        return value.strip()


class ConceptArtifact(WorkspaceModel):
    schema_version: int = 1
    project_id: str
    status: ArtifactStatus = ArtifactStatus.NOT_STARTED
    logline: str = ""
    theme: str = ""
    story_direction: str = ""
    ending_direction: str = ""
    visual_direction: str = ""
    director_rules: list[str] = Field(default_factory=list)
    blueprint: ProjectBlueprint | None = None
    handoff: StageHandoff = Field(default_factory=StageHandoff)


class StyleArtifact(WorkspaceModel):
    schema_version: int = 1
    project_id: str
    status: ArtifactStatus = ArtifactStatus.NOT_STARTED
    source_references: list[str] = Field(default_factory=list)
    palette: list[str] = Field(default_factory=list)
    lighting: list[str] = Field(default_factory=list)
    spatial_layers: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    composition: list[str] = Field(default_factory=list)
    density: str = ""
    prompt_anchors: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    handoff: StageHandoff = Field(default_factory=StageHandoff)


class AssetRecord(WorkspaceModel):
    id: str
    kind: str
    name: str
    status: ArtifactStatus = ArtifactStatus.DRAFT
    prompt_anchor: str = ""
    source_reference: str = ""
    consistency_rules: list[str] = Field(default_factory=list)


class AssetLibraryArtifact(WorkspaceModel):
    schema_version: int = 1
    project_id: str
    status: ArtifactStatus = ArtifactStatus.NOT_STARTED
    assets: list[AssetRecord] = Field(default_factory=list)
    handoff: StageHandoff = Field(default_factory=StageHandoff)

    @model_validator(mode="after")
    def asset_ids_must_be_unique(self) -> "AssetLibraryArtifact":
        identifiers = [asset.id for asset in self.assets]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("asset ids must be unique")
        return self


class StructuredShot(WorkspaceModel):
    id: str
    order: int = Field(ge=1)
    title: str
    duration_seconds: float | None = Field(default=None, gt=0)
    purpose: str = ""
    framing: str = ""
    camera: str = ""
    subject_action: str = ""
    environment_motion: str = ""
    asset_ids: list[str] = Field(default_factory=list)
    continuity: list[str] = Field(default_factory=list)
    difficulty: str = "medium"


class ShotPlanArtifact(WorkspaceModel):
    schema_version: int = 1
    project_id: str
    status: ArtifactStatus = ArtifactStatus.NOT_STARTED
    shots: list[StructuredShot] = Field(default_factory=list)
    handoff: StageHandoff = Field(default_factory=StageHandoff)

    @model_validator(mode="after")
    def shot_ids_and_orders_must_be_unique(self) -> "ShotPlanArtifact":
        identifiers = [shot.id for shot in self.shots]
        orders = [shot.order for shot in self.shots]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("shot ids must be unique")
        if len(orders) != len(set(orders)):
            raise ValueError("shot order values must be unique")
        return self


class StructuredPrompt(WorkspaceModel):
    id: str
    shot_id: str | None = None
    asset_ids: list[str] = Field(default_factory=list)
    prompt: str = ""
    negative_prompt: str = ""
    checkpoints: list[str] = Field(default_factory=list)
    fallback: str = ""
    status: ArtifactStatus = ArtifactStatus.DRAFT


class PromptPackArtifact(WorkspaceModel):
    schema_version: int = 1
    project_id: str
    kind: PromptKind
    status: ArtifactStatus = ArtifactStatus.NOT_STARTED
    prompts: list[StructuredPrompt] = Field(default_factory=list)
    handoff: StageHandoff = Field(default_factory=StageHandoff)

    @model_validator(mode="after")
    def prompt_ids_must_be_unique(self) -> "PromptPackArtifact":
        identifiers = [prompt.id for prompt in self.prompts]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("prompt ids must be unique")
        return self


class StructuredFailure(WorkspaceModel):
    step_id: str
    failure_type: str
    symptom: str = ""
    retry_count: int = Field(default=0, ge=0)
    resolved: bool = False


class StructuredExecutionState(WorkspaceModel):
    schema_version: int = 1
    project_id: str
    current_step: str = "intake"
    completed_ids: list[str] = Field(default_factory=list)
    invalidated_ids: list[str] = Field(default_factory=list)
    failures: list[StructuredFailure] = Field(default_factory=list)
    next_action: str = "collect_intake_answers"
    updated_at: datetime = Field(default_factory=utc_now)


class StageReview(WorkspaceModel):
    stage: StructuredStage
    status: ApprovalStatus = ApprovalStatus.NOT_STARTED
    score: float | None = Field(default=None, ge=0, le=10)
    findings: list[str] = Field(default_factory=list)
    reviewed_at: datetime | None = None


class StructuredReviewState(WorkspaceModel):
    schema_version: int = 1
    project_id: str
    reviews: list[StageReview] = Field(default_factory=list)
