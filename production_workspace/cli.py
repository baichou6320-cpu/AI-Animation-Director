from __future__ import annotations

import argparse
import json
import sys

from .importer import ManifestImportError, import_manifest
from .intake_service import (
    answer_intake,
    approve_project_blueprint,
    build_project_blueprint,
    plan_intake_questions,
    request_blueprint_revision,
)
from .media import (
    assemble_project,
    build_animatic,
    pixel_finish_project,
    prepare_web_background,
)
from .models import AttemptStatus, FAILURE_TAG_LABELS, ProductionPhase, utc_now
from .preproduction_models import (
    InteractionPolicy,
    IntakeState,
    ProjectBlueprint,
    ProjectConstraints,
    TextSafeZone,
    WebBackgroundInteraction,
    WebBackgroundSpec,
)
from .preproduction_storage import (
    StructuredProjectError,
    create_draft_project,
    load_structured_artifact,
    load_structured_manifest,
    save_structured_artifact,
    save_structured_manifest,
    validate_structured_project,
    write_json_schemas,
)
from .service import (
    WorkspaceOperationError,
    add_attempt,
    approve_animatic,
    approve_final,
    approve_sample,
    export_delivery,
    project_rows,
    readiness_warnings,
    review_attempt,
    select_attempt,
)
from .storage import ProjectStorageError, load_project, save_project


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="animation-workspace",
        description="AI Animation Director 本地生产工作台",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft_parser = subparsers.add_parser(
        "init-draft",
        help="Create a structured pre-production project draft",
    )
    draft_parser.add_argument("--projects-root", required=True)
    draft_parser.add_argument("--title", required=True)
    draft_parser.add_argument("--raw-input", required=True)
    draft_parser.add_argument("--project-id")
    draft_parser.add_argument("--platform")
    draft_parser.add_argument("--aspect-ratio", default="")
    draft_parser.add_argument("--duration", type=float)
    draft_parser.add_argument("--shots", type=int)
    draft_parser.add_argument(
        "--interaction-policy",
        choices=[policy.value for policy in InteractionPolicy],
        default=InteractionPolicy.SINGLE_CONFIRM.value,
    )

    validate_structured_parser = subparsers.add_parser(
        "validate-structured",
        help="Validate every JSON file in a structured project",
    )
    validate_structured_parser.add_argument("project")

    schema_parser = subparsers.add_parser(
        "export-schemas",
        help="Export the structured project JSON Schemas",
    )
    schema_parser.add_argument("--output", required=True)

    intake_plan_parser = subparsers.add_parser(
        "plan-intake",
        help="Plan the next 1-3 unanswered intake questions",
    )
    intake_plan_parser.add_argument("project")
    intake_plan_parser.add_argument("--limit", type=int, default=3)

    intake_answer_parser = subparsers.add_parser(
        "answer-intake",
        help="Save structured intake answers as field=value pairs",
    )
    intake_answer_parser.add_argument("project")
    intake_answer_parser.add_argument("--answer", action="append", required=True)

    blueprint_parser = subparsers.add_parser(
        "build-blueprint",
        help="Build the human-readable project blueprint confirmation card",
    )
    blueprint_parser.add_argument("project")
    blueprint_parser.add_argument("--understanding", required=True)
    blueprint_parser.add_argument("--story-direction", required=True)
    blueprint_parser.add_argument("--ending-direction", default="")
    blueprint_parser.add_argument("--style-direction", required=True)
    blueprint_parser.add_argument("--color-lighting", default="")
    blueprint_parser.add_argument("--camera-direction", required=True)
    blueprint_parser.add_argument("--assumption", action="append", default=[])
    blueprint_parser.add_argument("--editable", action="append", default=[])

    approve_blueprint_parser = subparsers.add_parser(
        "approve-blueprint",
        help="Approve the project blueprint and open the style stage",
    )
    approve_blueprint_parser.add_argument("project")
    approve_blueprint_parser.add_argument("--bypass", action="store_true")

    revise_blueprint_parser = subparsers.add_parser(
        "revise-blueprint",
        help="Request a blueprint-only revision",
    )
    revise_blueprint_parser.add_argument("project")

    import_parser = subparsers.add_parser("import", help="导入制作 manifest")
    import_parser.add_argument("manifest")
    import_parser.add_argument("--output", required=True)

    summary_parser = subparsers.add_parser("summary", help="查看镜头生产状态")
    summary_parser.add_argument("project")

    attempt_parser = subparsers.add_parser("add-attempt", help="记录一次生成尝试")
    attempt_parser.add_argument("project")
    attempt_parser.add_argument("shot_id")
    attempt_parser.add_argument("--provider", required=True)
    attempt_parser.add_argument("--model", default="")
    attempt_parser.add_argument("--prompt", required=True)
    attempt_parser.add_argument(
        "--phase",
        choices=[phase.value for phase in ProductionPhase],
        default=ProductionPhase.VIDEO.value,
    )
    attempt_parser.add_argument(
        "--status",
        choices=[status.value for status in AttemptStatus],
        default=AttemptStatus.PENDING.value,
    )
    attempt_parser.add_argument("--asset", action="append", default=[])
    attempt_parser.add_argument(
        "--failure",
        action="append",
        default=[],
        choices=sorted(FAILURE_TAG_LABELS),
    )
    attempt_parser.add_argument("--notes", default="")
    attempt_parser.add_argument("--score", action="append", default=[])
    attempt_parser.add_argument("--decision-reason", default="")

    select_parser = subparsers.add_parser("select", help="选择镜头最终版本")
    select_parser.add_argument("project")
    select_parser.add_argument("shot_id")
    select_parser.add_argument("attempt_id")

    review_parser = subparsers.add_parser("review-attempt", help="审核一次生成尝试")
    review_parser.add_argument("project")
    review_parser.add_argument("shot_id")
    review_parser.add_argument("attempt_id")
    review_parser.add_argument("--score", action="append", required=True)
    review_parser.add_argument("--decision-reason", required=True)
    review_parser.add_argument(
        "--status",
        choices=[status.value for status in AttemptStatus],
        default=AttemptStatus.PENDING.value,
    )

    storyboard_parser = subparsers.add_parser(
        "set-storyboard", help="登记动态分镜画面"
    )
    storyboard_parser.add_argument("project")
    storyboard_parser.add_argument("shot_id")
    storyboard_parser.add_argument("image")
    storyboard_parser.add_argument("--audio-cue", default="")

    animatic_parser = subparsers.add_parser(
        "build-animatic", help="根据分镜图片和时长生成动态分镜"
    )
    animatic_parser.add_argument("project")
    animatic_parser.add_argument("--output", required=True)
    animatic_parser.add_argument("--audio")

    approve_animatic_parser = subparsers.add_parser(
        "approve-animatic", help="批准动态分镜并开放关键帧生产"
    )
    approve_animatic_parser.add_argument("project")

    approve_sample_parser = subparsers.add_parser(
        "approve-sample", help="批准代表性样片并开放批量视频生产"
    )
    approve_sample_parser.add_argument("project")

    pixel_parser = subparsers.add_parser(
        "pixel-finish", help="统一像素帧率、调色板、分辨率和放大方式"
    )
    pixel_parser.add_argument("project")
    pixel_parser.add_argument("--output-directory", required=True)
    pixel_parser.add_argument("--palette-source")
    pixel_parser.add_argument("--shot", action="append", default=[])

    assemble_parser = subparsers.add_parser(
        "assemble", help="拼接已批准镜头并生成最终母版"
    )
    assemble_parser.add_argument("project")
    assemble_parser.add_argument("--output", required=True)
    assemble_parser.add_argument("--audio")

    web_media_parser = subparsers.add_parser(
        "prepare-web-background",
        help="生成可滚动定位的桌面/移动网页背景视频与海报",
    )
    web_media_parser.add_argument("source")
    web_media_parser.add_argument("--output-directory", required=True)
    web_media_parser.add_argument("--poster-source")
    web_media_parser.add_argument("--duration", type=float)
    web_media_parser.add_argument("--prefix", default="hero")
    web_media_parser.add_argument(
        "--keyframe-interval",
        type=float,
        default=0.125,
        help="Seconds between scrub-friendly video keyframes",
    )
    web_media_parser.add_argument("--desktop-focus-x", type=float, default=0.62)
    web_media_parser.add_argument("--mobile-focus-x", type=float, default=0.72)

    web_spec_parser = subparsers.add_parser(
        "set-web-background",
        help="保存网站背景视频的结构化交付契约",
    )
    web_spec_parser.add_argument("project")
    web_spec_parser.add_argument(
        "--interaction",
        choices=[item.value for item in WebBackgroundInteraction],
        default=WebBackgroundInteraction.SCROLL_SCRUB.value,
    )
    web_spec_parser.add_argument("--duration", type=float, required=True)
    web_spec_parser.add_argument(
        "--text-safe-zone",
        choices=[item.value for item in TextSafeZone],
        default=TextSafeZone.LEFT_CENTER.value,
    )
    web_spec_parser.add_argument("--allowed-motion", action="append", default=[])
    web_spec_parser.add_argument("--locked-element", action="append", default=[])
    web_spec_parser.add_argument(
        "--camera-motion",
        default="single_continuous_slow_push",
    )
    web_spec_parser.add_argument("--source-asset", default="")
    web_spec_parser.add_argument("--desktop-asset", default="")
    web_spec_parser.add_argument("--mobile-asset", default="")
    web_spec_parser.add_argument("--poster-asset", default="")
    web_spec_parser.add_argument("--public-release-ready", action="store_true")

    approve_final_parser = subparsers.add_parser(
        "approve-final", help="记录最终成片评分并批准交付"
    )
    approve_final_parser.add_argument("project")
    approve_final_parser.add_argument("--score", action="append", required=True)
    approve_final_parser.add_argument("--review-note", required=True)

    export_parser = subparsers.add_parser("export", help="导出剪辑交付包")
    export_parser.add_argument("project")
    export_parser.add_argument("--output", required=True)

    web_parser = subparsers.add_parser("web", help="启动 Gradio 本地界面")
    web_parser.add_argument("--server-name", default="127.0.0.1")
    web_parser.add_argument("--port", type=int, default=7860)
    return parser


