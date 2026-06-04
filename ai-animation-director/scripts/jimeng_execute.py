#!/usr/bin/env python3
"""
Execute a Jimeng-compatible AI animation production manifest.

This script intentionally keeps provider-specific endpoint paths and signing
minimal. Fill in the environment variables documented in references/jimeng-api.md
for a real Jimeng/Volcano-compatible provider.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


SUPPORTED_TASK_TYPES = {
    "image",
    "video_text",
    "video_image",
    "video_first_last_frame",
}
VIDEO_TASK_TYPES = {"video_text", "video_image", "video_first_last_frame"}
TERMINAL_SUCCESS = {"succeeded", "success", "completed", "done"}
TERMINAL_FAILURE = {"failed", "error", "cancelled", "canceled"}


class ManifestError(Exception):
    """Raised when a manifest is invalid or unsafe to execute."""


class ProviderError(Exception):
    """Raised when the provider call fails."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ManifestError(f"Manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"Manifest is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ManifestError("Manifest root must be a JSON object.")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def resolve_under(base: Path, candidate: str | None, default_name: str) -> Path:
    raw = candidate or default_name
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    resolved_base = base.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError as exc:
        raise ManifestError(
            f"Output path must stay under output directory: {resolved_path}"
        ) from exc
    return resolved_path


def task_filter(task: dict[str, Any], only: str | None) -> bool:
    if only is None:
        return True
    task_type = task.get("type")
    if only == "image":
        return task_type == "image"
    if only == "video":
        return task_type in VIDEO_TASK_TYPES
    return True


def validate_manifest(
    manifest: dict[str, Any], out_dir: Path, only: str | None = None
) -> list[dict[str, Any]]:
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ManifestError("Manifest must contain a non-empty 'tasks' array.")

    seen_ids: set[str] = set()
    planned_outputs: set[Path] = set()
    selected: list[dict[str, Any]] = []

    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ManifestError(f"Task at index {index} must be an object.")

        task_id = task.get("id")
        task_type = task.get("type")
        prompt = task.get("prompt")

        if not isinstance(task_id, str) or not task_id.strip():
            raise ManifestError(f"Task at index {index} is missing string 'id'.")
        if task_id in seen_ids:
            raise ManifestError(f"Duplicate task id: {task_id}")
        seen_ids.add(task_id)

        if task_type not in SUPPORTED_TASK_TYPES:
            raise ManifestError(
                f"Task {task_id} has unsupported type {task_type!r}. "
                f"Supported: {sorted(SUPPORTED_TASK_TYPES)}"
            )
        if not isinstance(prompt, str) or not prompt.strip():
            raise ManifestError(f"Task {task_id} is missing non-empty 'prompt'.")

        output_path = resolve_under(
            out_dir,
            task.get("output_path"),
            default_name=f"{task_id}.{'png' if task_type == 'image' else 'mp4'}",
        )
        task["_resolved_output_path"] = str(output_path)

        input_images = task.get("input_images", [])
        if input_images is None:
            input_images = []
        if not isinstance(input_images, list) or not all(
            isinstance(item, str) and item.strip() for item in input_images
        ):
            raise ManifestError(f"Task {task_id} 'input_images' must be a string list.")

        if task_type == "video_image" and len(input_images) < 1:
            raise ManifestError(f"Task {task_id} requires at least one input image.")
        if task_type == "video_first_last_frame" and len(input_images) < 2:
            raise ManifestError(
                f"Task {task_id} requires first-frame and last-frame input images."
            )

        for image_ref in input_images:
            image_path = Path(image_ref)
            if not image_path.is_absolute():
                image_path = out_dir / image_path
            resolved_image = image_path.resolve()
            if not resolved_image.exists() and resolved_image not in planned_outputs:
                raise ManifestError(
                    f"Task {task_id} references missing input image: {image_ref}. "
                    "It must exist already or be produced by an earlier image task."
                )

        planned_outputs.add(output_path.resolve())
        if task_filter(task, only):
            selected.append(task)

    if not selected:
        raise ManifestError(f"No tasks selected for --only {only!r}.")
    return selected


def require_credentials(dry_run: bool) -> dict[str, str]:
    if dry_run:
        return {}

    required = ["JIMENG_ACCESS_KEY", "JIMENG_SECRET_KEY", "JIMENG_API_BASE"]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise ProviderError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Set credentials in the environment; never store them in Skill files."
        )

    return {
        "access_key": os.environ["JIMENG_ACCESS_KEY"],
        "secret_key": os.environ["JIMENG_SECRET_KEY"],
        "api_base": os.environ["JIMENG_API_BASE"].rstrip("/"),
        "submit_endpoint": os.environ.get("JIMENG_SUBMIT_ENDPOINT", "/v1/tasks"),
        "query_endpoint": os.environ.get("JIMENG_QUERY_ENDPOINT", "/v1/tasks/{task_id}"),
        "image_model": os.environ.get("JIMENG_IMAGE_MODEL", ""),
        "video_model": os.environ.get("JIMENG_VIDEO_MODEL", ""),
    }


