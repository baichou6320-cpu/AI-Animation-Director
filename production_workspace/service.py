from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any, Iterable

from .models import (
    ApprovalStatus,
    AttemptStatus,
    DeliveryItem,
    DeliveryReport,
    FailureRecord,
    FailureTag,
    GenerationAttempt,
    MediaAsset,
    ProductionPhase,
    ProductionProject,
    infer_media_kind,
)


class WorkspaceOperationError(Exception):
    """Raised when a production workspace operation cannot be completed."""


REQUIRED_QUALITY_SCORES = {
    ProductionPhase.KEYFRAME: {
        "composition",
        "style_match",
        "readability",
        "continuity",
    },
    ProductionPhase.VIDEO: {
        "motion_completion",
        "temporal_stability",
        "camera_control",
        "continuity",
    },
    ProductionPhase.PIXEL_FINISH: {
        "pixel_stability",
        "palette_consistency",
        "editability",
    },
}


def _is_approved(status: str) -> bool:
    return status in {ApprovalStatus.APPROVED, ApprovalStatus.BYPASSED}


def _validate_phase_gate(
    project: ProductionProject, shot_id: str, phase: ProductionPhase
) -> None:
    if project.pipeline_mode != "pixel_short":
        return
    if phase in {ProductionPhase.KEYFRAME, ProductionPhase.VIDEO} and not _is_approved(
        project.animatic_state.status
    ):
        raise WorkspaceOperationError("动态分镜尚未批准，不能进入正式关键帧或视频生产")
    shot = project.find_shot(shot_id)
    if phase == ProductionPhase.VIDEO:
        if shot.selected_attempt_for(ProductionPhase.KEYFRAME) is None:
            raise WorkspaceOperationError(f"{shot_id} 尚未选择通过审核的关键帧")
        if (
            project.sample_shot_id
            and not _is_approved(project.sample_review_status)
            and shot_id != project.sample_shot_id
        ):
            raise WorkspaceOperationError(
                f"样片 {project.sample_shot_id} 尚未批准，不能批量生成其他镜头"
            )
    if phase == ProductionPhase.PIXEL_FINISH:
        if shot.selected_attempt_for(ProductionPhase.VIDEO) is None:
            raise WorkspaceOperationError(f"{shot_id} 尚未选择通过审核的视频版本")


def add_attempt(
    project: ProductionProject,
    shot_id: str,
    provider: str,
    prompt: str,
    *,
    model: str = "",
    status: AttemptStatus = AttemptStatus.PENDING,
    asset_paths: Iterable[str] = (),
    failure_tags: Iterable[str] = (),
    notes: str = "",
    parameters: dict[str, Any] | None = None,
    phase: ProductionPhase | str = ProductionPhase.VIDEO,
    quality_scores: dict[str, int] | None = None,
    decision_reason: str = "",
) -> GenerationAttempt:
    try:
        shot = project.find_shot(shot_id)
    except KeyError as exc:
        raise WorkspaceOperationError(str(exc)) from exc

    phase = ProductionPhase(phase)
    _validate_phase_gate(project, shot_id, phase)

    failures: list[FailureRecord] = []
    for tag in failure_tags:
        try:
            failures.append(FailureRecord(tag=FailureTag(tag)))
        except ValueError as exc:
            raise WorkspaceOperationError(f"未知失败标签：{tag}") from exc

    assets = [
        MediaAsset(kind=infer_media_kind(path), path=str(Path(path).resolve()))
        for path in asset_paths
        if str(path).strip()
    ]
    attempt = GenerationAttempt(
        shot_id=shot.id,
        attempt=len(shot.attempts) + 1,
        phase=phase,
        provider=provider,
        model=model,
        prompt=prompt,
        parameters=parameters or {},
        status=status,
        failures=failures,
        assets=assets,
        notes=notes,
        quality_scores=quality_scores or {},
        decision_reason=decision_reason,
    )
    shot.attempts.append(attempt)
    return attempt


