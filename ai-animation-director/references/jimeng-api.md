# Jimeng API Execution Reference

Use this reference before running or modifying `scripts/jimeng_execute.py`.

## Purpose

The prompt pipeline produces production-ready image and video prompts. The execution layer turns a prepared JSON manifest into provider calls, polls task status, downloads media, and records output paths.

This v1 execution layer is provider-adapter based because Jimeng public web features and exact API details may change. Fill in official Jimeng/Volcano-compatible endpoint details from the user's account console or official provider documentation before live execution.

## Credentials

Read credentials only from environment variables. Never store API keys, cookies, tokens, account passwords, or session data in Skill files.

Required for live execution:

- `JIMENG_ACCESS_KEY`
- `JIMENG_SECRET_KEY`
- `JIMENG_API_BASE`

Optional:

- `JIMENG_API_TOKEN`
- `JIMENG_SUBMIT_ENDPOINT`, default `/v1/tasks`
- `JIMENG_QUERY_ENDPOINT`, default `/v1/tasks/{task_id}`
- `JIMENG_IMAGE_MODEL`
- `JIMENG_VIDEO_MODEL`

Dry-run mode does not require credentials.

## CLI

```bash
python scripts/jimeng_execute.py --manifest outputs/project/manifest.json --out outputs/project --dry-run
python scripts/jimeng_execute.py --manifest outputs/project/manifest.json --out outputs/project
python scripts/jimeng_execute.py --manifest outputs/project/manifest.json --out outputs/project --only image
python scripts/jimeng_execute.py --manifest outputs/project/manifest.json --out outputs/project --only video
```

## Manifest Shape

The manifest root must contain `tasks`.

Task fields:

- `id`: stable unique task id.
- `type`: one of `image`, `video_text`, `video_image`, `video_first_last_frame`.
- `prompt`: copy-ready prompt.
- `negative_prompt`: optional avoid list.
- `input_images`: required for `video_image`; two images recommended for `video_first_last_frame`.
- `duration_hint`: human-readable intended duration.
- `aspect_ratio`: example `16:9`, `9:16`, `1:1`.
- `mode`: workflow hint, such as `text-to-image`, `image-to-video`, `first-last-frame`.
- `status`: local execution status.
- `output_path`: relative path under the output directory.
- `provider_task_id`: provider task id after submission.
- `notes`: production notes or fallback instructions.

Video tasks may reference image outputs produced by earlier image tasks in the same manifest. The script validates ordering: input images must already exist or be planned outputs from earlier tasks.

## Execution Flow

1. Validate manifest and output paths.
2. Dry-run prints planned calls and exits.
3. Live mode checks credentials.
4. Submit each selected task.
5. Poll provider status until success or failure.
6. Download the output asset.
7. Update the manifest after each successful task.

## Provider Adapter Notes

The script sends a generic JSON payload:

```json
{
  "type": "image",
  "prompt": "...",
  "negative_prompt": "...",
  "input_images": [],
  "duration_hint": "short shot",
  "aspect_ratio": "16:9",
  "mode": "text-to-image",
  "model": "optional model id"
}
```

If the official provider uses a different request shape, update only the provider adapter methods in `scripts/jimeng_execute.py`:

- `submit_task`
- `get_task`
- `download`
- `_headers`

Keep manifest fields stable so the prompt pipeline does not need to change.

## Safety

- Do not automate the Jimeng web UI in v1.
- Do not write outputs outside `outputs/`.
- Do not commit generated credentials or account data.
- Use `--dry-run` before live execution.
- Start with one image task and one short video task for integration testing.
