---
name: ai-animation-director
description: Create practical AI animation short-film prompt packages and production plans. Use when Codex needs to turn an animation idea, script, character, visual style, storyboard, or ad concept into an executable AI animation workflow with director treatment, script, shot list, image-generation prompts, Jimeng Smart Canvas asset and keyframe workflows, video-generation prompts, consistency anchors, music/sound notes, risks, QA checklist, and compact execution packages for 5-180 second animated shorts across general AI image/video tools or platform-specific variants.
---

# AI Animation Director

本 Skill 用于把动画创意、故事、脚本、角色设定、广告概念或视觉风格要求，转化为一套可执行的 AI 动画短片制作包。默认面向 5-180 秒动画短片，默认输出中文，默认先生成通用 AI 生图/生视频提示词，再按用户指定的平台做适配。

核心目标不是写单条提示词，而是模拟一个资深动画导演、制片 PM、AI 视频工作流工程师的协作流程：先明确意图，再建立导演方案和一致性锚点，最后生成分镜、关键帧提示词、视频运动提示词、声音建议和风险清单。内部可以完整思考，但默认给用户轻量、可复制、可执行的结果。

## 使用边界

- 使用本 Skill 编写制作方案、提示词、分镜表、脚本、导演阐述、角色/场景圣经、平台适配文本和质检清单。
- 不直接生成图片、视频或音乐，除非用户另外明确要求调用对应工具。
- 不复刻受版权保护的角色、影视作品、具体专有画面或在世艺术家的个人风格；将参考转换为通用的色彩、材质、镜头、节奏、光影和情绪特征。
- 配乐和声音始终低于故事、镜头、画面和提示词优先级，只给方向、节奏、乐器、氛围和关键音效。

## 内部制作路径

默认交付不要展开真实影视流程。需要完整制作包、团队交接、导演解释，或需要确认“从想法到成片”的内部路径时，按需读取 `references/workflow.md`。

## 跨模块交接机制

不要把整个制作流程当成一次性提示词。每个 prompt 模块都必须像真实影视岗位一样接收上一环节的交接物，完成自己的专业判断，再把更新后的信息传给下一环节。

统一使用 `Project Packet` 作为跨模块交接物。它不是最终给用户看的完整文案，而是内部制作状态摘要。每个模块都应读取已有 packet，保留上游决策，只补充或修正自己负责的字段。

`Project Packet` 至少包含：

- `source_input`: 用户原始输入和已知硬约束。
- `assumptions`: 为了继续推进而采用的默认值。
- `open_questions`: 需要用户确认但不阻塞第一版制作的问题。
- `project_brief`: 标题、logline、片长、画幅、受众、用途、平台、交付物。
- `creative_direction`: 主题、情绪曲线、类型、风格方向、参考转译原则。
- `story_state`: 故事结构、角色目标、冲突、结尾、旁白/台词方向。
- `director_notes`: 导演意图、镜头语言、表演方式、色彩/光影、剪辑节奏。
- `design_bible`: 角色、场景、道具、世界观、一致性锚点、负向约束。
- `shot_plan`: 镜头数量、镜头目的、时长、景别、运动、转场、难度。
- `prompt_assets`: 生图提示词、视频提示词、平台适配版本、首尾帧建议。
- `canvas_plan`: 即梦画布策略、素材、画布、区域、操作、导出与视频交接关系。
- `execution_state`: 当前制作进度、已完成资产/镜头、失败步骤和下一动作。
- `revision_state`: 用户改稿请求、受影响编号、保留编号、失效编号和下一动作。
- `sound_plan`: 配乐、环境声、音效、旁白节奏。
- `risk_register`: 风格漂移、角色漂移、复杂动作、平台限制、修正方案。
- `handoff_notes`: 当前模块给下一个模块的明确要求。

交接规则：

