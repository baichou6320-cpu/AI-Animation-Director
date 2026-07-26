from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WorkspaceModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class AttemptStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    FAILED = "failed"


class ProductionPhase(StrEnum):
    KEYFRAME = "keyframe"
    VIDEO = "video"
    PIXEL_FINISH = "pixel_finish"


class ApprovalStatus(StrEnum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    APPROVED = "approved"
    REVISION_REQUESTED = "revision_requested"
    BYPASSED = "bypassed"


class MediaKind(StrEnum):
    REFERENCE = "reference"
    KEYFRAME = "keyframe"
    VIDEO = "video"
    AUDIO = "audio"
    OTHER = "other"


class FailureTag(StrEnum):
    CHARACTER_DRIFT = "character_drift"
    STYLE_DRIFT = "style_drift"
    MOTION_ERROR = "motion_error"
    CAMERA_ERROR = "camera_error"
    DEFORMATION = "deformation"
    DURATION_MISMATCH = "duration_mismatch"
    MODERATION_BLOCKED = "moderation_blocked"
    GENERATION_TIMEOUT = "generation_timeout"
    OTHER = "other"


FAILURE_TAG_LABELS = {
    FailureTag.CHARACTER_DRIFT.value: "角色漂移",
    FailureTag.STYLE_DRIFT.value: "画风漂移",
    FailureTag.MOTION_ERROR.value: "动作错误",
    FailureTag.CAMERA_ERROR.value: "镜头运动错误",
    FailureTag.DEFORMATION.value: "画面变形",
    FailureTag.DURATION_MISMATCH.value: "时长不合适",
    FailureTag.MODERATION_BLOCKED.value: "内容审核失败",
    FailureTag.GENERATION_TIMEOUT.value: "生成超时",
    FailureTag.OTHER.value: "其他",
}


class MediaAsset(WorkspaceModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    kind: MediaKind
    path: str
    label: str = ""
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("path")
    @classmethod
    def path_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("asset path must not be empty")
        return value


class FailureRecord(WorkspaceModel):
    tag: FailureTag
    detail: str = ""
    remediation: str = ""


class PixelProfile(WorkspaceModel):
    status: ApprovalStatus = ApprovalStatus.NOT_STARTED
    base_width: int = Field(default=320, gt=0)
    base_height: int = Field(default=180, gt=0)
    delivery_width: int = Field(default=1920, gt=0)
    delivery_height: int = Field(default=1080, gt=0)
    motion_fps: int = Field(default=12, gt=0)
    delivery_fps: int = Field(default=24, gt=0)
    palette_colors: int = Field(default=48, ge=2, le=256)
    scaling: str = "nearest"
    dithering: str = "bayer"
    palette_source: str = ""

    @model_validator(mode="after")
    def pixel_scale_must_be_integer_and_uniform(self) -> "PixelProfile":
        if self.delivery_width % self.base_width:
            raise ValueError("delivery_width must be an integer multiple of base_width")
        if self.delivery_height % self.base_height:
            raise ValueError("delivery_height must be an integer multiple of base_height")
        width_scale = self.delivery_width // self.base_width
        height_scale = self.delivery_height // self.base_height
        if width_scale != height_scale:
            raise ValueError("pixel scaling must use the same integer factor on both axes")
        if self.delivery_fps % self.motion_fps:
            raise ValueError("delivery_fps must be an integer multiple of motion_fps")
        if self.scaling != "nearest":
            raise ValueError("pixel pipeline requires nearest scaling")
        return self


class AnimaticPanel(WorkspaceModel):
    shot_id: str
    image_path: str
    duration_seconds: float = Field(gt=0)
    audio_cue: str = ""


class AnimaticState(WorkspaceModel):
    status: ApprovalStatus = ApprovalStatus.NOT_STARTED
    output_path: str = ""
    temporary_audio_path: str = ""
    total_seconds: float | None = Field(default=None, gt=0)
    panels: list[AnimaticPanel] = Field(default_factory=list)


class FinalRenderState(WorkspaceModel):
    status: ApprovalStatus = ApprovalStatus.NOT_STARTED
    palette_path: str = ""
    audio_path: str = ""
    output_path: str = ""
    pixel_clips: dict[str, str] = Field(default_factory=dict)
    quality_scores: dict[str, int] = Field(default_factory=dict)
    review_note: str = ""

    @field_validator("quality_scores")
    @classmethod
    def final_scores_must_be_one_to_five(
        cls, value: dict[str, int]
    ) -> dict[str, int]:
        invalid = {name: score for name, score in value.items() if not 1 <= score <= 5}
        if invalid:
            raise ValueError(f"final quality scores must be between 1 and 5: {invalid}")
        return value


class GenerationAttempt(WorkspaceModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    shot_id: str
    attempt: int = Field(ge=1)
    phase: ProductionPhase = ProductionPhase.VIDEO
    provider: str
    model: str = ""
    prompt: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    status: AttemptStatus = AttemptStatus.PENDING
    failures: list[FailureRecord] = Field(default_factory=list)
    assets: list[MediaAsset] = Field(default_factory=list)
    notes: str = ""
    quality_scores: dict[str, int] = Field(default_factory=dict)
    decision_reason: str = ""
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("provider", "prompt")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must not be empty")
        return value

    @field_validator("quality_scores")
    @classmethod
    def quality_scores_must_be_one_to_five(
        cls, value: dict[str, int]
    ) -> dict[str, int]:
        invalid = {name: score for name, score in value.items() if not 1 <= score <= 5}
        if invalid:
            raise ValueError(f"quality scores must be between 1 and 5: {invalid}")
        return value


class Shot(WorkspaceModel):
    id: str
    order: int = Field(ge=1)
    title: str
    duration_seconds: float | None = Field(default=None, gt=0)
    image_prompt: str = ""
    video_prompt: str = ""
    negative_prompt: str = ""
    source_task_ids: list[str] = Field(default_factory=list)
    storyboard_image_path: str = ""
    audio_cue: str = ""
    attempts: list[GenerationAttempt] = Field(default_factory=list)
    selected_attempt_id: str | None = None
    selected_keyframe_attempt_id: str | None = None
    selected_video_attempt_id: str | None = None
    selected_pixel_attempt_id: str | None = None
    consistency_notes: str = ""

    @model_validator(mode="after")
    def selected_attempt_must_exist(self) -> "Shot":
        attempts_by_id = {attempt.id: attempt for attempt in self.attempts}
        selections = {
            "selected_attempt_id": (self.selected_attempt_id, None),
            "selected_keyframe_attempt_id": (
                self.selected_keyframe_attempt_id,
                ProductionPhase.KEYFRAME,
            ),
            "selected_video_attempt_id": (
                self.selected_video_attempt_id,
                ProductionPhase.VIDEO,
            ),
            "selected_pixel_attempt_id": (
                self.selected_pixel_attempt_id,
                ProductionPhase.PIXEL_FINISH,
            ),
        }
        for field_name, (attempt_id, expected_phase) in selections.items():
            if attempt_id is None:
                continue
            if attempt_id not in attempts_by_id:
                raise ValueError(
                    f"{field_name} {attempt_id!r} is not part of shot {self.id}"
                )
            if expected_phase and attempts_by_id[attempt_id].phase != expected_phase:
                raise ValueError(
                    f"{field_name} must reference a {expected_phase.value} attempt"
                )
        return self

    def selected_attempt(self) -> GenerationAttempt | None:
        selected_id = (
            self.selected_pixel_attempt_id
            or self.selected_video_attempt_id
            or self.selected_attempt_id
        )
        return next(
            (
                attempt
                for attempt in self.attempts
                if attempt.id == selected_id
            ),
            None,
        )

    def selected_attempt_for(
        self, phase: ProductionPhase | str
    ) -> GenerationAttempt | None:
        phase = ProductionPhase(phase)
        selected_id = {
            ProductionPhase.KEYFRAME: self.selected_keyframe_attempt_id,
            ProductionPhase.VIDEO: self.selected_video_attempt_id,
            ProductionPhase.PIXEL_FINISH: self.selected_pixel_attempt_id,
        }[phase]
        return next(
            (attempt for attempt in self.attempts if attempt.id == selected_id),
            None,
        )


class ProductionProject(WorkspaceModel):
    schema_version: int = 2
    id: str = Field(default_factory=lambda: uuid4().hex)
    title: str
    platform: str = ""
    aspect_ratio: str = ""
    notes: str = ""
    source_manifest: str = ""
    project_file: str = ""
    pipeline_mode: str = "legacy"
    pixel_profile: PixelProfile = Field(default_factory=PixelProfile)
    animatic_state: AnimaticState = Field(default_factory=AnimaticState)
    sample_shot_id: str | None = None
    sample_review_status: ApprovalStatus = ApprovalStatus.NOT_STARTED
    final_render: FinalRenderState = Field(default_factory=FinalRenderState)
    shots: list[Shot]
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("project title must not be empty")
        return value

    @model_validator(mode="after")
    def shot_ids_and_order_must_be_unique(self) -> "ProductionProject":
        shot_ids = [shot.id for shot in self.shots]
        orders = [shot.order for shot in self.shots]
        if len(shot_ids) != len(set(shot_ids)):
            raise ValueError("shot ids must be unique")
        if len(orders) != len(set(orders)):
            raise ValueError("shot order values must be unique")
        if self.sample_shot_id and self.sample_shot_id not in shot_ids:
            raise ValueError("sample_shot_id must reference a shot in the project")
        if self.pipeline_mode not in {"legacy", "pixel_short"}:
            raise ValueError("pipeline_mode must be legacy or pixel_short")
        return self

    def find_shot(self, shot_id: str) -> Shot:
        for shot in self.shots:
            if shot.id == shot_id:
                return shot
        raise KeyError(f"shot not found: {shot_id}")


class DeliveryItem(WorkspaceModel):
    shot_id: str
    attempt_id: str
    source_paths: list[str]
    delivered_paths: list[str]


class DeliveryReport(WorkspaceModel):
    project_id: str
    project_title: str
    status: str
    output_directory: str
    final_master: str = ""
    animatic: str = ""
    items: list[DeliveryItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)


def infer_media_kind(path: str) -> MediaKind:
    suffix = Path(path).suffix.lower()
    if suffix in {".mp4", ".mov", ".webm", ".mkv"}:
        return MediaKind.VIDEO
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return MediaKind.KEYFRAME
    if suffix in {".wav", ".mp3", ".aac", ".flac"}:
        return MediaKind.AUDIO
    return MediaKind.OTHER
