from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import TypeVar
from uuid import uuid4

from pydantic import BaseModel, ValidationError

from .preproduction_models import (
    AssetLibraryArtifact,
    ConceptArtifact,
    InteractionPolicy,
    IntakeState,
    ProjectConstraints,
    PromptKind,
    PromptPackArtifact,
    ShotPlanArtifact,
    StructuredExecutionState,
    StructuredApprovalState,
    StructuredProjectManifest,
    StructuredReviewState,
    StyleArtifact,
    WebBackgroundSpec,
)
from .models import ApprovalStatus


class StructuredProjectError(Exception):
    """Raised when a structured pre-production project is invalid or unsafe."""


ModelT = TypeVar("ModelT", bound=BaseModel)


ARTIFACT_MODELS: dict[str, type[BaseModel]] = {
    "input/intake.json": IntakeState,
    "creative/concept.json": ConceptArtifact,
    "creative/style.json": StyleArtifact,
    "production/assets.json": AssetLibraryArtifact,
    "production/shots.json": ShotPlanArtifact,
    "production/web-background.json": WebBackgroundSpec,
    "prompts/image-prompts.json": PromptPackArtifact,
    "prompts/video-prompts.json": PromptPackArtifact,
    "state/execution.json": StructuredExecutionState,
    "state/reviews.json": StructuredReviewState,
}


SCHEMA_MODELS: dict[str, type[BaseModel]] = {
    "project.schema.json": StructuredProjectManifest,
    "intake.schema.json": IntakeState,
    "concept.schema.json": ConceptArtifact,
    "style.schema.json": StyleArtifact,
    "assets.schema.json": AssetLibraryArtifact,
    "shots.schema.json": ShotPlanArtifact,
    "web-background.schema.json": WebBackgroundSpec,
    "prompt-pack.schema.json": PromptPackArtifact,
    "execution.schema.json": StructuredExecutionState,
    "reviews.schema.json": StructuredReviewState,
}


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _load_model(path: Path, model: type[ModelT]) -> ModelT:
    try:
        return model.model_validate_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StructuredProjectError(f"缺少结构化项目文件：{path}") from exc
    except (OSError, ValidationError, ValueError) as exc:
        raise StructuredProjectError(f"结构化项目文件无效：{path}: {exc}") from exc


def _initial_artifacts(project_id: str) -> dict[str, BaseModel]:
    return {
        "input/intake.json": IntakeState(
            project_id=project_id,
            raw_input="placeholder",
        ),
        "creative/concept.json": ConceptArtifact(project_id=project_id),
        "creative/style.json": StyleArtifact(project_id=project_id),
        "production/assets.json": AssetLibraryArtifact(project_id=project_id),
        "production/shots.json": ShotPlanArtifact(project_id=project_id),
        "production/web-background.json": WebBackgroundSpec(project_id=project_id),
        "prompts/image-prompts.json": PromptPackArtifact(
            project_id=project_id,
            kind=PromptKind.IMAGE,
        ),
        "prompts/video-prompts.json": PromptPackArtifact(
            project_id=project_id,
            kind=PromptKind.VIDEO,
        ),
        "state/execution.json": StructuredExecutionState(project_id=project_id),
        "state/reviews.json": StructuredReviewState(project_id=project_id),
    }


def create_draft_project(
    projects_root: str | Path,
    *,
    title: str,
    raw_input: str,
    project_id: str | None = None,
    extracted_fields: dict | None = None,
    constraints: ProjectConstraints | None = None,
    interaction_policy: InteractionPolicy = InteractionPolicy.SINGLE_CONFIRM,
) -> Path:
    identifier = project_id or f"project-{uuid4().hex[:10]}"
    manifest = StructuredProjectManifest(
        project_id=identifier,
        title=title,
        constraints=constraints or ProjectConstraints(),
        approvals=StructuredApprovalState(interaction_policy=interaction_policy),
    )
    intake = IntakeState(
        project_id=identifier,
        raw_input=raw_input,
        extracted_fields=extracted_fields or {},
    )

    root = Path(projects_root).resolve()
    destination = root / identifier
    staging = root / f".{identifier}.tmp"
    if destination.exists():
        raise StructuredProjectError(f"项目目录已存在：{destination}")
    if staging.exists():
        shutil.rmtree(staging)

    artifacts = _initial_artifacts(identifier)
    artifacts["input/intake.json"] = intake
    try:
        staging.mkdir(parents=True)
        _write_json(staging / "project.json", manifest.model_dump(mode="json"))
        for relative_path, artifact in artifacts.items():
            _write_json(staging / relative_path, artifact.model_dump(mode="json"))
        (staging / "deliverables").mkdir(exist_ok=True)
        validate_structured_project(staging)
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staging, destination)
    except (OSError, ValidationError, ValueError, StructuredProjectError) as exc:
        shutil.rmtree(staging, ignore_errors=True)
        if isinstance(exc, StructuredProjectError):
            raise
        raise StructuredProjectError(f"创建项目草稿失败：{exc}") from exc
    return destination


def load_structured_manifest(project_root: str | Path) -> StructuredProjectManifest:
    return _load_model(Path(project_root) / "project.json", StructuredProjectManifest)