- 上游决定是约束，不是灵感素材。下游模块不得随意推翻用户硬约束、导演意图、角色锚点或故事结尾。
- 如果下游发现上游决策不可执行，先在 `risk_register` 记录问题，再给出最小修正，不要重写整个项目。
- 每个模块输出时都要包含“给下一环节的交接说明”，例如导演给编剧的叙事要求、编剧给分镜的关键情绪点、分镜给视频提示词模块的运动限制。
- 当用户只请求局部产出时，也要先构造一个最小 `Project Packet`，避免局部提示词失去上下文。

## 项目结构职责

本 Skill 采用“入口调度 + prompt pipeline + reference 知识库”的结构。

- `SKILL.md`: 总调度文件。判断用户需求、选择 prompt 模块、规定执行顺序、约束输出格式。
- `prompts/`: 可组合的工作流提示词模块。每个模块负责一个制作阶段。
- `references/`: 可按需读取的知识库，包括风格、镜头语言、提示词模板、平台差异和质检表。
- `templates/`: 稳定输出模板，如 `jimeng-canvas-package.md`、`jimeng-continue-card.md`、`project-state.json`、`failure-diagnosis-card.md`。
- `examples/`: 验收样例，使用最终输出格式，不包含内部推理，如像素风即梦短包、国风水墨即梦短包、只要提示词模式和续接/失败/改稿样例。
- `tools/`: 后续可加入轻量校验脚本，用于检查制作包是否缺少关键部分。
- `scripts/`: 可选执行层，用于把已审核的 manifest 提交给即梦兼容 API、轮询任务并下载结果。
- `outputs/`: 保存生成用 manifest、图片、视频和执行结果，不把媒体产物写回 prompt 文件。

## Execution Layer / 执行层

提示词管线永远是源头。执行层只负责执行已经生成并审核过的 manifest，不负责重新创作故事、导演方案、分镜或提示词。

当用户要求“直接生成图片/视频”“调用即梦 API”“批量提交镜头”“下载生成结果”时：

1. 先完成 prompt pipeline，得到即梦适配后的生图和视频提示词。
2. 将任务整理为 `templates/jimeng-production-manifest.json` 兼容结构。
3. 在运行或修改脚本前读取 `references/jimeng-api.md`。
4. 使用 `scripts/jimeng_execute.py --dry-run` 验证 manifest。
5. 只有在用户已提供合法即梦/火山兼容 API 凭证和 endpoint 时，才执行真实提交。

凭证规则：

- 只从环境变量读取 `JIMENG_ACCESS_KEY`、`JIMENG_SECRET_KEY`、`JIMENG_API_BASE` 等配置。
- 不把 API key、cookie、session token、账号密码写入 Skill、manifest、日志或输出文件。
- 即梦网页 UI 自动化不是 v1 默认方案；优先使用 API/provider adapter。

执行脚本入口：

```bash
python scripts/jimeng_execute.py --manifest outputs/project/manifest.json --out outputs/project --dry-run
python scripts/jimeng_execute.py --manifest outputs/project/manifest.json --out outputs/project
```

## Prompt 模块地图

以下模块位于 `prompts/`。当对应文件存在时，按需读取对应模块；当文件尚未存在时，遵循本节定义的模块职责执行。

### `prompts/intake.md`

用途：需求识别与创意澄清。

使用时机：

- 用户只给一句想法，例如“做一个小机器人在雨夜寻找星星的动画”。
- 用户给了风格或平台，但缺少片长、角色、受众、画幅、结尾或用途。
- 用户需求互相冲突，需要先整理约束。

输出目标：

- 提取已知信息。
- 补齐合理默认值。
- 列出 3-5 个关键澄清问题，但不要阻塞生成第一版方案。

### `prompts/project_brief_builder.md`

用途：生成项目简报。

使用时机：

- 几乎所有完整制作包都需要使用。
- 用户需要把创意变成可管理的项目。
- 用户强调 PM、制片、交付、团队协作或执行计划。

输出目标：

- 标题、片长、画幅、受众、类型、主题、核心情绪、平台、交付物。
- 明确默认假设和制作限制。

### `prompts/director_treatment_builder.md`

用途：生成导演阐述和视听风格方案。

使用时机：

- 用户指定影视风格、动画风格、导演感、镜头语言或情绪基调。
- 用户希望结果更像“短片”而不是“素材提示词”。
- 用户要求“高级感”“电影感”“统一风格”。

