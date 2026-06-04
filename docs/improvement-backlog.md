# Improvement Backlog

This backlog converts the competitive analysis into concrete work items. It is ordered for a small open-source Skill project, not a full AI video platform.

## P0 - GitHub Launch Readiness

These items should be complete before announcing the repository widely.

### P0.1 Confirm Remote Repository

- Create or verify `baichou6320-cpu/ai-animation-director`.
- Push `main`.
- Confirm GitHub Actions runs `Validate Skill Package`.
- Add repository topics from `docs/repository-metadata.md`.

Acceptance:

- Repository URL is public or intentionally private.
- `git remote -v` points to the GitHub repository.
- Actions show a passing validation run.

### P0.2 Publish First Release

- Push tag `v0.1.0`.
- Use `docs/release-notes-v0.1.0.md` as release notes.
- State clearly that v0.1 is prompt-only with an experimental Jimeng-compatible adapter.

Acceptance:

- GitHub release exists.
- Release notes include boundaries and examples.

### P0.3 Remove Or Archive Local Scratch Output

- Decide whether `pixel_ai_animation_package_jimeng.md` should be deleted, moved to examples, or kept as local scratch.
- It is currently ignored by `.gitignore` and not part of the repository.

Acceptance:

- No untracked ignored scratch files remain if a fully clean local workspace is desired.

## P1 - Skill Quality

These items improve usefulness and reduce output drift.

### P1.1 Add More Final-Format Examples

Add examples for:

- Cyberpunk product ad, 15 seconds, 4 shots, Jimeng.
- Stop-motion toy short, 20 seconds, 5 shots.
- Documentary realism, 30 seconds, 4 shots.
- English prompt output.

Acceptance:

- Each example uses final user-facing format.
- Jimeng examples include `IMG-REF`, `IMG-Sxx`, and `VID-Sxx`.
- No example includes internal reasoning or `Project Packet`.

### P1.2 Add Static Checks For SKILL.md Size And Routing Terms

Extend validation to check:

- `SKILL.md` stays below a chosen size threshold.
- `quick_package_router.md` exists.
- `output_composer.md` contains `Prompts Only`, `Quick Mode`, and copy-block rules.

Acceptance:

- Validation fails when routing or output composition rules are accidentally removed.

### P1.3 Improve Platform Adapter Evidence

Document platform support levels:

- Generic natural-language adapter.
- Jimeng short-package adapter.
- Experimental Jimeng-compatible API adapter.
- Unknown/unverified parameters.

Acceptance:

- README and platform adapter do not imply verified API support where none exists.
- New platform requests must link official docs or mark assumptions.

## P2 - Productization

These items make the project easier to use beyond Codex.

### P2.1 Export Shot Tables

Add optional export templates for:

- Markdown shot table.
- JSON production manifest.
- CSV shot list.

Acceptance:

- Export schema is documented.
- Examples include at least one exported manifest.

### P2.2 Strengthen Execution Layer

Improve `scripts/jimeng_execute.py` after provider details are available:

- Separate provider config from generic manifest validation.
- Add no-network dry run fixtures.
- Add clear retry and failure states.

Acceptance:

- Dry run works without credentials.
- Live run is documented as provider-specific.

### P2.3 Add Cross-Platform Validation

Add a Python or Node validator mirroring the PowerShell script.

Acceptance:

- GitHub Actions can run validation on Linux and Windows.
- Local users without PowerShell can validate the package.

## P3 - Community And Presentation

These are useful after the first release is stable.

### P3.1 Add Social Preview

Create a simple preview image showing:

- Input idea.
- `IMG-REF`.
- `IMG-S01`.
- `VID-S01`.

Acceptance:

- GitHub social preview explains the project in one glance.

### P3.2 Add Demo GIF Or Screenshot

Show a before/after example in README.

Acceptance:

- README demonstrates copy-first workflow without overwhelming users.

## Current Strategic Choice

Do not compete with full AI video studios in v0.1. The project should stay focused on:

> Codex Skill for AI animation pre-production and Jimeng-ready prompt execution packages.

This positioning is narrower, easier to trust, and easier to maintain.
