from __future__ import annotations

from pathlib import Path

import pytest

from production_workspace.models import AttemptStatus, ProductionProject, Shot
from production_workspace.service import (
    WorkspaceOperationError,
    add_attempt,
    export_delivery,
    readiness_warnings,
    select_attempt,
)


def make_project() -> ProductionProject:
    return ProductionProject(
        title="三镜头动画",
        aspect_ratio="9:16",
        shots=[
            Shot(id=f"S{index:02d}", order=index, title=f"镜头 {index}")
            for index in range(1, 4)
        ],
    )


def test_attempts_are_traceable_and_selectable(tmp_path):
    project = make_project()
    first_asset = tmp_path / "失败版本.mp4"
    second_asset = tmp_path / "最终版本.mp4"
    first_asset.write_bytes(b"failed")
    second_asset.write_bytes(b"accepted")

    first = add_attempt(
        project,
        "S01",
        "jimeng",
        "prompt v1",
        status=AttemptStatus.REJECTED,
        asset_paths=[str(first_asset)],
        failure_tags=["character_drift"],
    )
    second = add_attempt(
        project,
        "S01",
        "jimeng",
        "prompt v2",
        status=AttemptStatus.PENDING,
        asset_paths=[str(second_asset)],
    )
    selected = select_attempt(project, "S01", second.id)

    assert first.attempt == 1
    assert first.failures[0].tag == "character_drift"
    assert selected.attempt == 2
    assert project.find_shot("S01").selected_attempt_id == second.id


def test_attempt_without_asset_cannot_be_selected():
    project = make_project()
    attempt = add_attempt(project, "S01", "jimeng", "prompt")

    with pytest.raises(WorkspaceOperationError, match="没有关联素材"):
        select_attempt(project, "S01", attempt.id)


def test_export_requires_every_shot_and_preserves_sources(tmp_path):
    project = make_project()
    source_files: list[Path] = []
    for shot in project.shots:
        source = tmp_path / "源素材" / f"{shot.id}.mp4"
        source.parent.mkdir(exist_ok=True)
        source.write_bytes(shot.id.encode())
        source_files.append(source)
        attempt = add_attempt(
            project,
            shot.id,
            "jimeng",
            f"{shot.id} prompt",
            asset_paths=[str(source)],
        )
        select_attempt(project, shot.id, attempt.id)

    output = tmp_path / "交付包"
    report = export_delivery(project, output)

    assert report.status == "ready"
    assert [path.name for path in (output / "assets").iterdir()] == [
        "01_S01_attempt-01_01.mp4",
        "02_S02_attempt-01_01.mp4",
        "03_S03_attempt-01_01.mp4",
    ]
    assert (output / "shot-list.csv").is_file()
    assert (output / "publishing-checklist.md").is_file()
    assert all(path.is_file() for path in source_files)


def test_missing_selected_asset_blocks_delivery(tmp_path):
    project = make_project()
    for shot in project.shots:
        missing = tmp_path / f"{shot.id}.mp4"
        attempt = add_attempt(
            project,
            shot.id,
            "jimeng",
            "prompt",
            asset_paths=[str(missing)],
        )
        select_attempt(project, shot.id, attempt.id)

    warnings = readiness_warnings(project)

    assert len(warnings) == 3
    with pytest.raises(WorkspaceOperationError, match="素材不存在"):
        export_delivery(project, tmp_path / "delivery")


def test_export_refuses_non_empty_directory(tmp_path):
    project = make_project()
    for shot in project.shots:
        source = tmp_path / f"{shot.id}.mp4"
        source.write_bytes(b"video")
        attempt = add_attempt(
            project,
            shot.id,
            "jimeng",
            "prompt",
            asset_paths=[str(source)],
        )
        select_attempt(project, shot.id, attempt.id)
    output = tmp_path / "delivery"
    output.mkdir()
    (output / "keep.txt").write_text("do not overwrite", encoding="utf-8")

    with pytest.raises(WorkspaceOperationError, match="必须为空"):
        export_delivery(project, output)

    assert (output / "keep.txt").read_text(encoding="utf-8") == "do not overwrite"
