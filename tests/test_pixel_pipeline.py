from __future__ import annotations

from pathlib import Path

import pytest

from production_workspace.models import (
    AnimaticPanel,
    AnimaticState,
    ApprovalStatus,
    ProductionPhase,
    ProductionProject,
    Shot,
)
from production_workspace.service import (
    WorkspaceOperationError,
    add_attempt,
    approve_animatic,
    approve_final,
    approve_sample,
    select_attempt,
)


KEYFRAME_SCORES = {
    "composition": 4,
    "style_match": 5,
    "readability": 4,
    "continuity": 4,
}
VIDEO_SCORES = {
    "motion_completion": 4,
    "temporal_stability": 4,
    "camera_control": 4,
    "continuity": 5,
}
PIXEL_SCORES = {
    "pixel_stability": 5,
    "palette_consistency": 4,
    "editability": 4,
}


def make_pixel_project(tmp_path: Path) -> ProductionProject:
    return ProductionProject(
        title="露水小灯",
        platform="jimeng",
        aspect_ratio="16:9",
        pipeline_mode="pixel_short",
        sample_shot_id="S03",
        shots=[
            Shot(
                id=f"S{index:02d}",
                order=index,
                title=f"镜头 {index}",
                duration_seconds=duration,
            )
            for index, duration in enumerate((4, 3, 4, 4), start=1)
        ],
    )


def add_and_select_keyframe(
    project: ProductionProject, tmp_path: Path, shot_id: str
):
    asset = tmp_path / f"{shot_id}.png"
    asset.write_bytes(b"png")
    attempt = add_attempt(
        project,
        shot_id,
        "jimeng",
        f"{shot_id} keyframe prompt",
        phase=ProductionPhase.KEYFRAME,
        asset_paths=[str(asset)],
        quality_scores=KEYFRAME_SCORES,
        decision_reason="构图、风格和连续性满足镜头目标",
    )
    select_attempt(project, shot_id, attempt.id)
    return attempt


def test_animatic_gate_blocks_formal_generation(tmp_path):
    project = make_pixel_project(tmp_path)

    with pytest.raises(WorkspaceOperationError, match="动态分镜尚未批准"):
        add_attempt(
            project,
            "S01",
            "jimeng",
            "keyframe",
            phase=ProductionPhase.KEYFRAME,
        )

    animatic = tmp_path / "animatic.mp4"
    animatic.write_bytes(b"animatic")
    project.animatic_state = AnimaticState(
        status=ApprovalStatus.PENDING,
        output_path=str(animatic),
        total_seconds=15,
        panels=[
            AnimaticPanel(
                shot_id=shot.id,
                image_path=str(tmp_path / f"{shot.id}-storyboard.png"),
                duration_seconds=shot.duration_seconds or 1,
            )
            for shot in project.shots
        ],
    )
    approve_animatic(project)

    attempt = add_and_select_keyframe(project, tmp_path, "S01")
    shot = project.find_shot("S01")
    assert shot.selected_keyframe_attempt_id == attempt.id
    assert shot.selected_video_attempt_id is None


def test_animatic_approval_rejects_wrong_panel_order_or_duration(tmp_path):
    project = make_pixel_project(tmp_path)
    animatic = tmp_path / "animatic.mp4"
    animatic.write_bytes(b"animatic")
    project.animatic_state = AnimaticState(
        status=ApprovalStatus.PENDING,
        output_path=str(animatic),
        total_seconds=14,
        panels=[
            AnimaticPanel(
                shot_id=shot.id,
                image_path="placeholder.png",
                duration_seconds=shot.duration_seconds or 1,
            )
            for shot in project.shots
        ],
    )

    with pytest.raises(WorkspaceOperationError, match="总时长"):
        approve_animatic(project)

    project.animatic_state.total_seconds = 15
    project.animatic_state.panels.reverse()
    with pytest.raises(WorkspaceOperationError, match="数量和顺序"):
        approve_animatic(project)