def save_structured_manifest(
    project_root: str | Path,
    manifest: StructuredProjectManifest,
) -> Path:
    root = Path(project_root)
    destination = root / "project.json"
    temporary = root / "project.json.tmp"
    backup = root / "project.json.bak"
    validated = StructuredProjectManifest.model_validate(
        manifest.model_dump(mode="json")
    )
    try:
        _write_json(temporary, validated.model_dump(mode="json"))
        StructuredProjectManifest.model_validate_json(
            temporary.read_text(encoding="utf-8")
        )
        if destination.exists():
            shutil.copy2(destination, backup)
        os.replace(temporary, destination)
    except (OSError, ValidationError, ValueError) as exc:
        temporary.unlink(missing_ok=True)
        raise StructuredProjectError(
            f"保存 project.json 失败，原文件已保留：{exc}"
        ) from exc
    return destination


def load_structured_artifact(
    project_root: str | Path,
    relative_path: str,
) -> BaseModel:
    model = ARTIFACT_MODELS.get(relative_path)
    if model is None:
        raise StructuredProjectError(f"未知阶段文件：{relative_path}")
    return _load_model(Path(project_root) / relative_path, model)


def validate_structured_project(
    project_root: str | Path,
) -> StructuredProjectManifest:
    root = Path(project_root)
    manifest = load_structured_manifest(root)
    indexed_paths = {
        manifest.files.intake,
        manifest.files.concept,
        manifest.files.style,
        manifest.files.assets,
        manifest.files.shots,
        manifest.files.web_background,
        manifest.files.image_prompts,
        manifest.files.video_prompts,
        manifest.files.execution,
        manifest.files.reviews,
    }
    if indexed_paths != set(ARTIFACT_MODELS):
        missing = sorted(set(ARTIFACT_MODELS) - indexed_paths)
        unknown = sorted(indexed_paths - set(ARTIFACT_MODELS))
        raise StructuredProjectError(
            f"project.json 文件索引不一致；缺少={missing}，未知={unknown}"
        )
    for relative_path in sorted(indexed_paths):
        artifact = load_structured_artifact(root, relative_path)
        if getattr(artifact, "project_id", None) != manifest.project_id:
            raise StructuredProjectError(
                f"{relative_path} 的 project_id 与 project.json 不一致"
            )
        if relative_path == manifest.files.image_prompts:
            if artifact.kind != PromptKind.IMAGE:
                raise StructuredProjectError("image-prompts.json 的 kind 必须是 image")
            if artifact.prompts and manifest.approvals.concept_approval not in {
                ApprovalStatus.APPROVED,
                ApprovalStatus.BYPASSED,
            }:
                raise StructuredProjectError(
                    "项目蓝图未确认，不得保存 IMG-* 提示词"
                )
        if relative_path == manifest.files.video_prompts:
            if artifact.kind != PromptKind.VIDEO:
                raise StructuredProjectError("video-prompts.json 的 kind 必须是 video")
            if artifact.prompts and manifest.approvals.keyframe_approval not in {
                ApprovalStatus.APPROVED,
                ApprovalStatus.BYPASSED,
            }:
                raise StructuredProjectError(
                    "关键帧未确认，不得保存 VID-* 提示词"
                )
    return manifest


def save_structured_artifact(
    project_root: str | Path,
    relative_path: str,
    artifact: BaseModel,
) -> Path:
    root = Path(project_root)
    manifest = load_structured_manifest(root)
    model = ARTIFACT_MODELS.get(relative_path)
    if model is None:
        raise StructuredProjectError(f"未知阶段文件：{relative_path}")
    validated = model.model_validate(artifact.model_dump(mode="json"))
    if getattr(validated, "project_id", None) != manifest.project_id:
        raise StructuredProjectError("阶段文件 project_id 与 project.json 不一致")
    if relative_path == manifest.files.image_prompts:
        if validated.prompts and manifest.approvals.concept_approval not in {
            ApprovalStatus.APPROVED,
            ApprovalStatus.BYPASSED,
        }:
            raise StructuredProjectError("项目蓝图未确认，不得保存 IMG-* 提示词")
    if relative_path == manifest.files.video_prompts:
        if validated.prompts and manifest.approvals.keyframe_approval not in {
            ApprovalStatus.APPROVED,
            ApprovalStatus.BYPASSED,
        }:
            raise StructuredProjectError("关键帧未确认，不得保存 VID-* 提示词")

    destination = root / relative_path
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    backup = destination.with_suffix(destination.suffix + ".bak")
    try:
        _write_json(temporary, validated.model_dump(mode="json"))
        model.model_validate_json(temporary.read_text(encoding="utf-8"))
        if destination.exists():
            shutil.copy2(destination, backup)
        os.replace(temporary, destination)
    except (OSError, ValidationError, ValueError) as exc:
        temporary.unlink(missing_ok=True)
        raise StructuredProjectError(f"保存阶段文件失败，原文件已保留：{exc}") from exc
    return destination


def write_json_schemas(output_directory: str | Path) -> list[Path]:
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename, model in SCHEMA_MODELS.items():
        path = output / filename
        _write_json(path, model.model_json_schema())
        written.append(path)
    return written