def _parse_scores(values: list[str]) -> dict[str, int]:
    scores: dict[str, int] = {}
    for value in values:
        name, separator, raw_score = value.partition("=")
        if not separator or not name.strip():
            raise WorkspaceOperationError(f"评分格式应为 name=1..5：{value}")
        try:
            score = int(raw_score)
        except ValueError as exc:
            raise WorkspaceOperationError(f"评分必须是整数：{value}") from exc
        if not 1 <= score <= 5:
            raise WorkspaceOperationError(f"评分必须在 1-5 之间：{value}")
        scores[name.strip()] = score
    return scores


def _parse_field_values(values: list[str]) -> dict[str, object]:
    parsed: dict[str, object] = {}
    for value in values:
        name, separator, raw_value = value.partition("=")
        if not separator or not name.strip():
            raise StructuredProjectError(
                f"Intake answer must use field=value format: {value}"
            )
        try:
            parsed_value = json.loads(raw_value)
        except json.JSONDecodeError:
            parsed_value = raw_value
        parsed[name.strip()] = parsed_value
    return parsed


def _print_summary(project_path: str) -> None:
    project = load_project(project_path)
    print(f"{project.title} | {len(project.shots)} 个镜头")
    for row in project_rows(project):
        print(
            f"- {row[0]} {row[1]} | 尝试 {row[3]} 次 | "
            f"{row[5]}{f' #{row[4]}' if row[4] else ''}"
        )
    warnings = readiness_warnings(project)
    if warnings:
        print("交付检查：")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("交付检查：已就绪")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "init-draft":
            constraints = ProjectConstraints(
                platform=args.platform or "jimeng",
                aspect_ratio=args.aspect_ratio,
                duration_seconds=args.duration,
                shot_count=args.shots,
            )
            extracted_fields = {
                key: value
                for key, value in {
                    "platform": args.platform,
                    "aspect_ratio": args.aspect_ratio,
                    "duration_seconds": args.duration,
                    "shot_count": args.shots,
                }.items()
                if value not in {None, ""}
            }
            project_root = create_draft_project(
                args.projects_root,
                title=args.title,
                raw_input=args.raw_input,
                project_id=args.project_id,
                extracted_fields=extracted_fields,
                constraints=constraints,
                interaction_policy=InteractionPolicy(args.interaction_policy),
            )
            print(f"Structured draft created: {project_root}")
        elif args.command == "validate-structured":
            manifest = validate_structured_project(args.project)
            print(
                json.dumps(
                    {
                        "project_id": manifest.project_id,
                        "status": manifest.status,
                        "current_stage": manifest.current_stage,
                        "valid": True,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "export-schemas":
            written = write_json_schemas(args.output)
            print(f"Exported {len(written)} JSON Schemas to {args.output}")
        elif args.command == "plan-intake":
            questions = plan_intake_questions(args.project, limit=args.limit)
            print(
                json.dumps(
                    [question.model_dump(mode="json") for question in questions],
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "answer-intake":
            intake = answer_intake(args.project, _parse_field_values(args.answer))
            print(
                json.dumps(
                    {
                        "status": intake.status,
                        "qa_round": intake.qa_round,
                        "missing_required": intake.missing_required,
                        "assumptions": intake.assumptions,
                        "next_action": intake.next_action,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "build-blueprint":
            manifest = load_structured_manifest(args.project)
            intake = load_structured_artifact(args.project, manifest.files.intake)
            if not isinstance(intake, IntakeState):
                raise StructuredProjectError("input/intake.json has the wrong type")
            blueprint = ProjectBlueprint(
                one_sentence_understanding=args.understanding,
                structured_summary=manifest.constraints.model_dump(mode="python"),
                recommended_story_direction=args.story_direction,
                ending_direction=args.ending_direction,
                style_direction=args.style_direction,
                color_lighting_direction=args.color_lighting,
                camera_direction=args.camera_direction,
                assumptions=[
                    f"{key}={value}" for key, value in intake.assumptions.items()
                ]
                + args.assumption,
                editable_fields=args.editable,
            )
            output = build_project_blueprint(args.project, blueprint)
            print(f"Project blueprint created: {output}")
        elif args.command == "approve-blueprint":
            manifest = approve_project_blueprint(args.project, bypass=args.bypass)
            print(
                json.dumps(
                    {
                        "concept_approval": manifest.approvals.concept_approval,
                        "current_stage": manifest.current_stage,
                        "next_action": manifest.next_action,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "revise-blueprint":
            manifest = request_blueprint_revision(args.project)
            print(
                json.dumps(
                    {
                        "concept_approval": manifest.approvals.concept_approval,
                        "next_action": manifest.next_action,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "import":
            project = import_manifest(args.manifest)
            saved = save_project(project, args.output)
            print(f"已导入 {len(project.shots)} 个镜头：{saved}")
        elif args.command == "summary":
            _print_summary(args.project)
        elif args.command == "add-attempt":
            project = load_project(args.project)
            attempt = add_attempt(
                project,
                args.shot_id,
                args.provider,
                args.prompt,
                model=args.model,
                status=AttemptStatus(args.status),
                asset_paths=args.asset,
                failure_tags=args.failure,
                notes=args.notes,
                phase=ProductionPhase(args.phase),
                quality_scores=_parse_scores(args.score),
                decision_reason=args.decision_reason,
            )
            save_project(project, args.project)
            print(
                json.dumps(
                    attempt.model_dump(mode="json"), ensure_ascii=False, indent=2
                )
            )
        elif args.command == "select":
            project = load_project(args.project)
            attempt = select_attempt(project, args.shot_id, args.attempt_id)
            save_project(project, args.project)
            print(f"已选择 {args.shot_id} 的第 {attempt.attempt} 次结果")
        elif args.command == "review-attempt":
            project = load_project(args.project)
            attempt = review_attempt(
                project,
                args.shot_id,
                args.attempt_id,
                _parse_scores(args.score),
                args.decision_reason,
                status=AttemptStatus(args.status),
            )
            save_project(project, args.project)
            print(f"已审核 {args.shot_id} 第 {attempt.attempt} 次生成")
        elif args.command == "set-storyboard":
            project = load_project(args.project)
            shot = project.find_shot(args.shot_id)
            shot.storyboard_image_path = args.image
            shot.audio_cue = args.audio_cue
            save_project(project, args.project)
            print(f"已登记 {args.shot_id} 动态分镜画面")
        elif args.command == "build-animatic":
            project = load_project(args.project)
            output = build_animatic(project, args.output, temporary_audio_path=args.audio)
            save_project(project, args.project)
            print(f"动态分镜已生成：{output}")
        elif args.command == "approve-animatic":
            project = load_project(args.project)
            approve_animatic(project)
            save_project(project, args.project)
            print("动态分镜已批准，可以进入正式关键帧生产")
        elif args.command == "approve-sample":
            project = load_project(args.project)
            approve_sample(project)
            save_project(project, args.project)
            print("代表性样片已批准，可以生成其余镜头")
        elif args.command == "pixel-finish":
            project = load_project(args.project)
            attempts = pixel_finish_project(
                project,
                args.output_directory,
                palette_source=args.palette_source,
                shot_ids=args.shot or None,
            )
            save_project(project, args.project)
            print(f"已生成 {len(attempts)} 个待审核像素成片镜头")
        elif args.command == "assemble":
            project = load_project(args.project)
            output = assemble_project(project, args.output, audio_path=args.audio)
            save_project(project, args.project)
            print(f"最终母版候选已生成：{output}")
        elif args.command == "prepare-web-background":
            bundle = prepare_web_background(
                args.source,
                args.output_directory,
                poster_source_path=args.poster_source,
                duration_seconds=args.duration,
                prefix=args.prefix,
                keyframe_interval_seconds=args.keyframe_interval,
                desktop_focus_x=args.desktop_focus_x,
                mobile_focus_x=args.mobile_focus_x,
            )
            print(
                json.dumps(
                    bundle.as_dict(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "set-web-background":
            manifest = load_structured_manifest(args.project)
            manifest.constraints.delivery_profile = "website_background"
            manifest.constraints.duration_seconds = args.duration
            manifest.constraints.deliverable = "website_background_bundle"
            manifest.next_action = "integrate_website_background"
            manifest.updated_at = utc_now()
            spec = WebBackgroundSpec(
                project_id=manifest.project_id,
                status="approved" if args.public_release_ready else "draft",
                interaction=WebBackgroundInteraction(args.interaction),
                duration_seconds=args.duration,
                text_safe_zone=TextSafeZone(args.text_safe_zone),
                allowed_motion=args.allowed_motion,
                locked_elements=args.locked_element,
                camera_motion=args.camera_motion,
                source_asset=args.source_asset,
                desktop_asset=args.desktop_asset,
                mobile_asset=args.mobile_asset,
                poster_asset=args.poster_asset,
                public_release_ready=args.public_release_ready,
            )
            save_structured_manifest(args.project, manifest)
            save_structured_artifact(
                args.project,
                manifest.files.web_background,
                spec,
            )
            print(json.dumps(spec.model_dump(mode="json"), ensure_ascii=False, indent=2))
        elif args.command == "approve-final":
            project = load_project(args.project)
            approve_final(project, _parse_scores(args.score), args.review_note)
            save_project(project, args.project)
            print("最终母版已通过成片验收")
        elif args.command == "export":
            project = load_project(args.project)
            report = export_delivery(project, args.output)
            print(f"交付包已生成：{report.output_directory}")
        elif args.command == "web":
            from .app import launch

            launch(server_name=args.server_name, port=args.port)
        return 0
    except (
        ManifestImportError,
        ProjectStorageError,
        StructuredProjectError,
        WorkspaceOperationError,
    ) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
