# AI Animation Director

A Codex Skill that turns animation ideas into director-style, Jimeng-ready AI video prompt packages.

中文定位：面向 AI 动画短片的导演型提示词 Skill，把一句想法变成可复制到即梦的生图、图生视频和分镜执行包。

## Why

AI 视频短片常见失败点不是“没有提示词”，而是：

- 角色和场景漂移。
- 镜头动作太复杂。
- 风格描述太虚。
- 生图提示词和视频提示词脱节。
- 用户拿到长文档后不知道先复制哪一条。

This Skill solves that by using an internal animation production workflow, then compressing the result into a copy-first execution package.

## What It Produces

- `Prompts Only`: only anchors, image prompts, video prompts, and fixes.
- `Quick Mode`: default for 5-30 second Jimeng shorts with 3-6 shots.
- `Standard Mode`: for 30-90 second short-film packages.
- `Full Mode`: for complete production packages and team handoff.

For Jimeng-style short videos, output blocks use stable IDs:

- `IMG-REF`: reference image prompt.
- `IMG-S01`: shot 1 keyframe prompt.
- `VID-S01`: shot 1 video prompt, using `IMG-S01`.

## Quick Start

1. Copy `ai-animation-director/` into your Codex skills directory.

   Windows example:

   ```powershell
   Copy-Item -Recurse .\ai-animation-director "$env:USERPROFILE\.codex\skills\ai-animation-director"
   ```

2. Ask Codex to use the Skill:

   ```text
   用 ai-animation-director 生成一个像素风动画，10 秒，3 个镜头，用即梦。
   ```

3. Copy the generated `IMG-*` prompts into Jimeng image generation, then use the corresponding `VID-*` prompts for image-to-video generation.

## Examples

- [10 秒像素风即梦执行包](ai-animation-director/examples/pixel-10s-3shots-jimeng.md)
- [30 秒国风水墨即梦执行包](ai-animation-director/examples/ink-30s-3shots-jimeng.md)
- [只要即梦提示词](ai-animation-director/examples/prompts-only-jimeng.md)

## Project Structure

```text
ai-animation-director/
  SKILL.md
  agents/
  prompts/
  references/
  templates/
  examples/
  scripts/
```

Research and release planning live in `docs/`.

Detailed production workflow references live in `ai-animation-director/references/` and are loaded only when needed, keeping the Skill entrypoint lighter.

## Jimeng API Layer

The script layer is experimental. In v0.1, the reliable default is prompt generation, not automatic media generation.

- Credentials must come from environment variables.
- Do not commit API keys, cookies, session tokens, or account credentials.
- Exact provider endpoints and signing rules may need official Jimeng/Volcano account documentation.
- Web UI automation is not the default v0.1 path.

## Validate

Run the static package check:

```powershell
.\scripts\validate_skill_package.ps1
```

This checks required Skill files, examples, copy-block references, and publish-risk files.

The same check is wired into GitHub Actions via `.github/workflows/validate.yml`.

## Roadmap

- More examples for ads, product videos, documentary style, stop motion, and English prompts.
- Smaller `SKILL.md` with more details moved into references.
- Stronger manifest validation.
- Provider adapters for Jimeng-compatible APIs.
- Optional export formats for shot tables and production manifests.

## License

MIT. See [LICENSE](LICENSE).
