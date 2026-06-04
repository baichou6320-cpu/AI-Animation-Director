# AI Animation Director

AI Animation Director 是一个 Codex Skill，用导演、编剧、分镜和提示词工程的方式，把一句动画想法变成可复制到即梦的短片执行包。

> 第一版重点是“生成可用提示词和制作包”，不是直接生成图片、视频或音乐。

## 解决什么问题

AI 视频短片常见失败点通常不是没有提示词，而是：

- 角色和场景容易漂移。
- 镜头动作写得太复杂，模型生成不了。
- 风格描述太虚，结果不可控。
- 生图提示词和视频提示词脱节。
- 输出文档太长，用户不知道先复制哪一条。

本 Skill 的思路是：内部按真实动画短片制作流程思考，外部默认输出轻量、可复制、可试错的即梦执行包。

## 输出模式

- `Prompts Only`：只输出全局锚点、生图提示词、视频提示词和失败修正。
- `Quick Mode`：默认模式，适合 5-30 秒、3-6 镜头的即梦短片。
- `Standard Mode`：适合 30-90 秒短片，保留简短项目说明和完整镜头提示词。
- `Full Mode`：用户明确要求完整制作包、详细方案或团队交接时才使用。

即梦短片会使用稳定复制块编号：

- `IMG-REF`：角色/场景参考图。
- `IMG-S01`：第 1 个镜头首帧。
- `VID-S01`：第 1 个镜头视频提示词，使用 `IMG-S01`。

## 快速开始

1. 把 `ai-animation-director/` 复制到 Codex skills 目录。

   Windows 示例：

   ```powershell
   Copy-Item -Recurse .\ai-animation-director "$env:USERPROFILE\.codex\skills\ai-animation-director"
   ```

2. 在 Codex 中使用：

   ```text
   用 ai-animation-director 生成一个像素风动画，10 秒，3 个镜头，用即梦。
   ```

3. 按输出顺序复制：

   - 先复制 `IMG-REF` 生成参考图。
   - 再复制 `IMG-S01`、`IMG-S02`、`IMG-S03` 生成首帧。
   - 最后用对应首帧复制 `VID-S01`、`VID-S02`、`VID-S03` 做图生视频。

## 示例

- [10 秒像素风即梦执行包](ai-animation-director/examples/pixel-10s-3shots-jimeng.md)
- [30 秒国风水墨即梦执行包](ai-animation-director/examples/ink-30s-3shots-jimeng.md)
- [只要即梦提示词](ai-animation-director/examples/prompts-only-jimeng.md)

## 项目结构

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

- `SKILL.md`：Skill 入口和调度规则。
- `prompts/`：分阶段提示词模块。
- `references/`：按需读取的风格、镜头语言、工作流和检查清单。
- `templates/`：即梦执行包和 manifest 模板。
- `examples/`：最终输出格式样例。
- `scripts/`：实验性即梦兼容执行层。

## 即梦 API 层说明

`scripts/jimeng_execute.py` 是实验性执行层。v0.1 的稳定能力是生成提示词和制作包，不承诺直接自动生成图片/视频。

安全边界：

- 凭证只从环境变量读取。
- 不要提交 API key、cookie、session token 或账号密码。
- 即梦/火山兼容接口的 endpoint、签名规则和模型 ID 需要用户提供官方控制台或文档信息。
- v0.1 不默认做网页 UI 自动化。

## 验证

运行静态校验：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_skill_package.ps1
```

跨平台校验：

```bash
python scripts/validate_skill_package.py
```

期望输出：

```text
Skill package validation passed.
```

创建空 GitHub 仓库后，可以用脚本发布：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish_to_github.ps1
```

如果你有具备创建仓库权限的 `GITHUB_TOKEN`，也可以先运行 `scripts/create_github_repo.ps1` 创建空仓库。脚本只读取环境变量，不会保存 token。

## 发布文档

- [竞品分析与项目差距](docs/competitive-analysis.md)
- [GitHub 发布路线图](docs/github-release-roadmap.md)
- [发布检查清单](docs/release-checklist.md)
- [发布到 GitHub 操作步骤](docs/publish-to-github.md)
- [优先级改进 backlog](docs/improvement-backlog.md)

## 许可证

MIT。见 [LICENSE](LICENSE)。
