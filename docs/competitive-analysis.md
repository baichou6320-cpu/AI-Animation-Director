# AI Animation Director 竞品分析与项目差距

## 当前项目定位

`ai-animation-director` 现在是一个 Codex Skill 原型，核心能力是把动画想法拆成短片制作流程，并输出即梦友好的生图/视频提示词。它的优势在“导演 + 编剧 + 分镜 + 角色一致性 + 即梦执行包”的文本工作流，而不是完整的视频生成应用。

当前已具备：

- `SKILL.md` 主入口和多阶段 prompt pipeline。
- 面向即梦短片的 `Quick Mode`、`Prompts Only` 和复制块编号规则。
- 角色/场景圣经、分镜、图像提示词、视频提示词、平台适配、声音建议等模块。
- 即梦 API 执行层占位脚本和 manifest 模板。
- 3 个最终输出格式验收样例。

当前不适合直接作为成熟 GitHub 项目发布，因为缺少项目包装、安装说明、许可证、验证方式和清晰的对外定位。

## 相关项目

| 项目 | 类型 | 主要能力 | 对我们的启发 |
| --- | --- | --- | --- |
| [rich5000/seedance-prompt-guide](https://github.com/rich5000/seedance-prompt-guide) | 即梦/Seedance prompt skill | 有 README、安装方式、验证安装、核心公式、场景模板、MIT License | GitHub 发布包装很完整；我们的 Skill 需要同等级 README、安装和验证说明。 |
| [dseditor/AI-storyboard-generator](https://github.com/dseditor/AI-storyboard-generator) | Web storyboard app | React + Gemini + ComfyUI，支持多种 storyboard 模式、镜头数量、图像/视频配置 | 用户体验强，有 UI 和配置入口；我们的优势不是 UI，而是更轻的 Skill 工作流。 |
| [0xsline/StoryGen-Atelier](https://github.com/0xsline/StoryGen-Atelier) | Storyboard + video app | Gemini 生成脚本/画面，Veo 生成过渡视频，ffmpeg 拼接，日志和图库管理 | 它证明“故事板到视频”项目需要日志、图库、导出和示例；我们的 API 层目前还只是占位。 |
| [vericontext/vibeframe](https://github.com/vericontext/vibeframe) | CLI-first video workflow | 从 brief 到 storyboard/design/render，强调 JSON、dry run、cost gates、报告和可修复命令 | 如果要做执行层，必须有 dry run、机器可读报告、成本/失败保护；当前脚本还不够产品化。 |
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | Agentic video production system | 面向 AI coding assistant 的完整视频生产系统，包含多 pipeline、多工具和质量控制 | 不应和它拼“完整视频工作室”；我们的切入点应是“AI 动画前期与提示词导演 Skill”。 |

## 我们的差异化机会

- 比通用 prompt guide 更强：不仅写单条提示词，还覆盖故事、导演、角色一致性、镜头拆解和失败修正。
- 比完整视频应用更轻：不要求用户安装前后端、ComfyUI、Veo 或 ffmpeg，适合作为 Codex Skill 直接使用。
- 比普通 storyboard 工具更面向 AI 视频生成：每个镜头都保留首帧、图生视频提示词和失败降级方案。
- 中文和即梦优先：对国内创作者更友好，尤其适合 10-30 秒短视频创作。

## 当前主要缺点

### 1. GitHub 项目包装不足

- 根目录没有 `README.md`。
- 没有 `LICENSE`。
- 没有 `.gitignore`，`outputs/` 和生成媒体容易误提交。
- 没有贡献说明、版本说明、路线图和安装验证说明。
- 当前目录本身不是 git 仓库，无法直接发布。

### 2. 对外定位还不够锋利

现在容易被理解成“又一个 AI 视频生成器”，但实际不是。更准确的定位应该是：

> A Codex Skill for AI animation pre-production and Jimeng-ready prompt execution packages.

中文定位：

> 面向 AI 动画短片的导演型提示词 Skill：把一句想法变成即梦可复制执行包。

### 3. `SKILL.md` 仍然偏长

`SKILL.md` 超过 26KB，作为 Skill 入口偏重。虽然已经把很多内容拆到 `prompts/` 和 `references/`，但真实影视流程、Project Packet 字段和模块地图仍然很长。后续应继续把细节下沉到 references，让入口更像调度规则。

### 4. 执行层可信度不足

`scripts/jimeng_execute.py` 是好的方向，但当前即梦 API 细节仍是 provider placeholder。发布时必须非常明确：

- v1 默认只生成文本提示词。
- API 执行层是实验性/适配器结构。
- 不保证可直接调用即梦官方接口。
- 不收集、不保存用户凭证。

### 5. 缺少自动验收

目前只有人工可读 examples，没有脚本检查：

- Quick Mode 是否只输出指定镜头数。
- `VID-Sxx` 是否引用对应 `IMG-Sxx`。
- Prompts Only 是否省略镜头表和一句话设定。
- 文件结构是否符合 Skill 发布规范。

### 6. 示例还不能变成宣传资产

已有 examples 是好基础，但 GitHub 首页需要更短的“Before / After”展示：

- 输入一句话。
- 输出一张即梦执行包截图或 Markdown 片段。
- 显示复制块编号。
- 说明 3 步生成流程。

## 建议方向

### 推荐项目形态

不要做成“AI 视频平台”或“完整视频编辑器”。第一版应该做成：

> 一个可安装的 Codex Skill，用于 AI 动画短片前期制作和即梦提示词执行包生成。

GitHub 项目名可以保留 `ai-animation-director`。

### 推荐卖点

- From idea to shot-ready prompts.
- Director-style workflow, copy-ready Jimeng prompts.
- Character and scene consistency anchors.
- Quick Mode for 10-30 second shorts.
- Full Mode for production handoff.

### 推荐近期优先级

1. 补齐 GitHub 外层文件：`README.md`、`LICENSE`、`.gitignore`、`CHANGELOG.md`。
2. 清理不应发布的生成产物：根目录临时输出、`outputs/smoke/` 内产物。
3. 增加 `scripts/validate_skill_package.ps1` 或 Python 校验脚本。
4. 把 `SKILL.md` 再瘦身，把长说明迁移到 `references/workflow.md`。
5. 在 README 中明确 v1 不直接生成视频，避免用户误解。

## 结论

当前项目的内核有价值，但发布前需要从“工作区原型”变成“可安装、可验证、可理解的开源 Skill”。竞品最值得学习的不是提示词内容本身，而是它们的项目包装、安装路径、验证方式、示例和可信边界。
