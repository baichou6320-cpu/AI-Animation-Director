from __future__ import annotations

import pytest

from production_workspace.models import ProductionProject, Shot
from production_workspace.storage import ProjectStorageError, load_project, save_project


def make_project() -> ProductionProject:
    return ProductionProject(
        title="测试项目",
        shots=[Shot(id="S01", order=1, title="开场")],
    )


def test_save_and_load_project_with_chinese_path(tmp_path):
    path = tmp_path / "动画项目" / "生产记录.json"
    save_project(make_project(), path)

    loaded = load_project(path)

    assert loaded.title == "测试项目"
    assert loaded.project_file == str(path.resolve())


def test_corrupt_project_is_not_overwritten(tmp_path):
    path = tmp_path / "broken.json"
    original = "{this is not json"
    path.write_text(original, encoding="utf-8")

    with pytest.raises(ProjectStorageError, match="原文件未被修改"):
        load_project(path)

    assert path.read_text(encoding="utf-8") == original


def test_existing_project_gets_backup(tmp_path):
    path = tmp_path / "project.json"
    project = make_project()
    save_project(project, path)
    first_version = path.read_text(encoding="utf-8")
    project.notes = "第二版"

    save_project(project, path)

    assert path.with_suffix(".json.bak").read_text(encoding="utf-8") == first_version