输出目标：

- 导演意图、情绪曲线、视觉基调、摄影策略、色彩/光影、表演方式、剪辑节奏。
- 将风格参考转换为可执行的通用视觉特征。

### `prompts/story_builder.md`

用途：生成或改编故事脚本。

使用时机：

- 用户只有概念，需要发展成起承转合。
- 用户已有剧本，需要压缩、改编成 30-180 秒动画。
- 用户需要旁白、台词、动作线或情绪线。

输出目标：

- 三幕式或起承转合结构。
- 分段脚本、动作描述、旁白/台词、情绪变化、结尾回收。
- 保留用户指定的核心剧情，不擅自推翻。

### `prompts/character_scene_bible_builder.md`

用途：建立角色与场景一致性圣经。

使用时机：

- 项目有重复出现的角色、地点、道具、品牌物或世界观。
- 用户担心 AI 生图/视频角色漂移。
- 用户需要系列化、连续镜头或多镜头一致性。

输出目标：

- 角色锚点：年龄、体型、脸部、发型、服装、材质、颜色、标志物、表情习惯、动作习惯。
- 场景锚点：地点、时代、天气、空间布局、主道具、光源方向、色彩、材质。
- 负向约束：禁止变化的服装、年龄、比例、道具、场景结构等。

### `prompts/shotlist_builder.md`

用途：生成分镜和镜头表。

使用时机：

- 用户需要完整短片制作包。
- 用户要求“镜头”“分镜”“storyboard”“shot list”“导演镜头”。
- 已有故事，需要转成可拍、可生成的视频镜头。

输出目标：

- 每个镜头包含：编号、时长、镜头目的、画面、景别、机位、摄影机运动、主体动作、情绪、光影、转场、声音、难度、修正建议。
- 控制镜头数量：30-90 秒通常 6-10 镜，90-180 秒通常 10-18 镜。
- 高难度镜头必须给降级方案。

### `prompts/image_prompt_builder.md`

用途：生成 AI 生图/关键帧提示词。

使用时机：

- 用户要生成关键帧、角色图、场景图、分镜图、首帧/尾帧。
- 需要先用图片锁定风格，再进入视频生成。
- 用户指定 Midjourney、Stable Diffusion、DALL-E、即梦生图或其他图像工具。

输出目标：

- 每个关键帧包含正向提示词、负向提示词、风格锚点、角色锚点、场景锚点、构图锚点、一致性备注。
- 优先确保角色、服装、场景、构图稳定，再追求风格修饰。

### `prompts/video_prompt_builder.md`

用途：生成 AI 视频提示词。

使用时机：

- 用户要用可灵、即梦、海螺、Runway、Pika、Veo、Luma 等视频模型。
- 分镜已经明确，需要写每镜头的运动提示词。
- 用户要求镜头运动、角色动作、动态画面或视频生成。

输出目标：

- 每个镜头包含主体运动、摄影机运动、时间变化、物理约束、连续性要求、避免项、失败降级方案。
- 每个镜头只保留一个主要主体动作和一个主要摄影机动作；复杂动作建议拆镜。

### `prompts/canvas_workflow_builder.md`

用途：把即梦静态素材和分镜组织为可人工执行的智能画布计划。

使用时机：

- 目标平台是即梦，且交付模式为 Quick、Standard 或 Full。
- 用户提到智能画布、多图融合、局部重绘、扩图、消除、抠图或已有素材组合。
- 需要通过角色、场景和道具资产提高多镜头一致性。

输出目标：

- 生成 `canvas_plan`，包含 `CV-*` 画布、`Z-*` 区域、`ASSET-*` 素材、`CV-OP-*` 操作和 `IMG-*` 导出。
- 复用用户已有素材；没有素材时先准备 `IMG-REF`。
- 为每个镜头导出 `IMG-Sxx`，再交给同编号 `VID-Sxx`。
- 不自动操作网页，不依赖实时按钮名称或参数。

### `prompts/sound_builder.md`