class JimengProvider:
    def __init__(self, config: dict[str, str], timeout: int) -> None:
        self.config = config
        self.timeout = timeout

    def _url(self, endpoint: str) -> str:
        return self.config["api_base"] + "/" + endpoint.lstrip("/")

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "X-Jimeng-Access-Key": self.config["access_key"],
            "X-Jimeng-Secret-Key": self.config["secret_key"],
        }
        token = os.environ.get("JIMENG_API_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _request(self, method: str, url: str, payload: dict[str, Any] | None = None) -> Any:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers=self._headers(),
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ProviderError(f"Provider HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise ProviderError(f"Provider network error: {exc}") from exc

        if not body:
            return {}
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return {"raw": body.decode("utf-8", errors="replace")}

    def submit_task(self, task: dict[str, Any]) -> str:
        task_type = task["type"]
        model = self.config["image_model"] if task_type == "image" else self.config["video_model"]
        payload = {
            "type": task_type,
            "prompt": task["prompt"],
            "negative_prompt": task.get("negative_prompt", ""),
            "input_images": task.get("input_images", []),
            "duration_hint": task.get("duration_hint"),
            "aspect_ratio": task.get("aspect_ratio"),
            "mode": task.get("mode"),
            "model": model or None,
            "metadata": {
                "manifest_task_id": task["id"],
                "notes": task.get("notes", ""),
            },
        }
        response = self._request("POST", self._url(self.config["submit_endpoint"]), payload)
        provider_task_id = (
            response.get("task_id")
            or response.get("id")
            or response.get("data", {}).get("task_id")
            or response.get("data", {}).get("id")
        )
        if not provider_task_id:
            raise ProviderError(f"Submit response did not include a task id: {response}")
        return str(provider_task_id)

    def get_task(self, provider_task_id: str) -> dict[str, Any]:
        endpoint = self.config["query_endpoint"].format(
            task_id=urllib.parse.quote(provider_task_id)
        )
        response = self._request("GET", self._url(endpoint))
        if not isinstance(response, dict):
            raise ProviderError(f"Unexpected task response: {response!r}")
        return response

    def download(self, url: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                output_path.write_bytes(response.read())
        except urllib.error.URLError as exc:
            raise ProviderError(f"Download failed for {url}: {exc}") from exc


def extract_status(response: dict[str, Any]) -> str:
    status = (
        response.get("status")
        or response.get("state")
        or response.get("data", {}).get("status")
        or response.get("data", {}).get("state")
        or "unknown"
    )
    return str(status).lower()


def extract_download_url(response: dict[str, Any]) -> str | None:
    candidates = [
        response.get("download_url"),
        response.get("output_url"),
        response.get("url"),
        response.get("data", {}).get("download_url"),
        response.get("data", {}).get("output_url"),
        response.get("data", {}).get("url"),
    ]
    outputs = response.get("outputs") or response.get("data", {}).get("outputs")
    if isinstance(outputs, list) and outputs:
        first = outputs[0]
        if isinstance(first, dict):
            candidates.extend([first.get("url"), first.get("download_url")])
        elif isinstance(first, str):
            candidates.append(first)
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.startswith(("http://", "https://")):
            return candidate
    return None


def execute_task(
    provider: JimengProvider,
    task: dict[str, Any],
    poll_seconds: int,
    max_polls: int,
) -> None:
    if task.get("status") == "succeeded" and task.get("output_path"):
        print(f"SKIP {task['id']}: already succeeded")
        return

    print(f"SUBMIT {task['id']} ({task['type']})")
    provider_task_id = provider.submit_task(task)
    task["provider_task_id"] = provider_task_id
    task["status"] = "submitted"

    last_response: dict[str, Any] = {}
    for attempt in range(1, max_polls + 1):
        time.sleep(poll_seconds)
        response = provider.get_task(provider_task_id)
        last_response = response
        status = extract_status(response)
        task["status"] = status
        print(f"POLL {task['id']} attempt {attempt}/{max_polls}: {status}")

        if status in TERMINAL_SUCCESS:
            download_url = extract_download_url(response)
            if not download_url:
                raise ProviderError(f"Task {task['id']} succeeded but no output URL was found.")
            output_path = Path(task["_resolved_output_path"])
            provider.download(download_url, output_path)
            task["output_path"] = str(output_path)
            task["status"] = "succeeded"
            print(f"DONE {task['id']}: {output_path}")
            return
        if status in TERMINAL_FAILURE:
            task["last_response"] = last_response
            raise ProviderError(f"Task {task['id']} failed: {response}")

    task["last_response"] = last_response
    raise ProviderError(f"Task {task['id']} did not finish after {max_polls} polls.")


def print_plan(tasks: list[dict[str, Any]]) -> None:
    print("Dry run: planned Jimeng-compatible tasks")
    for task in tasks:
        print(
            f"- {task['id']} [{task['type']}]: "
            f"mode={task.get('mode', '')} aspect={task.get('aspect_ratio', '')} "
            f"output={task['_resolved_output_path']}"
        )
        if task.get("input_images"):
            print(f"  input_images={', '.join(task['input_images'])}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Path to production manifest JSON.")
    parser.add_argument("--out", required=True, help="Output directory for generated assets.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print planned calls.")
    parser.add_argument("--only", choices=["image", "video"], help="Run only image or video tasks.")
    parser.add_argument("--poll-seconds", type=int, default=5, help="Seconds between polls.")
    parser.add_argument("--max-polls", type=int, default=120, help="Maximum poll attempts per task.")
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout in seconds.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    manifest_path = Path(args.manifest)
    out_dir = Path(args.out)

    try:
        manifest = load_json(manifest_path)
        tasks = validate_manifest(manifest, out_dir, args.only)

        if args.dry_run:
            print_plan(tasks)
            return 0

        config = require_credentials(dry_run=False)
        provider = JimengProvider(config, timeout=args.timeout)
        for task in tasks:
            execute_task(provider, task, args.poll_seconds, args.max_polls)
            write_json(manifest_path, manifest)
        write_json(manifest_path, manifest)
        return 0
    except (ManifestError, ProviderError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
