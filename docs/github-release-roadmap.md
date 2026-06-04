# GitHub 发布路线图

## 目标

把当前 `ai-animation-director` 从本地 Skill 原型整理成可发布的 GitHub 项目。第一版不要承诺完整视频生成，而要稳定交付“AI 动画导演提示词 Skill + 即梦执行包模板”。

## v0.1 发布范围

包含：

- Codex Skill 主体：`ai-animation-director/SKILL.md`。
- Prompt pipeline：`prompts/`。
- 参考资料：`references/`。
- 即梦短包模板：`templates/jimeng-quick-package.md`。
- 验收样例：`examples/`。
- 实验性执行层：`scripts/jimeng_execute.py` 和 manifest 模板。

不承诺：

- 自动登录即梦网页。
- 保证即梦 API 可用。
- 真正生成图片、视频或音乐。
- 提供完整 Web UI。

## 必须补齐的仓库文件

- `README.md`
  - 项目一句话定位。
  - 适合谁用。
  - 3 个快速示例。
  - 安装方式。
  - Quick Mode / Standard Mode / Full Mode 说明。
  - 即梦 API 执行层的限制声明。
- `LICENSE`
  - 推荐 MIT，方便别人使用和贡献。
- `.gitignore`
  - 忽略 `ai-animation-director/outputs/**`，但保留 `.gitkeep`。
  - 忽略 `.env`、API key、临时媒体、Python cache。
- `CHANGELOG.md`
  - 从 `0.1.0` 开始记录。
- `CONTRIBUTING.md`
  - 如何新增风格、平台适配、验收样例。

## 发布前清理

- 删除或移动根目录的临时输出 `pixel_ai_animation_package_jimeng.md`。
- 清理 `ai-animation-director/outputs/smoke/` 里的假图片和 smoke manifest，或移到 `tests/fixtures/`。
- 确认没有 API key、cookie、session token、账号凭证。
- 确认 examples 只包含最终输出，不包含内部推理。

## 验证脚本建议

新增一个轻量校验脚本，第一版只做静态检查：

- 必须存在 `SKILL.md`。
- 必须存在 `agents/openai.yaml`。
- 必须存在 `prompts/output_composer.md` 和 `prompts/quick_package_router.md`。
- examples 中必须出现 `IMG-REF`。
- 每个 `VID-Sxx` 必须引用同编号 `IMG-Sxx`。
- `prompts-only-jimeng.md` 不应包含 `一句话设定` 和 `镜头表`。
- `outputs/` 不应包含要提交的媒体文件。

脚本可以先用 PowerShell 写，适合当前 Windows 工作区；后续再加 Python 跨平台版本。

## README 推荐结构

```markdown
# AI Animation Director

一句话：A Codex Skill that turns animation ideas into director-style, Jimeng-ready AI video prompt packages.

## Why
AI 视频失败常见原因：角色漂移、镜头太复杂、风格词过虚、提示词不能复用。

## What It Produces
- Quick Mode
- Prompts Only
- Standard Mode
- Full Mode

## Quick Start
安装 Skill，输入示例，复制输出到即梦。

## Examples
链接到 examples。

## Jimeng API Layer
说明实验性、凭证只读环境变量、不提交密钥。

## Roadmap
平台适配、校验器、manifest 导出、更多样例。
```

## 建议里程碑

### Milestone 1: GitHub-ready package

- 补 `README.md`、`LICENSE`、`.gitignore`、`CHANGELOG.md`。
- 清理 outputs 和临时产物。
- 增加静态校验脚本。

### Milestone 2: Skill quality

- 瘦身 `SKILL.md`。
- 把真实影视流程迁移到 `references/workflow.md`。
- 增加 5-8 个不同类型 examples。
- 增加英文输出样例。

### Milestone 3: Execution layer

- 明确 Jimeng-compatible provider 配置。
- manifest 校验更严格。
- 输出下载和失败重试可验证。
- README 中给出 dry-run 和 live-run 示例。

## 首次发布建议

发布 `v0.1.0`，定位为：

> Prompt-only Skill with experimental Jimeng execution adapter.

这样既能展示项目价值，又不会过度承诺自动生成视频能力。
