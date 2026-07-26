from __future__ import annotations

from .importer import import_manifest
from .media import assemble_project, build_animatic, pixel_finish_project
from .models import AttemptStatus, FAILURE_TAG_LABELS, ProductionPhase
from .service import (
    add_attempt,
    approve_animatic,
    approve_final,
    approve_sample,
    export_delivery,
    readiness_warnings,
    select_attempt,
)
from .storage import load_project, save_project


TABLE_HEADERS = [
    "镜头",
    "说明",
    "时长",
    "生成次数",
    "关键帧",
    "视频",
    "像素成片",
    "状态",
]


def _phase_rows(project) -> list[list]:
    rows: list[list] = []
    for shot in sorted(project.shots, key=lambda item: item.order):
        keyframe = shot.selected_attempt_for(ProductionPhase.KEYFRAME)
        video = shot.selected_attempt_for(ProductionPhase.VIDEO)
        pixel = shot.selected_attempt_for(ProductionPhase.PIXEL_FINISH)
        if project.pipeline_mode == "legacy":
            status = "已选定" if shot.selected_attempt() else "待完成"
        else:
            status = "已完成" if keyframe and video and pixel else "进行中"
        rows.append(
            [
                shot.id,
                shot.title,
                shot.duration_seconds or "",
                len(shot.attempts),
                keyframe.attempt if keyframe else "",
                video.attempt if video else "",
                pixel.attempt if pixel else "",
                status,
            ]
        )
    return rows


def _project_status(project) -> str:
    warnings = readiness_warnings(project)
    if project.pipeline_mode == "pixel_short":
        keyframes = sum(
            shot.selected_attempt_for(ProductionPhase.KEYFRAME) is not None
            for shot in project.shots
        )
        videos = sum(
            shot.selected_attempt_for(ProductionPhase.VIDEO) is not None
            for shot in project.shots
        )
        pixels = sum(
            shot.selected_attempt_for(ProductionPhase.PIXEL_FINISH) is not None
            for shot in project.shots
        )
        progress = (
            f"关键帧 **{keyframes}/{len(project.shots)}**，"
            f"视频 **{videos}/{len(project.shots)}**，"
            f"像素成片 **{pixels}/{len(project.shots)}**。"
        )
    else:
        ready_count = len(project.shots) - sum(
            1 for shot in project.shots if shot.selected_attempt() is None
        )
        progress = f"已选定 **{ready_count}/{len(project.shots)}** 个镜头。"
    lines = [
        f"## {project.title}",
        progress,
    ]
    if warnings:
        lines.append("\n**当前不能交付：**")
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("\n所有镜头已就绪，可以导出交付包。")
    return "\n".join(lines)


def _load_ui(project_path: str):
    import gradio as gr

    try:
        project = load_project(project_path)
        shot_ids = [shot.id for shot in sorted(project.shots, key=lambda item: item.order)]
        first_shot = shot_ids[0] if shot_ids else None
        prompt = project.find_shot(first_shot).video_prompt if first_shot else ""
        return (
            _project_status(project),
            _phase_rows(project),
            gr.update(choices=shot_ids, value=first_shot),
            prompt,
            gr.update(choices=[], value=None),
            "",
        )
    except Exception as exc:
        return (
            f"**加载失败：** {exc}",
            [],
            gr.update(choices=[], value=None),
            "",
            gr.update(choices=[], value=None),
            str(exc),
        )


def _import_ui(manifest_path: str, project_path: str):
    try:
        project = import_manifest(manifest_path)
        save_project(project, project_path)
        return f"已导入 {len(project.shots)} 个镜头并保存到 `{project_path}`"
    except Exception as exc:
        return f"导入失败：{exc}"


def _shot_ui(project_path: str, shot_id: str):
    import gradio as gr

    try:
        project = load_project(project_path)
        shot = project.find_shot(shot_id)
        choices = [
            (
                f"{attempt.phase} | 第 {attempt.attempt} 次 | {attempt.provider} | "
                f"{attempt.status} | {len(attempt.assets)} 个素材",
                attempt.id,
            )
            for attempt in shot.attempts
        ]
        return (
            shot.video_prompt or shot.image_prompt,
            gr.update(choices=choices, value=shot.selected_attempt_id),
            "",
        )
    except Exception as exc:
        return "", gr.update(choices=[], value=None), str(exc)