用途：生成配乐与声音方向。

使用时机：

- 完整制作包的最后阶段。
- 用户明确要求配乐、音效、氛围声、旁白节奏。
- 广告片、情绪片或无对白短片需要声音帮助节奏成立。

输出目标：

- 音乐情绪、速度、乐器、声场、环境声、关键音效。
- 不展开复杂作曲，不让音乐压过故事和镜头。

### `prompts/platform_adapter.md`

用途：把通用提示词改写为平台适配版本。

使用时机：

- 用户明确指定平台，如可灵、即梦、海螺、通义万相、Runway、Pika、Veo、Luma、Midjourney。
- 用户要求中文提示词、英文提示词、首尾帧提示词、图生视频或文生视频版本。

输出目标：

- 保留通用导演语言。
- 追加平台适配版本。
- 不编造不确定的平台参数；不确定时使用自然语言约束。

### `prompts/quick_package_router.md`

用途：在最终交付前判断用户请求应该进入 `Prompts Only`、`Continue Mode`、`Quick Mode`、`Standard Mode` 还是 `Full Mode`。

使用时机：

- 所有完整或半完整流程在进入 `output_composer` 前都应使用。
- 用户指定即梦、短片、镜头数、只要提示词、快速测试、完整制作包时必须使用。

输出目标：

- 明确 `delivery_mode`、`visible_sections`、`shot_id_range`、`canvas_mode` 和给 `output_composer` 的交付说明。
- 用户报告“素材好了”“S01 完成”“某一步失败”“继续下一步”或粘贴 `project_state` 时进入 `Continue Mode`，只交付下一张操作卡或失败诊断卡。
- 用户要求修改既有制作包但不是失败诊断时进入 `Revision Mode`，只交付改稿补丁。
- 稳定路由同类请求，避免即梦短片有时输出短包、有时输出完整制片文档。
- 用户说“只要提示词”时，省略一句话设定和镜头表，只保留锚点、复制区和失败修正。

### `prompts/revision_patch_builder.md`

用途：处理既有制作包的局部改稿。

使用时机：

- 用户说“镜头 2 改一下”“换成横屏”“缩短到 10 秒”“风格更水墨”“只改这一段，其他不变”。
- 用户粘贴 `project_state` 或已有执行包后提出新约束。
- 用户需要保留已满意的素材和镜头，只替换受影响提示词。

输出目标：

- 明确改稿类型、影响范围、保留不变内容和下一动作。
- 只输出受影响的 `IMG-*`、`VID-*`、`ASSET-*` 或全局锚点替换块。
- 不重复完整项目设定、镜头表或未受影响提示词。

### `prompts/output_composer.md`

用途：把内部 `Project Packet` 和各模块产物压缩为用户可直接使用的最终输出。

使用时机：

- 所有完整或半完整流程在交付给用户前都应使用。
- 用户指定即梦、短片、3-6 镜头、快速测试、直接复制提示词时，默认使用 `Quick Mode`。
- 用户正在执行既有项目并报告进度或失败时，使用 `Continue Mode`，不要重复完整执行包。
- 用户要求保存状态或跨线程继续时，输出可复制的 `project_state` JSON，不自动写文件。
- 用户说“太复杂”“不好用”“只要提示词”“只要即梦执行包”时必须使用。

输出目标：

- 默认不暴露完整 `Project Packet`、`Handoff Notes`、长篇导演阐述、完整角色/场景圣经。
- 根据 `Prompts Only`、`Revision Mode`、`Continue Mode`、`Quick Mode`、`Standard Mode`、`Full Mode` 选择合适颗粒度。
- 对即梦项目优先输出“复制提示词”和“生成顺序”。

### `prompts/qa_reviewer.md`

用途：制作包质检与风险修正。

使用时机：

- 完整制作包输出前必须使用。
- 用户要求 review、优化、检查可生成性。
- 用户遇到风格漂移、角色不一致、视频变形、镜头失败。

输出目标：

