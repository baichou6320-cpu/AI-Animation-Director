from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .models import PixelProfile, ProductionProject, Shot


class ManifestImportError(Exception):
    """Raised when an Animation Director manifest cannot be imported."""


VIDEO_TYPES = {"video_text", "video_image", "video_first_last_frame"}


def _shot_key(task_id: str) -> str | None:
    normalized = task_id.lower().replace("-", "_")
    match = re.search(r"(?:shot|s)[_\s-]?(\d+)", normalized)
    if match:
        return f"S{int(match.group(1)):02d}"
    match = re.search(r"(\d+)$", normalized)
    if match:
        return f"S{int(match.group(1)):02d}"
    return None


def _duration_seconds(value: Any) -> float | None:
    if isinstance(value, (int, float)) and value > 0:
        return float(value)
    if isinstance(value, str):
        match = re.search(r"(\d+(?:\.\d+)?)", value)
        if match:
            return float(match.group(1))
    return None


def load_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestImportError(f"manifest 不存在：{manifest_path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestImportError(f"manifest 无法读取：{exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        raise ManifestImportError("manifest 必须包含 tasks 数组")
    return data


def import_manifest(path: str | Path) -> ProductionProject:
    manifest_path = Path(path).resolve()
    manifest = load_manifest(manifest_path)
    project_info = manifest.get("project") or {}
    if not isinstance(project_info, dict):
        project_info = {}

    grouped: dict[str, dict[str, Any]] = {}
    for task in manifest["tasks"]:
        if not isinstance(task, dict):
            continue
        task_id = str(task.get("id", "")).strip()
        task_type = task.get("type")
        if not task_id or task_type not in {"image", *VIDEO_TYPES}:
            continue
        key = _shot_key(task_id)
        if key is None:
            continue
        bucket = grouped.setdefault(
            key,
            {
                "image": None,
                "video": None,
                "task_ids": [],
            },
        )
        bucket["task_ids"].append(task_id)
        if task_type == "image":
            bucket["image"] = task
        else:
            bucket["video"] = task

    if not grouped:
        raise ManifestImportError(
            "没有找到可识别的镜头任务；任务 id 应包含 shot_001、S01 等镜头编号"
        )

    shots: list[Shot] = []
    for order, key in enumerate(
        sorted(grouped, key=lambda item: int(re.search(r"\d+", item).group())),
        start=1,
    ):
        group = grouped[key]
        image = group["image"] or {}
        video = group["video"] or {}
        title = (
            video.get("notes")
            or image.get("notes")
            or f"镜头 {key[1:]}"
        )
        shots.append(
            Shot(
                id=key,
                order=order,
                title=str(title),
                duration_seconds=_duration_seconds(video.get("duration_hint")),
                image_prompt=str(image.get("prompt", "")),
                video_prompt=str(video.get("prompt", "")),
                negative_prompt=str(
                    video.get("negative_prompt")
                    or image.get("negative_prompt")
                    or ""
                ),
                source_task_ids=group["task_ids"],
                storyboard_image_path=str(
                    image.get("storyboard_image_path")
                    or image.get("output_path")
                    or ""
                ),
                audio_cue=str(video.get("audio_cue") or ""),
            )
        )

    pixel_profile_data = project_info.get("pixel_profile") or {}
    if not isinstance(pixel_profile_data, dict):
        pixel_profile_data = {}

    return ProductionProject(
        title=str(project_info.get("title") or manifest_path.stem),
        platform=str(project_info.get("platform") or ""),
        aspect_ratio=str(project_info.get("aspect_ratio") or ""),
        notes=str(project_info.get("notes") or ""),
        source_manifest=str(manifest_path),
        pipeline_mode=str(project_info.get("pipeline_mode") or "legacy"),
        pixel_profile=PixelProfile.model_validate(pixel_profile_data),
        sample_shot_id=(
            str(project_info["sample_shot_id"])
            if project_info.get("sample_shot_id")
            else None
        ),
        shots=shots,
    )