def select_attempt(
    project: ProductionProject, shot_id: str, attempt_id: str
) -> GenerationAttempt:
    try:
        shot = project.find_shot(shot_id)
    except KeyError as exc:
        raise WorkspaceOperationError(str(exc)) from exc
    attempt = next(
        (candidate for candidate in shot.attempts if candidate.id == attempt_id),
        None,
    )
    if attempt is None:
        raise WorkspaceOperationError(
            f"镜头 {shot_id} 中不存在生成记录 {attempt_id}"
        )
    if not attempt.assets:
        raise WorkspaceOperationError("没有关联素材的生成记录不能设为最终版本")
    if project.pipeline_mode == "pixel_short":
        required = REQUIRED_QUALITY_SCORES[ProductionPhase(attempt.phase)]
        missing = sorted(required - set(attempt.quality_scores))
        low = {
            name: attempt.quality_scores[name]
            for name in required & set(attempt.quality_scores)
            if attempt.quality_scores[name] < 4
        }
        if missing:
            raise WorkspaceOperationError(
                "通过像素短片审核前缺少评分：" + ", ".join(missing)
            )
        if low:
            raise WorkspaceOperationError(f"评分低于 4，不能选为通过版本：{low}")
        if not attempt.decision_reason.strip():
            raise WorkspaceOperationError("通过版本必须记录选用理由")
    attempt.status = AttemptStatus.ACCEPTED
    phase = ProductionPhase(attempt.phase)
    if phase == ProductionPhase.KEYFRAME:
        shot.selected_keyframe_attempt_id = attempt.id
    elif phase == ProductionPhase.VIDEO:
        shot.selected_video_attempt_id = attempt.id
        shot.selected_attempt_id = attempt.id
    else:
        shot.selected_pixel_attempt_id = attempt.id
        shot.selected_attempt_id = attempt.id
    return attempt


def review_attempt(
    project: ProductionProject,
    shot_id: str,
    attempt_id: str,
    quality_scores: dict[str, int],
    decision_reason: str,
    *,
    status: AttemptStatus | str = AttemptStatus.PENDING,
) -> GenerationAttempt:
    shot = project.find_shot(shot_id)
    attempt = next(
        (candidate for candidate in shot.attempts if candidate.id == attempt_id),
        None,
    )
    if attempt is None:
        raise WorkspaceOperationError(f"镜头 {shot_id} 中不存在生成记录 {attempt_id}")
    for name, score in quality_scores.items():
        if not 1 <= int(score) <= 5:
            raise WorkspaceOperationError(f"评分必须在 1-5 之间：{name}={score}")
    attempt.quality_scores = {name: int(score) for name, score in quality_scores.items()}
    attempt.decision_reason = decision_reason.strip()
    attempt.status = AttemptStatus(status)
    return attempt


def approve_animatic(project: ProductionProject) -> None:
    output = Path(project.animatic_state.output_path)
    if not output.is_file():
        raise WorkspaceOperationError("动态分镜文件不存在，不能批准")
    if project.pipeline_mode == "pixel_short":
        expected_shots = sorted(project.shots, key=lambda item: item.order)
        panels = project.animatic_state.panels
        if [panel.shot_id for panel in panels] != [shot.id for shot in expected_shots]:
            raise WorkspaceOperationError("动态分镜面板必须与项目镜头数量和顺序一致")
        expected_duration = sum(shot.duration_seconds or 0 for shot in expected_shots)
        actual_duration = project.animatic_state.total_seconds or 0
        tolerance = 1 / project.pixel_profile.delivery_fps
        if abs(actual_duration - expected_duration) > tolerance:
            raise WorkspaceOperationError(
                "动态分镜总时长与镜头计划不一致，误差不能超过 1 帧"
            )
    project.animatic_state.status = ApprovalStatus.APPROVED


def approve_sample(project: ProductionProject) -> None:
    if not project.sample_shot_id:
        raise WorkspaceOperationError("项目未设置样片镜头")
    shot = project.find_shot(project.sample_shot_id)
    if shot.selected_attempt_for(ProductionPhase.VIDEO) is None:
        raise WorkspaceOperationError("样片镜头尚未选择通过审核的视频版本")
    project.sample_review_status = ApprovalStatus.APPROVED


def approve_final(
    project: ProductionProject,
    quality_scores: dict[str, int],
    review_note: str,
) -> None:
    output = Path(project.final_render.output_path)
    if not output.is_file():
        raise WorkspaceOperationError("最终母版不存在，不能批准")
    required = {"story_clarity", "pacing", "visual_consistency", "sound"}
    missing = sorted(required - set(quality_scores))
    if missing:
        raise WorkspaceOperationError("最终验收缺少评分：" + ", ".join(missing))
    low = {name: int(quality_scores[name]) for name in required if int(quality_scores[name]) < 4}
    if low:
        raise WorkspaceOperationError(f"最终评分低于 4，不能批准：{low}")
    if not review_note.strip():
        raise WorkspaceOperationError("最终验收必须记录审核结论")
    project.final_render.quality_scores = {
        name: int(score) for name, score in quality_scores.items()
    }
    project.final_render.review_note = review_note.strip()
    project.final_render.status = ApprovalStatus.APPROVED


def project_rows(project: ProductionProject) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for shot in sorted(project.shots, key=lambda item: item.order):
        selected = shot.selected_attempt()
        rows.append(
            [
                shot.id,
                shot.title,
                shot.duration_seconds or "",
                len(shot.attempts),
                selected.attempt if selected else "",
                "已选定" if selected else "待完成",
            ]
        )
    return rows


