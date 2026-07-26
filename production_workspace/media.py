from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import (
    AnimaticPanel,
    AnimaticState,
    ApprovalStatus,
    AttemptStatus,
    GenerationAttempt,
    PixelProfile,
    ProductionPhase,
    ProductionProject,
)
from .service import WorkspaceOperationError, add_attempt


VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


@dataclass(frozen=True)
class WebMediaBundle:
    desktop_video: Path
    mobile_video: Path
    poster: Path
    duration_seconds: float

    def as_dict(self) -> dict[str, str | float]:
        return {
            "desktop_video": str(self.desktop_video),
            "mobile_video": str(self.mobile_video),
            "poster": str(self.poster),
            "duration_seconds": self.duration_seconds,
        }


def ffmpeg_executable() -> str:
    try:
        import imageio_ffmpeg
    except ImportError as exc:
        raise WorkspaceOperationError(
            "缺少 imageio-ffmpeg，请先运行 python -m pip install -e ."
        ) from exc
    try:
        return imageio_ffmpeg.get_ffmpeg_exe()
    except RuntimeError:
        package_directory = Path(imageio_ffmpeg.__file__).resolve().parent
        candidates = sorted((package_directory / "binaries").glob("ffmpeg*"))
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
        raise WorkspaceOperationError(
            "imageio-ffmpeg 已安装，但未找到可执行文件；请设置 IMAGEIO_FFMPEG_EXE"
        )


def _run_ffmpeg(arguments: list[str]) -> None:
    command = [ffmpeg_executable(), "-hide_banner", "-loglevel", "error", *arguments]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise WorkspaceOperationError(f"FFmpeg 执行失败：{detail}")


def _require_file(path: str | Path, label: str) -> Path:
    resolved = Path(path).resolve()
    if not resolved.is_file():
        raise WorkspaceOperationError(f"{label}不存在：{resolved}")
    return resolved


def _first_asset(attempt: GenerationAttempt, suffixes: set[str], label: str) -> Path:
    for asset in attempt.assets:
        candidate = Path(asset.path)
        if candidate.suffix.lower() in suffixes and candidate.is_file():
            return candidate.resolve()
    raise WorkspaceOperationError(f"{attempt.shot_id} 的{label}版本没有可用素材")


def _concat_path(path: Path) -> str:
    return path.as_posix().replace("'", "'\\''")


def _write_still_concat(panels: Iterable[AnimaticPanel], path: Path) -> None:
    panel_list = list(panels)
    lines: list[str] = []
    for panel in panel_list:
        image = _require_file(panel.image_path, f"{panel.shot_id} 动态分镜图片")
        lines.append(f"file '{_concat_path(image)}'")
        lines.append(f"duration {panel.duration_seconds:.6f}")
    if panel_list:
        final_image = _require_file(
            panel_list[-1].image_path, f"{panel_list[-1].shot_id} 动态分镜图片"
        )
        lines.append(f"file '{_concat_path(final_image)}'")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_video_concat(paths: Iterable[Path], path: Path) -> None:
    lines = [f"file '{_concat_path(item.resolve())}'" for item in paths]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _storyboard_panels(project: ProductionProject) -> list[AnimaticPanel]:
    panels: list[AnimaticPanel] = []
    for shot in sorted(project.shots, key=lambda item: item.order):
        image_path = shot.storyboard_image_path
        if not image_path:
            keyframe = shot.selected_attempt_for(ProductionPhase.KEYFRAME)
            if keyframe:
                image_path = str(_first_asset(keyframe, IMAGE_SUFFIXES, "关键帧"))
        if not image_path:
            raise WorkspaceOperationError(
                f"{shot.id} 缺少 storyboard_image_path，无法制作动态分镜"
            )
        if not shot.duration_seconds:
            raise WorkspaceOperationError(f"{shot.id} 缺少镜头时长")
        panels.append(
            AnimaticPanel(
                shot_id=shot.id,
                image_path=str(Path(image_path).resolve()),
                duration_seconds=shot.duration_seconds,
                audio_cue=shot.audio_cue,
            )
        )
    return panels