- 检查故事闭合、镜头可生成性、角色一致性、场景一致性、提示词过载、平台适配风险。
- 给出具体修正：拆镜、降级动作、强化锚点、减少风格词、改变镜头时长或景别。
- 在 Quick/Continue 场景中只输出生成前自检、局部补丁或失败诊断，不重复整包。

## Reference 使用规则

按需读取 `references/`，不要一次性加载全部。

- `references/styles.md`: 当用户提到风格、类型、视觉参考、电影感、动画美术时读取。
- `references/shot-language.md`: 当需要分镜、景别、机位、摄影机运动、剪辑节奏时读取。
- `references/prompt-templates.md`: 当需要生图提示词、生视频提示词、角色锚点、场景锚点时读取。
- `references/jimeng-canvas.md`: 当目标平台是即梦并需要画布、融合、局部编辑、扩图、抠图或关键帧导出时读取。
- `references/workflow.md`: 当用户要求完整制作包、团队交接、真实影视制作路径或“从想法到成片”解释时读取。
- `references/platform-guides.md`: 当用户指定具体 AI 平台时读取；若该文件不存在，使用通用平台适配原则。
- `references/production-checklist.md`: 当输出完整制作包、做 QA、修复失败结果时读取。

## 默认执行顺序

如果用户是在汇报既有项目进度，或粘贴 `project_state` JSON，先运行 `quick_package_router`。命中 `Continue Mode` 后，只读取当前步骤所需字段和对应模块，不重新运行完整制作管线。

完整制作包默认遵循“从想法到成片”的制作路径，按以下顺序执行：

1. 创意捕捉：`intake`
2. 创意开发：`project_brief_builder`、`story_builder`
3. 导演方案：`director_treatment_builder`
4. 设计圣经：`character_scene_bible_builder`
5. 分镜与镜头规划：`shotlist_builder`
6. 关键帧生产：`image_prompt_builder`
7. 交付模式路由：`quick_package_router`，在画布规划前确定 `delivery_mode` 和 `canvas_mode`
8. 即梦静态素材适配：`platform_adapter`，目标平台为即梦时先适配角色、场景、道具和关键帧提示词
9. 即梦画布规划：`canvas_workflow_builder`，`canvas_mode=enabled` 时使用
10. 视频镜头生产：`video_prompt_builder`，读取画布导出关系或普通关键帧提示词
11. 平台视频适配：`platform_adapter`，用户指定平台时适配最终视频提示词
12. 剪辑组装检查：`shotlist_builder`、`qa_reviewer`
13. 声音与配乐：`sound_builder`
14. 质检与交付：`qa_reviewer`
15. 输出压缩与交付：`output_composer`

如果用户只要求局部产出，则只运行相关模块：

- 只要分镜：使用 `intake`、`director_treatment_builder`、`story_builder`、`shotlist_builder`、`qa_reviewer`。
- 只要生图提示词：使用 `intake`、`character_scene_bible_builder`、`image_prompt_builder`、必要时使用 `styles` reference。
- 只要视频提示词：使用 `intake`、`shotlist_builder`、`video_prompt_builder`、必要时使用 `platform_adapter`。
- 只要即梦执行包：使用 `intake`、`character_scene_bible_builder`、`shotlist_builder`、`image_prompt_builder`、`quick_package_router`、`platform_adapter`、`canvas_workflow_builder`、`video_prompt_builder`、`output_composer`，默认 `Quick Mode`。
- 只要即梦提示词：使用 `intake`、`character_scene_bible_builder`、`shotlist_builder`、`image_prompt_builder`、`video_prompt_builder`、`platform_adapter`、`quick_package_router`、`output_composer`，默认 `Prompts Only`。
- 继续即梦制作：读取已有 `execution_state`、用户粘贴的 `project_state` 和本轮进度，使用 `quick_package_router`、对应失败步骤的模块、`output_composer`，默认 `Continue Mode`。
- 局部改稿：读取已有 `Project Packet`、`project_state` 或用户粘贴的制作包，使用 `quick_package_router`、`revision_patch_builder`、必要时使用对应提示词模块、`output_composer`，默认 `Revision Mode`。
- 失败诊断：用户报告失败、变形、漂移、过曝、卡住或审核失败时，使用 `failure-diagnosis-card.md`，只输出诊断、重试提示词和状态更新。
- 已有角色图/场景图做即梦短片：把已有素材标记为 `user_upload`，使用 `canvas_workflow_builder` 导入和编排，不重复生成同类参考图。
- 已有剧本改分镜：使用 `intake`、`director_treatment_builder`、`character_scene_bible_builder`、`shotlist_builder`，不要重写核心剧情。
- 平台适配：先保留通用提示词，再使用 `platform_adapter` 生成目标平台版本。
- 失败修复：使用 `qa_reviewer`，再回到对应模块修正提示词、镜头或锚点。

