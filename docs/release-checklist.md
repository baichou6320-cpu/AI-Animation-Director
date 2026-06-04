# GitHub Release Checklist

Use this before publishing the repository or creating a release tag.

## Repository Basics

- [ ] Repository has a clear name: `ai-animation-director`.
- [ ] `README.md` explains what the project does and what it does not do.
- [ ] `README.zh-CN.md` is present for Chinese users.
- [ ] `LICENSE` is present.
- [ ] `.gitignore` excludes secrets, generated media, and execution outputs.
- [ ] `CHANGELOG.md` has an unreleased `0.1.0` entry.
- [ ] `CONTRIBUTING.md` explains how to add examples and platform support.
- [ ] GitHub Actions validation workflow is present.
- [ ] GitHub issue and PR templates are present.
- [ ] Repository metadata and release notes drafts are present in `docs/`.

## Skill Package

- [ ] `ai-animation-director/SKILL.md` has valid frontmatter.
- [ ] `ai-animation-director/agents/openai.yaml` matches the compact execution package positioning.
- [ ] Prompt modules exist for routing and output composition.
- [ ] Long workflow details live in `references/workflow.md`, not only in `SKILL.md`.
- [ ] Examples use final output format and do not include internal reasoning.

## Safety

- [ ] No API keys, cookies, session tokens, or account credentials.
- [ ] `ai-animation-director/outputs/` contains only `.gitkeep`.
- [ ] Jimeng API execution is described as experimental.
- [ ] README does not promise automatic video generation in v0.1.

## Validation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_skill_package.ps1
```

Expected:

```text
Skill package validation passed.
```

## First GitHub Release

- [ ] Initialize git repository if needed.
- [ ] Review ignored local scratch files.
- [ ] Commit as `v0.1.0-prep` or similar.
- [ ] Create GitHub repository.
- [ ] Follow `docs/publish-to-github.md`.
- [ ] Push default branch.
- [ ] Confirm the validation workflow passes on GitHub.
- [ ] Create first release only after README, examples, and validation are stable.
