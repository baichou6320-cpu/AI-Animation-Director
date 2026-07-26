from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

imageio_ffmpeg = pytest.importorskip("imageio_ffmpeg")

from production_workspace.media import (
    assemble_project,
    build_animatic,
    ffmpeg_executable,
    media_metadata,
    pixel_finish_project,
    prepare_web_background,
)
from production_workspace.models import (
    ApprovalStatus,
    ProductionPhase,
    ProductionProject,
    Shot,
)
from production_workspace.service import add_attempt, select_attempt


def run_ffmpeg(*arguments: str) -> None:
    completed = subprocess.run(
        [ffmpeg_executable(), "-hide_banner", "-loglevel", "error", *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def make_image(path: Path, color: str) -> None:
    run_ffmpeg(
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c={color}:s=320x180:d=0.04",
        "-frames:v",
        "1",
        str(path),
    )


def make_video(path: Path, color: str, duration: float = 0.5) -> None:
    run_ffmpeg(
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c={color}:s=640x360:r=24:d={duration}",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(path),
    )


def test_build_animatic_is_fifteen_seconds_at_delivery_spec(tmp_path):
    durations = (4, 3, 4, 4)
    colors = ("0x163447", "0x2c5b50", "0xc69b45", "0xf0c96a")
    shots: list[Shot] = []
    for index, (duration, color) in enumerate(zip(durations, colors), start=1):
        panel = tmp_path / f"S{index:02d}.png"
        make_image(panel, color)
        shots.append(
            Shot(
                id=f"S{index:02d}",
                order=index,
                title=f"镜头 {index}",
                duration_seconds=duration,
                storyboard_image_path=str(panel),
            )
        )
    project = ProductionProject(
        title="露水小灯动态分镜",
        pipeline_mode="pixel_short",
        aspect_ratio="16:9",
        shots=shots,
    )

    output = build_animatic(project, tmp_path / "animatic.mp4")
    metadata = media_metadata(output)

    assert project.animatic_state.total_seconds == 15
    assert project.animatic_state.status == ApprovalStatus.PENDING
    assert metadata["size"] == (1920, 1080)
    assert metadata["fps"] == pytest.approx(24, abs=0.1)
    assert metadata["duration"] == pytest.approx(15, abs=1 / 24)


def test_pixel_finish_and_assemble_use_fixed_pixel_spec(tmp_path):
    hero = tmp_path / "REF-HERO.png"
    source = tmp_path / "S01-source.mp4"
    make_image(hero, "0x315b55")
    make_video(source, "0xb3c777")
    project = ProductionProject(
        title="像素后期烟测",
        pipeline_mode="legacy",
        aspect_ratio="16:9",
        shots=[Shot(id="S01", order=1, title="镜头 1", duration_seconds=0.5)],
    )
    video = add_attempt(
        project,
        "S01",
        "jimeng",
        "wind moves the grass",
        phase=ProductionPhase.VIDEO,
        asset_paths=[str(source)],
    )
    select_attempt(project, "S01", video.id)

    finished_attempts = pixel_finish_project(
        project,
        tmp_path / "pixel",
        palette_source=hero,
    )
    finished = Path(finished_attempts[0].assets[0].path)
    metadata = media_metadata(finished)
    assert metadata["size"] == (1920, 1080)
    assert metadata["fps"] == pytest.approx(24, abs=0.1)
    palette_path = Path(project.final_render.palette_path)
    assert palette_path.is_file()
    palette_reader = imageio_ffmpeg.read_frames(str(palette_path), pix_fmt="rgb24")
    palette_metadata = next(palette_reader)
    palette_frame = next(palette_reader)
    palette_reader.close()
    palette_colors = {
        palette_frame[index : index + 3]
        for index in range(0, len(palette_frame), 3)
    }
    assert palette_metadata["size"] == (16, 16)
    assert len(palette_colors) <= 48
    frame_count, duration = imageio_ffmpeg.count_frames_and_secs(str(finished))
    assert frame_count == 12
    assert duration == pytest.approx(0.5, abs=1 / 24)

    finished_attempts[0].quality_scores = {
        "pixel_stability": 5,
        "palette_consistency": 5,
        "editability": 5,
    }
    finished_attempts[0].decision_reason = "固定调色板与整数倍放大通过"
    select_attempt(project, "S01", finished_attempts[0].id)
    master = assemble_project(project, tmp_path / "final-master.mp4")
    master_metadata = media_metadata(master)
    assert master.is_file()
    assert master_metadata["size"] == (1920, 1080)
    assert master_metadata["fps"] == pytest.approx(24, abs=0.1)
    assert master_metadata["duration"] == pytest.approx(0.5, abs=1 / 24)


def test_prepare_web_background_builds_scrub_friendly_media(tmp_path):
    source = tmp_path / "approved-hero.png"
    make_image(source, "0x526f54")

    bundle = prepare_web_background(
        source,
        tmp_path / "site-media",
        duration_seconds=1.0,
    )

    desktop = media_metadata(bundle.desktop_video)
    mobile = media_metadata(bundle.mobile_video)
    assert desktop["size"] == (1280, 720)
    assert mobile["size"] == (720, 1280)
    assert desktop["fps"] == pytest.approx(24, abs=0.1)
    assert desktop["duration"] == pytest.approx(1.0, abs=1 / 24)
    assert "audio_codec" not in desktop
    assert bundle.poster.is_file()
    assert bundle.poster.suffix == ".webp"
