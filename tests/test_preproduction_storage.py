from __future__ import annotations

import json

import pytest

from production_workspace.preproduction_models import (
    IntakeState,
    ProjectConstraints,
    WebBackgroundSpec,
)
from production_workspace.preproduction_storage import (
    StructuredProjectError,
    create_draft_project,
    load_structured_artifact,
    load_structured_manifest,
    save_structured_artifact,
    validate_structured_project,
    write_json_schemas,
)


def test_create_draft_project_uses_split_structured_files(tmp_path):
    project_root = create_draft_project(
        tmp_path / "projects",
        project_id="warm-isekai",
        title="温馨异世界",
        raw_input="我想做一个温馨异世界动画",
        extracted_fields={"emotional_target": "温馨"},
        constraints=ProjectConstraints(platform="jimeng"),
    )

    manifest = load_structured_manifest(project_root)
    intake = load_structured_artifact(project_root, manifest.files.intake)
    web_background = load_structured_artifact(
        project_root, manifest.files.web_background
    )

    assert manifest.project_id == "warm-isekai"
    assert manifest.status == "draft"
    assert manifest.current_stage == "intake"
    assert intake.raw_input == "我想做一个温馨异世界动画"
    assert intake.extracted_fields == {"emotional_target": "温馨"}
    assert isinstance(web_background, WebBackgroundSpec)
    assert web_background.delivery_profile == "website_background"
    assert web_background.audio is False
    assert "raw_input" not in json.loads(
        (project_root / "project.json").read_text(encoding="utf-8")
    )
    assert validate_structured_project(project_root) == manifest


def test_draft_creation_refuses_to_overwrite_existing_project(tmp_path):
    root = tmp_path / "projects"
    create_draft_project(
        root,
        project_id="same-project",
        title="第一版",
        raw_input="第一版输入",
    )

    with pytest.raises(StructuredProjectError, match="已存在"):
        create_draft_project(
            root,
            project_id="same-project",
            title="第二版",
            raw_input="第二版输入",
        )


def test_save_stage_artifact_creates_backup(tmp_path):
    project_root = create_draft_project(
        tmp_path,
        project_id="qa-draft",
        title="QA 草稿",
        raw_input="像素动画",
    )
    intake = load_structured_artifact(project_root, "input/intake.json")
    assert isinstance(intake, IntakeState)
    intake.confirmed_fields["platform"] = "jimeng"

    saved = save_structured_artifact(project_root, "input/intake.json", intake)

    assert saved.with_suffix(".json.bak").is_file()
    reloaded = load_structured_artifact(project_root, "input/intake.json")
    assert reloaded.confirmed_fields["platform"] == "jimeng"


def test_corrupt_stage_file_fails_validation_without_rewriting(tmp_path):
    project_root = create_draft_project(
        tmp_path,
        project_id="broken-stage",
        title="损坏测试",
        raw_input="测试输入",
    )
    path = project_root / "creative/concept.json"
    path.write_text("{broken json", encoding="utf-8")

    with pytest.raises(StructuredProjectError, match="无效"):
        validate_structured_project(project_root)

    assert path.read_text(encoding="utf-8") == "{broken json"


def test_exported_json_schemas_are_valid_json_objects(tmp_path):
    paths = write_json_schemas(tmp_path / "schemas")

    assert len(paths) == 10
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["type"] == "object"
        assert "$defs" in payload or "properties" in payload


def test_web_background_rejects_audio():
    with pytest.raises(ValueError, match="must not contain audio"):
        WebBackgroundSpec(project_id="silent-hero", audio=True)


def test_public_web_background_requires_all_delivery_assets():
    with pytest.raises(ValueError, match="requires desktop, mobile, and poster"):
        WebBackgroundSpec(
            project_id="public-hero",
            public_release_ready=True,
            desktop_asset="hero-desktop.mp4",
        )
