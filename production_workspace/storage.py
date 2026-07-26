from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from pydantic import ValidationError

from .models import ProductionProject, utc_now


class ProjectStorageError(Exception):
    """Raised when a project file cannot be read or safely written."""


def load_project(path: str | Path) -> ProductionProject:
    project_path = Path(path)
    try:
        raw = project_path.read_text(encoding="utf-8")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("project JSON must contain an object")
        project = ProductionProject.model_validate(_migrate_project_payload(payload))
    except FileNotFoundError as exc:
        raise ProjectStorageError(f"项目文件不存在：{project_path}") from exc
    except (OSError, ValidationError, ValueError) as exc:
        raise ProjectStorageError(f"项目文件无效，原文件未被修改：{exc}") from exc
    project.project_file = str(project_path.resolve())
    return project


def _migrate_project_payload(payload: dict) -> dict:
    migrated = dict(payload)
    if int(migrated.get("schema_version", 1)) >= 2:
        return migrated

    migrated["schema_version"] = 2
    migrated.setdefault("pipeline_mode", "legacy")
    for shot in migrated.get("shots", []):
        if not isinstance(shot, dict):
            continue
        selected_id = shot.get("selected_attempt_id")
        if selected_id and not shot.get("selected_video_attempt_id"):
            shot["selected_video_attempt_id"] = selected_id
    return migrated


def save_project(project: ProductionProject, path: str | Path) -> Path:
    project_path = Path(path)
    project_path.parent.mkdir(parents=True, exist_ok=True)
    project.updated_at = utc_now()
    project.project_file = str(project_path.resolve())

    temporary_path = project_path.with_suffix(project_path.suffix + ".tmp")
    backup_path = project_path.with_suffix(project_path.suffix + ".bak")
    payload = project.model_dump(mode="json")

    try:
        temporary_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        # Validate the temporary file before replacing a known-good project.
        ProductionProject.model_validate_json(temporary_path.read_text(encoding="utf-8"))
        if project_path.exists():
            shutil.copy2(project_path, backup_path)
        os.replace(temporary_path, project_path)
    except (OSError, ValidationError, ValueError) as exc:
        temporary_path.unlink(missing_ok=True)
        raise ProjectStorageError(f"保存失败，原项目文件已保留：{exc}") from exc

    return project_path
