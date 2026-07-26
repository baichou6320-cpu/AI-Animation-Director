from __future__ import annotations

import json
from pathlib import Path

import pytest

from production_workspace.importer import ManifestImportError, import_manifest


def test_import_three_shot_manifest(tmp_path):
    manifest = {
        "project": {
            "title": "小红书三镜头短片",
            "platform": "jimeng",
            "aspect_ratio": "9:16",
        },
        "tasks": [],
    }
    for index in range(1, 4):
        manifest["tasks"].extend(
            [
                {
                    "id": f"img_shot_{index:03d}",
                    "type": "image",
                    "prompt": f"image {index}",
                    "negative_prompt": "watermark",
                },
                {
                    "id": f"vid_shot_{index:03d}",
                    "type": "video_image",
                    "prompt": f"video {index}",
                    "duration_hint": f"{index + 2}s",
                },
            ]
        )
    path = tmp_path / "中文项目.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    project = import_manifest(path)

    assert project.title == "小红书三镜头短片"
    assert [shot.id for shot in project.shots] == ["S01", "S02", "S03"]
    assert project.shots[0].image_prompt == "image 1"
    assert project.shots[0].video_prompt == "video 1"
    assert project.shots[2].duration_seconds == 5


def test_manifest_without_recognizable_shots_fails(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "tasks": [
                    {"id": "character_reference", "type": "image", "prompt": "x"}
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ManifestImportError, match="没有找到"):
        import_manifest(path)


def test_import_golden_pixel_short_manifest():
    manifest = (
        Path(__file__).parents[1]
        / "examples"
        / "workspace"
        / "dew-light-pixel-15s-manifest.json"
    )

    project = import_manifest(manifest)

    assert project.pipeline_mode == "pixel_short"
    assert project.sample_shot_id == "S03"
    assert project.aspect_ratio == "16:9"
    assert [shot.duration_seconds for shot in project.shots] == [4, 3, 4, 4]
    assert sum(shot.duration_seconds or 0 for shot in project.shots) == 15
    assert project.pixel_profile.base_width == 320
    assert project.pixel_profile.delivery_width == 1920
    assert project.pixel_profile.palette_colors == 48
    assert "以 IMG-S03 为唯一首帧" in project.find_shot("S03").video_prompt
