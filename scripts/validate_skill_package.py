from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "ai-animation-director"


REQUIRED_FILES = [
    ROOT / "README.md",
    ROOT / "README.zh-CN.md",
    ROOT / "LICENSE",
    ROOT / "SECURITY.md",
    ROOT / ".gitignore",
    ROOT / "docs/repository-metadata.md",
    ROOT / "docs/release-notes-v0.1.0.md",
    ROOT / "docs/improvement-backlog.md",
    ROOT / "docs/issue-seeds.md",
    ROOT / "scripts/create_github_repo.ps1",
    ROOT / "scripts/publish_to_github.ps1",
    SKILL / "SKILL.md",
    SKILL / "agents/openai.yaml",
    SKILL / "prompts/output_composer.md",
    SKILL / "prompts/quick_package_router.md",
    SKILL / "templates/jimeng-quick-package.md",
    SKILL / "references/workflow.md",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []

    for path in REQUIRED_FILES:
        if not path.is_file():
            failures.append(f"Missing file: {path.relative_to(ROOT)}")

    examples_dir = SKILL / "examples"
    if not examples_dir.is_dir():
        failures.append(f"Missing directory: {examples_dir.relative_to(ROOT)}")
        examples: list[Path] = []
    else:
        examples = sorted(examples_dir.glob("*.md"))

    if len(examples) < 3:
        failures.append("Expected at least 3 markdown examples.")

    for example in examples:
        text = read_text(example)
        if "jimeng" in example.name and "IMG-REF" not in text:
            failures.append(f"{example.name}: Jimeng example missing IMG-REF.")

        for match in re.finditer(r"VID-S(\d{2})", text):
            shot = match.group(1)
            required_image = f"`IMG-S{shot}`"
            if required_image not in text:
                failures.append(f"{example.name}: VID-S{shot} does not reference IMG-S{shot}.")

    prompts_only = SKILL / "examples/prompts-only-jimeng.md"
    if prompts_only.is_file():
        text = read_text(prompts_only)
        if "## 2." in text or "## 4." in text:
            failures.append(
                "prompts-only-jimeng.md should not include one-line setup or shot table sections."
            )

    outputs_dir = SKILL / "outputs"
    output_files = [
        path
        for path in outputs_dir.rglob("*")
        if path.is_file() and path.name != ".gitkeep"
    ]
    if output_files:
        failures.append(
            f"outputs/ contains generated files that should not be published: {len(output_files)}"
        )

    if failures:
        print("Skill package validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Skill package validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