def _record_attempt_ui(
    project_path: str,
    shot_id: str,
    provider: str,
    model: str,
    prompt: str,
    status: str,
    phase: str,
    asset_paths: str,
    failure_labels: list[str],
    score_text: str,
    decision_reason: str,
    notes: str,
):
    import gradio as gr

    try:
        project = load_project(project_path)
        label_to_tag = {label: tag for tag, label in FAILURE_TAG_LABELS.items()}
        attempt = add_attempt(
            project,
            shot_id,
            provider,
            prompt,
            model=model,
            status=AttemptStatus(status),
            phase=ProductionPhase(phase),
            asset_paths=[
                line.strip()
                for line in asset_paths.splitlines()
                if line.strip()
            ],
            failure_tags=[label_to_tag[label] for label in failure_labels],
            quality_scores=_parse_scores(score_text),
            decision_reason=decision_reason,
            notes=notes,
        )
        save_project(project, project_path)
        shot = project.find_shot(shot_id)
        choices = [
            (
                f"{item.phase} | 第 {item.attempt} 次 | {item.provider} | "
                f"{item.status} | {len(item.assets)} 个素材",
                item.id,
            )
            for item in shot.attempts
        ]
        return (
            _project_status(project),
            _phase_rows(project),
            gr.update(choices=choices, value=attempt.id),
            f"已记录 {shot_id} 的第 {attempt.attempt} 次生成。",
        )
    except Exception as exc:
        return "", [], gr.update(), f"记录失败：{exc}"


def _select_attempt_ui(project_path: str, shot_id: str, attempt_id: str):
    try:
        project = load_project(project_path)
        attempt = select_attempt(project, shot_id, attempt_id)
        save_project(project, project_path)
        return (
            _project_status(project),
            _phase_rows(project),
            f"已把 {shot_id} 第 {attempt.attempt} 次生成设为最终版本。",
        )
    except Exception as exc:
        return "", [], f"选择失败：{exc}"


def _export_ui(project_path: str, output_path: str):
    try:
        project = load_project(project_path)
        report = export_delivery(project, output_path)
        return (
            f"交付包已生成：`{report.output_directory}`\n\n"
            "包含素材、镜头表、项目快照、交付报告和小红书发布检查表。"
        )
    except Exception as exc:
        return f"导出失败：{exc}"


def _parse_scores(value: str) -> dict[str, int]:
    if not value.strip():
        return {}
    scores: dict[str, int] = {}
    for raw_line in value.replace(",", "\n").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        name, separator, raw_score = line.partition("=")
        if not separator:
            raise ValueError(f"评分格式应为 name=1..5：{line}")
        score = int(raw_score.strip())
        if not 1 <= score <= 5:
            raise ValueError(f"评分必须在 1-5 之间：{line}")
        scores[name.strip()] = score
    return scores


def _build_animatic_ui(project_path: str, output_path: str, audio_path: str):
    try:
        project = load_project(project_path)
        output = build_animatic(
            project,
            output_path,
            temporary_audio_path=audio_path.strip() or None,
        )
        save_project(project, project_path)
        return f"动态分镜已生成：`{output}`。请观看并审核后再批准。"
    except Exception as exc:
        return f"动态分镜生成失败：{exc}"


def _approve_animatic_ui(project_path: str):
    try:
        project = load_project(project_path)
        approve_animatic(project)
        save_project(project, project_path)
        return "动态分镜已批准，可以开始正式关键帧。"
    except Exception as exc:
        return f"批准失败：{exc}"


def _approve_sample_ui(project_path: str):
    try:
        project = load_project(project_path)
        approve_sample(project)
        save_project(project, project_path)
        return "代表性样片已批准，可以生成其余镜头。"
    except Exception as exc:
        return f"批准失败：{exc}"