def readiness_warnings(project: ProductionProject) -> list[str]:
    warnings: list[str] = []
    for shot in sorted(project.shots, key=lambda item: item.order):
        if project.pipeline_mode == "pixel_short":
            if shot.selected_attempt_for(ProductionPhase.KEYFRAME) is None:
                warnings.append(f"{shot.id} 尚未选择关键帧版本")
            if shot.selected_attempt_for(ProductionPhase.VIDEO) is None:
                warnings.append(f"{shot.id} 尚未选择视频版本")
        attempt = shot.selected_attempt_for(ProductionPhase.PIXEL_FINISH)
        if attempt is None and project.pipeline_mode == "legacy":
            attempt = shot.selected_attempt()
        if attempt is None:
            warnings.append(f"{shot.id} 尚未选择像素成片版本")
            continue
        if not attempt.assets:
            warnings.append(f"{shot.id} 的最终版本没有关联素材")
            continue
        for asset in attempt.assets:
            if not Path(asset.path).is_file():
                warnings.append(f"{shot.id} 素材不存在：{asset.path}")
    if project.pipeline_mode == "pixel_short":
        if project.final_render.status != ApprovalStatus.APPROVED:
            warnings.append("最终母版尚未通过成片验收")
        elif not Path(project.final_render.output_path).is_file():
            warnings.append(f"最终母版不存在：{project.final_render.output_path}")
    return warnings


def export_delivery(
    project: ProductionProject,
    output_directory: str | Path,
) -> DeliveryReport:
    warnings = readiness_warnings(project)
    if warnings:
        raise WorkspaceOperationError("无法交付：\n- " + "\n- ".join(warnings))

    output = Path(output_directory).resolve()
    if output.exists() and any(output.iterdir()):
        raise WorkspaceOperationError(f"交付目录必须为空：{output}")
    output.mkdir(parents=True, exist_ok=True)
    assets_directory = output / "assets"
    assets_directory.mkdir()

    items: list[DeliveryItem] = []
    for shot in sorted(project.shots, key=lambda item: item.order):
        attempt = shot.selected_attempt()
        assert attempt is not None
        delivered_paths: list[str] = []
        for asset_index, asset in enumerate(attempt.assets, start=1):
            source = Path(asset.path)
            suffix = source.suffix.lower() or ".bin"
            destination = assets_directory / (
                f"{shot.order:02d}_{shot.id}_attempt-{attempt.attempt:02d}"
                f"_{asset_index:02d}{suffix}"
            )
            shutil.copy2(source, destination)
            delivered_paths.append(str(destination.relative_to(output)))
        items.append(
            DeliveryItem(
                shot_id=shot.id,
                attempt_id=attempt.id,
                source_paths=[asset.path for asset in attempt.assets],
                delivered_paths=delivered_paths,
            )
        )

    final_master = ""
    animatic = ""
    if project.pipeline_mode == "pixel_short":
        source_master = Path(project.final_render.output_path)
        master_destination = output / "final-master.mp4"
        shutil.copy2(source_master, master_destination)
        final_master = str(master_destination.relative_to(output))
        animatic_source = Path(project.animatic_state.output_path)
        if animatic_source.is_file():
            animatic_destination = output / "animatic.mp4"
            shutil.copy2(animatic_source, animatic_destination)
            animatic = str(animatic_destination.relative_to(output))

    report = DeliveryReport(
        project_id=project.id,
        project_title=project.title,
        status="ready",
        output_directory=str(output),
        final_master=final_master,
        animatic=animatic,
        items=items,
    )
    _write_delivery_files(project, report, output)
    return report


def _write_delivery_files(
    project: ProductionProject, report: DeliveryReport, output: Path
) -> None:
    with (output / "shot-list.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["order", "shot_id", "title", "duration_seconds", "attempt", "assets"]
        )
        for shot, item in zip(
            sorted(project.shots, key=lambda candidate: candidate.order),
            report.items,
            strict=True,
        ):
            selected = shot.selected_attempt()
            assert selected is not None
            writer.writerow(
                [
                    shot.order,
                    shot.id,
                    shot.title,
                    shot.duration_seconds or "",
                    selected.attempt,
                    " | ".join(item.delivered_paths),
                ]
            )

    (output / "project.json").write_text(
        json.dumps(project.model_dump(mode="json"), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (output / "delivery-report.json").write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    checklist = f"""# {project.title} 发布检查表

- [ ] 所有镜头按 `shot-list.csv` 顺序导入剪辑软件
- [ ] 画幅为 {project.aspect_ratio or "项目设定画幅"}
- [ ] 角色、服装、道具和画风连续
- [ ] 字幕、配乐和音效已检查
- [ ] 无平台水印、敏感信息或未授权素材
- [ ] 小红书标题、封面、正文和话题已准备
- [ ] 发布后记录曝光、完播、点赞、收藏和评论
"""
    (output / "publishing-checklist.md").write_text(
        checklist, encoding="utf-8", newline="\n"
    )