def test_pixel_short_selection_requires_scores_and_reason(tmp_path):
    project = make_pixel_project(tmp_path)
    project.animatic_state.status = ApprovalStatus.APPROVED
    asset = tmp_path / "S01.png"
    asset.write_bytes(b"png")
    attempt = add_attempt(
        project,
        "S01",
        "jimeng",
        "keyframe",
        phase=ProductionPhase.KEYFRAME,
        asset_paths=[str(asset)],
    )

    with pytest.raises(WorkspaceOperationError, match="缺少评分"):
        select_attempt(project, "S01", attempt.id)

    attempt.quality_scores = KEYFRAME_SCORES
    with pytest.raises(WorkspaceOperationError, match="选用理由"):
        select_attempt(project, "S01", attempt.id)


def test_sample_gate_blocks_batch_video(tmp_path):
    project = make_pixel_project(tmp_path)
    project.animatic_state.status = ApprovalStatus.APPROVED
    add_and_select_keyframe(project, tmp_path, "S01")
    add_and_select_keyframe(project, tmp_path, "S03")

    with pytest.raises(WorkspaceOperationError, match="样片 S03 尚未批准"):
        add_attempt(
            project,
            "S01",
            "jimeng",
            "motion contract",
            phase=ProductionPhase.VIDEO,
        )

    sample_asset = tmp_path / "S03.mp4"
    sample_asset.write_bytes(b"video")
    sample = add_attempt(
        project,
        "S03",
        "jimeng",
        "motion contract",
        phase=ProductionPhase.VIDEO,
        asset_paths=[str(sample_asset)],
        quality_scores=VIDEO_SCORES,
        decision_reason="动作完成，镜头稳定，像素漂移可接受",
    )
    select_attempt(project, "S03", sample.id)
    approve_sample(project)

    batch_attempt = add_attempt(
        project,
        "S01",
        "jimeng",
        "motion contract",
        phase=ProductionPhase.VIDEO,
    )
    assert batch_attempt.phase == ProductionPhase.VIDEO


def test_phase_selections_remain_separate(tmp_path):
    project = make_pixel_project(tmp_path)
    project.animatic_state.status = ApprovalStatus.APPROVED
    project.sample_review_status = ApprovalStatus.APPROVED
    keyframe = add_and_select_keyframe(project, tmp_path, "S01")

    video_asset = tmp_path / "S01-video.mp4"
    video_asset.write_bytes(b"video")
    video = add_attempt(
        project,
        "S01",
        "jimeng",
        "motion contract",
        phase=ProductionPhase.VIDEO,
        asset_paths=[str(video_asset)],
        quality_scores=VIDEO_SCORES,
        decision_reason="运动和摄影机符合动态分镜",
    )
    select_attempt(project, "S01", video.id)

    pixel_asset = tmp_path / "S01-pixel.mp4"
    pixel_asset.write_bytes(b"pixel")
    pixel = add_attempt(
        project,
        "S01",
        "local-ffmpeg",
        "pixel finish",
        phase=ProductionPhase.PIXEL_FINISH,
        asset_paths=[str(pixel_asset)],
        quality_scores=PIXEL_SCORES,
        decision_reason="颗粒、调色板和放大方式统一",
    )
    select_attempt(project, "S01", pixel.id)

    shot = project.find_shot("S01")
    assert shot.selected_keyframe_attempt_id == keyframe.id
    assert shot.selected_video_attempt_id == video.id
    assert shot.selected_pixel_attempt_id == pixel.id


def test_final_approval_requires_four_scores_at_four_or_better(tmp_path):
    project = make_pixel_project(tmp_path)
    master = tmp_path / "final-master.mp4"
    master.write_bytes(b"master")
    project.final_render.output_path = str(master)

    with pytest.raises(WorkspaceOperationError, match="缺少评分"):
        approve_final(project, {"story_clarity": 5}, "test")

    with pytest.raises(WorkspaceOperationError, match="低于 4"):
        approve_final(
            project,
            {
                "story_clarity": 5,
                "pacing": 3,
                "visual_consistency": 4,
                "sound": 4,
            },
            "节奏仍需修正",
        )

    approve_final(
        project,
        {
            "story_clarity": 5,
            "pacing": 4,
            "visual_consistency": 4,
            "sound": 4,
        },
        "故事、节奏、画面和声音达到交付标准",
    )
    assert project.final_render.status == ApprovalStatus.APPROVED