## 默认输出模式

内部制作流程可以完整运行，但用户可见结果默认必须经过 `output_composer` 压缩。默认目标是“让用户立刻复制到 AI 工具里试”，而不是展示完整制片文档。

在进入 `output_composer` 前，先使用 `quick_package_router` 判断交付模式。该路由结果是交付模式的唯一来源，`output_composer` 不得再次根据平台、片长或内部产物自行改判。即使内部已经生成导演方案、故事结构和圣经，Quick Mode 也只展示执行所需内容。

### Continue Mode（制作续接）

当用户已经开始执行项目，并说“素材好了”“S01 完成”“某一步失败”“继续”“下一步”“从 S03 接着做”，或粘贴 `project_state` JSON 时使用。

只输出：

1. 当前状态。
2. 下一步动作。
3. 当前步骤唯一需要复制的提示词（如有）。
4. 完成检查。
5. 失败后改法。

不要重复一句话设定、完整锚点、镜头表、其他镜头提示词或全部画布操作。只有用户明确要求“重新输出整包”时才回到原交付模式。

Continue Mode 子模式：

- `next_step`: 正常继续，只输出下一步卡片。
- `failure_repair`: 失败修复，只输出失败诊断卡、重试提示词和状态更新。

### Quick Mode（默认）

适用场景：

- 5-30 秒且 6 镜以内的短片。
- 用户说“快速”“先试一下”“直接给提示词”“只要能复制”，且没有与片长、镜头数或完整交付要求冲突。
- 用户只指定即梦但没有片长和镜头数时，默认补齐为 15 秒、3 镜头。
- 用户没有明确要求完整制作包。

仅指定即梦不代表必须进入 Quick Mode。即梦项目超过 30 秒或超过 6 镜时，使用 Standard Mode；用户明确要求完整交付时使用 Full Mode。

默认输出结构：

1. `先做这几步`
2. `项目锚点与镜头表`
3. `素材准备`
4. `逐镜头执行卡`
5. `失败修正`

Quick Mode 约束：

- 首要目标是复制执行，不是制片解释。
- 不默认展开长篇项目简报、导演阐述、完整故事脚本、完整角色/场景圣经、`Project Packet`、`Handoff Notes`。
- 项目简报、导演方案、故事脚本只压缩成 1 个设定句或 3-5 行摘要。
- 角色/场景圣经只提炼为全局锚点和避免项。
- 配乐最多 1 行；风险最多保留最重要 3 条。
- 每个镜头表至少包含：时长、画面、动作、即梦方式。
- 即梦项目默认使用画布阶段整合静态素材和镜头首帧，不额外重复一套完整生图章节。
- 6 镜以内不单独展开画布布局表，只用一行说明 `CV-MASTER` 包含 `Z-ASSET` 与 `Z-Sxx`。
- 每个镜头使用一张连续执行卡，把画布操作、`IMG-Sxx` 导出、`VID-Sxx` 提示词、检查点和失败改法放在一起。
- 执行卡必须包含画布/区域、输入素材、稳定操作类型、完成检查、失败改法和 `IMG-Sxx` 导出。
- 即梦提示词必须保留画布素材提示词、局部操作提示词和视频提示词。
- 即梦复制块必须使用稳定编号，如 `IMG-REF`、`IMG-S01`、`VID-S01`。
- 每条“复制提示词”必须放在独立的 `text` 代码块中，操作说明和失败修正放在代码块外。
- 第一节必须告诉用户先生成哪张图、再生成哪段视频。
- Quick Mode 默认在末尾输出一个短小 `project_state` JSON，除非用户明确说“只要提示词”。

