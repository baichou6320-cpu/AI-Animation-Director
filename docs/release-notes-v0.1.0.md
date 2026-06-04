# v0.1.0 - Prompt-only Skill with experimental Jimeng adapter

Initial release of AI Animation Director.

## Highlights

- Codex Skill for AI animation pre-production.
- Quick Mode for 5-30 second Jimeng-ready short video execution packages.
- Prompts Only mode for copy-first image/video prompts.
- Standard and Full modes for longer short-film planning and team handoff.
- Modular prompt pipeline for intake, director treatment, story, character/scene bible, shot list, image prompts, video prompts, platform routing, and output composition.
- Copy-block IDs such as `IMG-REF`, `IMG-S01`, and `VID-S01`.
- Examples for pixel style, Chinese ink style, and prompts-only output.
- Experimental Jimeng-compatible manifest execution layer.

## Included Examples

- `ai-animation-director/examples/pixel-10s-3shots-jimeng.md`
- `ai-animation-director/examples/ink-30s-3shots-jimeng.md`
- `ai-animation-director/examples/prompts-only-jimeng.md`

## Validation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_skill_package.ps1
```

Expected:

```text
Skill package validation passed.
```

## Boundaries

- This release does not generate images, videos, or music by itself.
- Jimeng API execution is experimental and requires user-provided provider details.
- No API keys, cookies, session tokens, or credentials should be committed.

## Recommended Next Work

- Add more examples for ads, product videos, documentary style, stop motion, and English prompts.
- Continue slimming `SKILL.md`.
- Improve manifest validation and provider adapters.
- Add export formats for shot tables and production manifests.