def build_animatic(
    project: ProductionProject,
    output_path: str | Path,
    *,
    temporary_audio_path: str | Path | None = None,
) -> Path:
    panels = _storyboard_panels(project)
    total_seconds = sum(panel.duration_seconds for panel in panels)
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    audio = (
        _require_file(temporary_audio_path, "临时声音")
        if temporary_audio_path
        else None
    )

    profile = project.pixel_profile
    width = profile.delivery_width
    height = profile.delivery_height
    with tempfile.TemporaryDirectory(prefix="animation-animatic-") as temporary:
        concat_path = Path(temporary) / "panels.txt"
        _write_still_concat(panels, concat_path)
        arguments = [
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
        ]
        if audio:
            arguments.extend(["-i", str(audio)])
        arguments.extend(
            [
                "-vf",
                (
                    f"scale={width}:{height}:force_original_aspect_ratio=decrease:"
                    f"flags=lanczos,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
                    f"fps={profile.delivery_fps},format=yuv420p"
                ),
                "-t",
                f"{total_seconds:.6f}",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "18",
            ]
        )
        if audio:
            arguments.extend(["-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac"])
        else:
            arguments.append("-an")
        arguments.extend(["-movflags", "+faststart", str(output)])
        _run_ffmpeg(arguments)

    project.animatic_state = AnimaticState(
        status=ApprovalStatus.PENDING,
        output_path=str(output),
        temporary_audio_path=str(audio) if audio else "",
        total_seconds=total_seconds,
        panels=panels,
    )
    return output


def generate_palette(
    source_path: str | Path,
    output_path: str | Path,
    profile: PixelProfile,
) -> Path:
    source = _require_file(source_path, "REF-HERO 调色板来源")
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    _run_ffmpeg(
        [
            "-y",
            "-i",
            str(source),
            "-vf",
            (
                f"scale={profile.base_width}:{profile.base_height}:"
                "force_original_aspect_ratio=decrease:flags=area,"
                f"pad={profile.base_width}:{profile.base_height}:"
                "(ow-iw)/2:(oh-ih)/2:color=black,"
                f"palettegen=max_colors={profile.palette_colors}:stats_mode=full"
            ),
            "-frames:v",
            "1",
            str(output),
        ]
    )
    return output