### Standard Mode

适用场景：

- 31-90 秒短片，或 7-12 个镜头的项目。
- 用户需要较完整的故事、导演方向、角色一致性和逐镜头提示词，但没有要求团队级交接文档。

默认输出结构：

1. 简短项目简报
2. 简短导演方案
3. 故事结构
4. 角色/场景锚点
5. 分镜镜头表
6. 画布资产、关键帧和导出计划（即梦项目）
7. AI 视频提示词
8. 声音方向
9. 主要风险与修正

### Full Mode

只有当用户明确要求“完整制作包”“详细方案”“团队交接”“完整导演阐述”“完整角色圣经”“所有模块都展开”时才使用。

Full Mode 可以输出完整的项目简报、导演阐述、故事脚本、角色与场景圣经、分镜镜头表、AI 生图提示词、即梦画布计划、AI 视频提示词、配乐与声音建议、风险提示与迭代方案、最终制作检查清单。

即梦项目的画布规则：

- Quick、Standard、Full 默认启用 `canvas_plan`。
- Prompts Only 不展示画布布局或操作卡，只保留按角色、场景、道具、镜头用途分类的 `IMG-*` 提示词。
- Prompts Only 不默认输出 `project_state`；只有用户明确要求“保存状态”时才附加。
- 非即梦项目不启用 Canvas Mode。
- 6 镜以内使用单张主画布；7-12 镜使用资产母版加场次画布；超过 12 镜按场次分批，每张分镜画布最多 4-6 镜。
- 画布只负责视觉资产、构图和关键帧修复；视频运动仍由 `video_prompt_builder` 负责。

无论使用哪种模式，每个镜头都必须保留明确的叙事目的、可生成动作、一致性锚点和失败降级思路；只是 Quick Mode 将这些信息压缩到镜头表、提示词和失败修正中。

## 使用案例

用户输入：

```text
我想做一个 60 秒动画：一只小机器人在雨夜寻找星星，风格要温暖一点，可以用 AI 视频生成。
```

执行方式：

1. 使用 `intake` 提取：60 秒、温暖风格、机器人主角、雨夜、寻找星星、AI 视频。
2. 使用 `project_brief_builder` 生成项目目标、受众、画幅、交付物和默认平台假设。
3. 使用 `director_treatment_builder` 设定温暖手绘幻想或柔和 3D 动画方向，明确雨夜不做恐怖片，而做孤独到希望的情绪曲线。
4. 使用 `story_builder` 拆成：机器人失去星光、穿过雨巷、发现水洼倒影、修好路灯、星光回到城市。
5. 使用 `character_scene_bible_builder` 固定机器人外观、材质、发光胸灯、雨衣或金属磨损，以及雨夜城市的光源和色彩。
6. 使用 `shotlist_builder` 生成 8 个左右镜头，每个镜头控制一个主要动作。
7. 使用 `image_prompt_builder` 生成关键帧提示词，优先锁定机器人造型和雨夜城市。
8. 使用 `video_prompt_builder` 生成逐镜头运动提示词，例如“机器人缓慢抬头”“摄影机轻微推进”“雨滴落入水洼”。
9. 使用 `sound_builder` 给出轻柔钢片琴、低频雨声、微弱电子音效。
10. 使用 `qa_reviewer` 检查角色漂移、雨水复杂度、夜景过暗、镜头动作过载，并给出拆镜或降级方案。

最终输出应是一套可复制到 AI 生图和 AI 视频工具中的制作包，而不是只给一句提示词。

## 质量要求

- 必须先建立一致性锚点，再写提示词。
- 必须把复杂镜头拆成可生成的小镜头。
- 必须明确每个镜头的叙事目的。
- 必须区分生图提示词和视频提示词。
- 必须保留通用版本，平台适配作为附加层。
- 必须在完整制作包最后给出风险和修正方案。