def _pixel_finish_ui(
    project_path: str, output_directory: str, palette_source: str
):
    try:
        project = load_project(project_path)
        attempts = pixel_finish_project(
            project,
            output_directory,
            palette_source=palette_source.strip() or None,
        )
        save_project(project, project_path)
        return f"已生成 {len(attempts)} 个待审核像素成片镜头。"
    except Exception as exc:
        return f"像素后期失败：{exc}"


def _assemble_ui(project_path: str, output_path: str, audio_path: str):
    try:
        project = load_project(project_path)
        output = assemble_project(
            project,
            output_path,
            audio_path=audio_path.strip() or None,
        )
        save_project(project, project_path)
        return f"最终母版候选已生成：`{output}`。请完成四项评分。"
    except Exception as exc:
        return f"母版拼接失败：{exc}"


def _approve_final_ui(project_path: str, score_text: str, review_note: str):
    try:
        project = load_project(project_path)
        approve_final(project, _parse_scores(score_text), review_note)
        save_project(project, project_path)
        return "最终母版已通过验收，可以导出交付包。"
    except Exception as exc:
        return f"最终验收失败：{exc}"


def build_app():
    try:
        import gradio as gr
    except ImportError as exc:
        raise RuntimeError(
            '未安装 Web 依赖，请运行：pip install -e ".[web]"'
        ) from exc

    with gr.Blocks(title="AI 动画生产工作台") as app:
        gr.Markdown(
            "# AI 动画生产工作台\n"
            "把 Animation Director 的分镜生产包，推进为可追踪、可交付的成片素材。"
        )

        with gr.Tab("1. 导入项目"):
            manifest_path = gr.Textbox(
                label="Animation Director manifest 路径",
                placeholder="C:\\projects\\animation\\manifest.json",
            )
            imported_project_path = gr.Textbox(
                label="工作台项目文件",
                value="workspace-data/my-animation.project.json",
            )
            import_button = gr.Button("导入 manifest", variant="primary")
            import_result = gr.Markdown()
            import_button.click(
                _import_ui,
                [manifest_path, imported_project_path],
                import_result,
            )

        with gr.Tab("2. 镜头生产"):
            project_path = gr.Textbox(
                label="工作台项目文件",
                value="workspace-data/my-animation.project.json",
            )
            load_button = gr.Button("加载项目", variant="primary")
            status_markdown = gr.Markdown()
            shot_table = gr.Dataframe(
                headers=TABLE_HEADERS,
                datatype=[
                    "str",
                    "str",
                    "number",
                    "number",
                    "number",
                    "number",
                    "number",
                    "str",
                ],
                interactive=False,
                label="镜头看板",
            )
            shot_id = gr.Dropdown(label="当前镜头", choices=[])
            prompt = gr.Textbox(label="本次实际使用的提示词", lines=8)

            with gr.Row():
                provider = gr.Textbox(label="生成平台", value="jimeng")
                model = gr.Textbox(label="模型/模式", placeholder="可选")
                production_phase = gr.Dropdown(
                    label="制作阶段",
                    choices=[phase.value for phase in ProductionPhase],
                    value=ProductionPhase.VIDEO.value,
                )
                attempt_status = gr.Dropdown(
                    label="结果状态",
                    choices=[status.value for status in AttemptStatus],
                    value=AttemptStatus.PENDING.value,
                )

            asset_paths = gr.Textbox(
                label="素材路径",
                lines=3,
                placeholder="每行一个图片、视频或音频文件路径",
            )
            failure_labels = gr.CheckboxGroup(
                label="失败原因",
                choices=list(FAILURE_TAG_LABELS.values()),
            )
            score_text = gr.Textbox(
                label="阶段评分",
                lines=4,
                placeholder=(
                    "每行 name=1..5，例如：\n"
                    "motion_completion=4\n"
                    "temporal_stability=4"
                ),
            )
            decision_reason = gr.Textbox(
                label="选用/返修理由",
                lines=2,
                placeholder="像素短片的通过版本必须记录理由",
            )
            notes = gr.Textbox(label="本次记录", lines=3)
            record_button = gr.Button("记录本次生成")

            attempt_id = gr.Dropdown(label="生成版本", choices=[])
            select_button = gr.Button("设为最终版本", variant="primary")
            operation_result = gr.Markdown()

            load_button.click(
                _load_ui,
                project_path,
                [
                    status_markdown,
                    shot_table,
                    shot_id,
                    prompt,
                    attempt_id,
                    operation_result,
                ],
            )
            shot_id.change(
                _shot_ui,
                [project_path, shot_id],
                [prompt, attempt_id, operation_result],
            )
            record_button.click(
                _record_attempt_ui,
                [
                    project_path,
                    shot_id,
                    provider,
                    model,
                    prompt,
                    attempt_status,
                    production_phase,
                    asset_paths,
                    failure_labels,
                    score_text,
                    decision_reason,
                    notes,
                ],
                [status_markdown, shot_table, attempt_id, operation_result],
            )
            select_button.click(
                _select_attempt_ui,
                [project_path, shot_id, attempt_id],
                [status_markdown, shot_table, operation_result],
            )

        with gr.Tab("3. 动态分镜与成片"):
            finish_project_path = gr.Textbox(
                label="工作台项目文件",
                value="workspace-data/my-animation.project.json",
            )
            with gr.Group():
                gr.Markdown("### 动态分镜")
                animatic_output = gr.Textbox(
                    label="animatic 输出",
                    value="workspace-data/outputs/animatic.mp4",
                )
                animatic_audio = gr.Textbox(label="临时声音路径（可选）")
                with gr.Row():
                    animatic_button = gr.Button("构建动态分镜", variant="primary")
                    approve_animatic_button = gr.Button("批准动态分镜")

            with gr.Group():
                gr.Markdown("### 样片与像素后期")
                approve_sample_button = gr.Button("批准代表性样片")
                pixel_output = gr.Textbox(
                    label="像素成片目录",
                    value="workspace-data/outputs/pixel",
                )
                palette_source = gr.Textbox(
                    label="REF-HERO 路径",
                    placeholder="assets/REF-HERO.png",
                )
                pixel_button = gr.Button("生成待审核像素成片")

            with gr.Group():
                gr.Markdown("### 拼接与最终验收")
                master_output = gr.Textbox(
                    label="最终母版路径",
                    value="workspace-data/outputs/final-master.mp4",
                )
                final_audio = gr.Textbox(label="最终混音路径（可选）")
                assemble_button = gr.Button("拼接最终母版")
                final_scores = gr.Textbox(
                    label="最终四项评分",
                    lines=4,
                    value=(
                        "story_clarity=4\n"
                        "pacing=4\n"
                        "visual_consistency=4\n"
                        "sound=4"
                    ),
                )
                final_review_note = gr.Textbox(
                    label="最终审核结论",
                    placeholder="说明为什么达到交付标准",
                )
                approve_final_button = gr.Button("批准最终母版", variant="primary")

            finish_result = gr.Markdown()
            animatic_button.click(
                _build_animatic_ui,
                [finish_project_path, animatic_output, animatic_audio],
                finish_result,
            )
            approve_animatic_button.click(
                _approve_animatic_ui,
                finish_project_path,
                finish_result,
            )
            approve_sample_button.click(
                _approve_sample_ui,
                finish_project_path,
                finish_result,
            )
            pixel_button.click(
                _pixel_finish_ui,
                [finish_project_path, pixel_output, palette_source],
                finish_result,
            )
            assemble_button.click(
                _assemble_ui,
                [finish_project_path, master_output, final_audio],
                finish_result,
            )
            approve_final_button.click(
                _approve_final_ui,
                [finish_project_path, final_scores, final_review_note],
                finish_result,
            )

        with gr.Tab("4. 导出交付"):
            export_project_path = gr.Textbox(
                label="工作台项目文件",
                value="workspace-data/my-animation.project.json",
            )
            delivery_path = gr.Textbox(
                label="新的空交付目录",
                value="workspace-data/delivery/my-animation",
            )
            export_button = gr.Button("生成剪辑交付包", variant="primary")
            export_result = gr.Markdown()
            export_button.click(
                _export_ui,
                [export_project_path, delivery_path],
                export_result,
            )
    return app


def launch(server_name: str = "127.0.0.1", port: int = 7860) -> None:
    app = build_app()
    app.launch(server_name=server_name, server_port=port, inbrowser=True)