def pixel_finish_clip(
    input_path: str | Path,
    output_path: str | Path,
    palette_path: str | Path,
    profile: PixelProfile,
) -> Path:
    source = _require_file(input_path, "待像素化视频")
    palette = _require_file(palette_path, "全局调色板")
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    source_duration = float(media_metadata(source).get("duration") or 0)
    dither = "none" if profile.dithering == "none" else "bayer:bayer_scale=3"
    filter_graph = (
        f"[0:v]tpad=stop_mode=clone:stop_duration={1 / profile.motion_fps:.9f},"
        f"fps={profile.motion_fps}:round=up,"
        f"scale={profile.base_width}:{profile.base_height}:"
        "force_original_aspect_ratio=decrease:flags=area,"
        f"pad={profile.base_width}:{profile.base_height}:"
        "(ow-iw)/2:(oh-ih)/2:color=black[low];"
        f"[low][1:v]paletteuse=dither={dither},"
        f"scale={profile.delivery_width}:{profile.delivery_height}:flags=neighbor,"
        f"fps={profile.delivery_fps},format=yuv420p[v]"
    )
    arguments = [
        "-y",
        "-i",
        str(source),
        "-i",
        str(palette),
        "-filter_complex",
        filter_graph,
        "-map",
        "[v]",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
    ]
    if source_duration:
        arguments.extend(["-t", f"{source_duration:.9f}"])
    arguments.extend(
        [
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    _run_ffmpeg(arguments)
    return output


def pixel_finish_project(
    project: ProductionProject,
    output_directory: str | Path,
    *,
    palette_source: str | Path | None = None,
    shot_ids: Iterable[str] | None = None,
) -> list[GenerationAttempt]:
    output = Path(output_directory).resolve()
    output.mkdir(parents=True, exist_ok=True)
    profile = project.pixel_profile
    source = palette_source or profile.palette_source
    if not source:
        raise WorkspaceOperationError("缺少 REF-HERO 或 pixel_profile.palette_source")
    palette_path = generate_palette(source, output / "global-palette.png", profile)
    requested = set(shot_ids or [shot.id for shot in project.shots])
    attempts: list[GenerationAttempt] = []
    for shot in sorted(project.shots, key=lambda item: item.order):
        if shot.id not in requested:
            continue
        video_attempt = shot.selected_attempt_for(ProductionPhase.VIDEO)
        if video_attempt is None:
            raise WorkspaceOperationError(f"{shot.id} 尚未选择通过审核的视频版本")
        source_video = _first_asset(video_attempt, VIDEO_SUFFIXES, "视频")
        finished = pixel_finish_clip(
            source_video,
            output / f"{shot.order:02d}_{shot.id}_pixel.mp4",
            palette_path,
            profile,
        )
        attempt = add_attempt(
            project,
            shot.id,
            provider="local-ffmpeg",
            model="pixel-finish-v1",
            prompt=(
                f"{profile.motion_fps}fps motion, {profile.base_width}x"
                f"{profile.base_height}, {profile.palette_colors} colors, "
                f"{profile.delivery_width}x{profile.delivery_height} nearest scaling"
            ),
            phase=ProductionPhase.PIXEL_FINISH,
            status=AttemptStatus.PENDING,
            asset_paths=[str(finished)],
            parameters=profile.model_dump(mode="json"),
            notes=f"source video attempt: {video_attempt.id}",
        )
        attempts.append(attempt)
        project.final_render.pixel_clips[shot.id] = str(finished)
    project.final_render.palette_path = str(palette_path)
    project.final_render.status = ApprovalStatus.PENDING
    return attempts


def assemble_project(
    project: ProductionProject,
    output_path: str | Path,
    *,
    audio_path: str | Path | None = None,
) -> Path:
    clips: list[Path] = []
    for shot in sorted(project.shots, key=lambda item: item.order):
        attempt = shot.selected_attempt_for(ProductionPhase.PIXEL_FINISH)
        if attempt is None and project.pipeline_mode == "legacy":
            attempt = shot.selected_attempt_for(ProductionPhase.VIDEO)
        if attempt is None:
            raise WorkspaceOperationError(f"{shot.id} 尚未选择像素成片版本")
        clips.append(_first_asset(attempt, VIDEO_SUFFIXES, "成片"))

    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    audio = _require_file(audio_path, "最终音频") if audio_path else None
    total_seconds = sum(shot.duration_seconds or 0 for shot in project.shots)
    with tempfile.TemporaryDirectory(prefix="animation-assemble-") as temporary:
        concat_path = Path(temporary) / "clips.txt"
        _write_video_concat(clips, concat_path)
        arguments = [
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
        ]
        if audio:
            arguments.extend(["-i", str(audio)])
        arguments.extend(
            [
                "-map",
                "0:v:0",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "18",
                "-r",
                str(project.pixel_profile.delivery_fps),
                "-pix_fmt",
                "yuv420p",
            ]
        )
        if audio:
            arguments.extend(["-map", "1:a:0", "-c:a", "aac", "-b:a", "192k"])
        else:
            arguments.append("-an")
        if total_seconds:
            arguments.extend(["-t", f"{total_seconds:.6f}"])
        arguments.extend(["-movflags", "+faststart", str(output)])
        _run_ffmpeg(arguments)

    project.final_render.output_path = str(output)
    project.final_render.audio_path = str(audio) if audio else ""
    project.final_render.status = ApprovalStatus.PENDING
    return output


def _aspect_crop(
    width: int,
    height: int,
    *,
    focus_x: float,
    focus_y: float = 0.5,
) -> str:
    ratio = width / height
    return (
        f"crop=w='min(iw,ih*{ratio:.9f})':"
        f"h='min(ih,iw/{ratio:.9f})':"
        f"x='(iw-ow)*{focus_x:.6f}':"
        f"y='(ih-oh)*{focus_y:.6f}'"
    )


def _web_video_arguments(
    source: Path,
    output: Path,
    *,
    width: int,
    height: int,
    duration_seconds: float,
    fps: int,
    keyframe_interval_seconds: float,
    focus_x: float,
    source_is_image: bool,
) -> list[str]:
    crop = _aspect_crop(width, height, focus_x=focus_x)
    if source_is_image:
        frame_count = max(round(duration_seconds * fps), 2)
        filter_chain = (
            f"{crop},"
            f"zoompan=z='1+0.04*on/{frame_count - 1}':"
            f"x='(iw-iw/zoom)*{focus_x:.6f}':"
            "y='(ih-ih/zoom)*0.5':"
            f"d=1:s={width}x{height}:fps={fps},"
            "format=yuv420p"
        )
        input_arguments = ["-loop", "1", "-framerate", str(fps), "-i", str(source)]
    else:
        filter_chain = (
            f"{crop},scale={width}:{height}:flags=lanczos,"
            f"fps={fps},format=yuv420p"
        )
        input_arguments = ["-i", str(source)]

    keyframe_interval = max(round(fps * keyframe_interval_seconds), 1)
    return [
        "-y",
        *input_arguments,
        "-vf",
        filter_chain,
        "-t",
        f"{duration_seconds:.6f}",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "24",
        "-g",
        str(keyframe_interval),
        "-keyint_min",
        str(keyframe_interval),
        "-sc_threshold",
        "0",
        "-movflags",
        "+faststart",
        str(output),
    ]


def _web_poster_arguments(
    source: Path,
    output: Path,
    *,
    width: int,
    height: int,
    focus_x: float,
) -> list[str]:
    arguments = ["-y"]
    if source.suffix.lower() in VIDEO_SUFFIXES:
        arguments.extend(["-ss", "0.1"])
    arguments.extend(
        [
            "-i",
            str(source),
            "-vf",
            (
                f"{_aspect_crop(width, height, focus_x=focus_x)},"
                f"scale={width}:{height}:flags=lanczos"
            ),
            "-frames:v",
            "1",
            "-c:v",
            "libwebp",
            "-q:v",
            "78",
            str(output),
        ]
    )
    return arguments


def prepare_web_background(
    source_path: str | Path,
    output_directory: str | Path,
    *,
    poster_source_path: str | Path | None = None,
    duration_seconds: float | None = None,
    prefix: str = "hero",
    fps: int = 24,
    keyframe_interval_seconds: float = 0.125,
    desktop_focus_x: float = 0.62,
    mobile_focus_x: float = 0.72,
) -> WebMediaBundle:
    source = _require_file(source_path, "网页背景媒体")
    source_is_image = source.suffix.lower() in IMAGE_SUFFIXES
    if not source_is_image and source.suffix.lower() not in VIDEO_SUFFIXES:
        raise WorkspaceOperationError(f"不支持的网页背景媒体格式：{source.suffix}")
    if not 0 <= desktop_focus_x <= 1 or not 0 <= mobile_focus_x <= 1:
        raise WorkspaceOperationError("构图焦点必须位于 0 到 1 之间")
    if fps <= 0:
        raise WorkspaceOperationError("网页背景帧率必须大于 0")

    if keyframe_interval_seconds <= 0:
        raise WorkspaceOperationError(
            "website background keyframe interval must be greater than zero"
        )

    if duration_seconds is None:
        if source_is_image:
            duration_seconds = 10.0
        else:
            duration_seconds = float(media_metadata(source).get("duration") or 0)
    if duration_seconds <= 0:
        raise WorkspaceOperationError("无法确定网页背景视频时长")

    poster_source = (
        _require_file(poster_source_path, "网页背景海报源")
        if poster_source_path
        else source
    )
    output = Path(output_directory).resolve()
    output.mkdir(parents=True, exist_ok=True)
    desktop = output / f"{prefix}-desktop.mp4"
    mobile = output / f"{prefix}-mobile.mp4"
    poster = output / f"{prefix}-poster.webp"

    _run_ffmpeg(
        _web_video_arguments(
            source,
            desktop,
            width=1280,
            height=720,
            duration_seconds=duration_seconds,
            fps=fps,
            keyframe_interval_seconds=keyframe_interval_seconds,
            focus_x=desktop_focus_x,
            source_is_image=source_is_image,
        )
    )
    _run_ffmpeg(
        _web_video_arguments(
            source,
            mobile,
            width=720,
            height=1280,
            duration_seconds=duration_seconds,
            fps=fps,
            keyframe_interval_seconds=keyframe_interval_seconds,
            focus_x=mobile_focus_x,
            source_is_image=source_is_image,
        )
    )
    _run_ffmpeg(
        _web_poster_arguments(
            poster_source,
            poster,
            width=1280,
            height=720,
            focus_x=desktop_focus_x,
        )
    )
    return WebMediaBundle(
        desktop_video=desktop,
        mobile_video=mobile,
        poster=poster,
        duration_seconds=duration_seconds,
    )


def media_metadata(path: str | Path) -> dict:
    source = _require_file(path, "媒体文件")
    try:
        import imageio_ffmpeg
    except ImportError as exc:
        raise WorkspaceOperationError("缺少 imageio-ffmpeg") from exc
    reader = imageio_ffmpeg.read_frames(str(source), pix_fmt="rgb24")
    try:
        return dict(next(reader))
    finally:
        reader.close()
