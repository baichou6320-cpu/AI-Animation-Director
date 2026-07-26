---
name: ai-animation-director
description: Guide AI animation projects from one structured QA confirmation to a complete production-ready execution package. Use when Codex needs to turn an animation theme, idea, script, episode, character, visual reference, storyboard, ad concept, or website hero/background video into researched creative directions, shot plans, image/video prompts, pixel finishing, web media delivery, and a reviewed final short. Defaults to one QA round followed by automatic continuation; supports optional strict stage reviews, Jimeng Smart Canvas, scroll-scrub website backgrounds, professional pixel shorts, Seedance script pipelines, reusable assets, prompt QA, continuation, revision, and failure repair for 5-180 second projects.
---

# AI Animation Director

本 Skill 用于把动画创意、故事、脚本、角色设定、广告概念或视觉风格要求，转化为高效率的 AI 动画创作流程。默认路径是：主题输入、一次结构化 QA、连续完成研究与创意、镜头、图片提示词、视频提示词、后期与质检。只有用户明确要求逐阶段审核时，才增加蓝图、关键帧或样片确认门。

核心目标不是写单条提示词，而是模拟一个资深动画导演、制片 PM、AI 视频工作流工程师的协作流程：先明确意图，再建立导演方案和一致性锚点，最后生成分镜、关键帧提示词、视频运动提示词、声音建议和风险清单。内部可以完整思考，但默认给用户轻量、可复制、可执行的结果。

## 使用边界

- 使用本 Skill 编写制作方案、提示词、分镜表、脚本、导演阐述、角色/场景圣经、平台适配文本和质检清单。
- 图像或视频工具可用且执行范围明确时可以连续生成；工具不可用时一次性交付平台可复制的全部图片与视频提示词。默认不要求关键帧二次确认，`strict_review` 除外。
- 不复刻受版权保护的角色、影视作品、具体专有画面或在世艺术家的个人风格；将参考转换为通用的色彩、材质、镜头、节奏、光影和情绪特征。
- 配乐和声音始终低于故事、镜头、画面和提示词优先级，只给方向、节奏、乐器、氛围和关键音效。

## 内部制作路径

默认交付不要展开真实影视流程。需要完整制作包、团队交接、导演解释，或需要确认“从想法到成片”的内部路径时，按需读取 `references/workflow.md`。

## 跨模块交接机制

不要把整个制作流程当成一次性提示词。每个 prompt 模块都必须像真实影视岗位一样接收上一环节的交接物，完成自己的专业判断，再把更新后的信息传给下一环节。

新建即梦 Quick 项目优先使用结构化项目目录：`project.json` 只保存索引，阶段事实分别写入 `input/`、`creative/`、`production/`、`prompts/` 和 `state/` 下的 JSON。用户可见内容写入 `deliverables/`。模块只读取当前阶段需要的字段，不再传递不断扩大的 Markdown `Project Packet`。

旧项目、Seedance Harness 和尚未迁移的 Full Mode 暂时继续使用 `Project Packet` 兼容层。它不是最终给用户看的完整文案；迁移后的等价物是运行时只读的 `ProjectContextView`。

`Project Packet` 至少包含：

- `source_input`: 用户原始输入和已知硬约束。
- `guided_intake_state`: 新项目一次 1-3 题的问答状态、已回答项、默认项和下一动作；只有 `strict_review` 最多允许两轮。
- `research_state`: 联网研究策略、触发原因、状态、查询、来源数量、未验证假设和下一动作。
- `research_brief`: 题材洞察、同类参考方法、视觉语言、差异化机会和来源链接。
- `visual_references`: 用户上传或描述的风格参考、失败图和原提示词，使用 `REF-STYLE-*` 记录来源、可见性和分析状态。
- `style_dna`: 参考图风格真相源，记录主色调、光影、空间层次、材质、构图、画面密度、稳定提示词表达和版权安全转译。
- `concept_pitch`: 2-3 个创意方向、推荐项、故事大纲、角色世界观初稿和视觉方向。
- `approval_state`: `interaction_policy`、`qa_confirmation`、`concept_approval`、`keyframe_approval` 和 `approval_override`。
- `generation_capabilities`: 网页研究、图像生成、视频生成工具是否可用及降级方式。
- `approved_assets`: 已确认的 `REF-*`、`IMG-Sxx`；候选资产不得提前标记为批准。
- `direct_assumption_mode`: 用户要求试跑、先给一版或跳过问答时为 `true`。
- `batch_window`: 偏长 Quick 包当前展开的镜头范围，例如 `S01-S02`。
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
- `web_background_spec`: 网站背景交付配置，记录滚动交互、真实时长、文案安全区、环境微动、不动项、静音要求和桌面/移动/海报资产。
- `script_state`: 分集、场次、剧情点、原始剧本文本、处理进度和下一动作。
- `director_scene_book`: 导演讲戏本、人物清单、场景清单、道具清单和可执行性风险。
- `asset_library`: `CHAR-*`、`SCENE-*`、`PROP-*`、`REF-*` 资产 ID、状态、提示词和复用关系。
- `reference_index`: Seedance Harness 的单一素材真相源，统一登记角色、场景、道具、音频、故事板、文件名、`@图片/@音频` 用途和复用状态。
- `reference_map`: Seedance `@图片/@视频/@音频` 映射表和用途说明。
- `seedance_constraints`: Seedance 节拍密度、安全区、素材数量限制和分时段规则。
- `hero_image_state`: 全片调性参考图状态，记录 `REF-HERO` 是否需要生成、已生成或已批准。
- `pixel_style_bible`: 像素短片的原生/交付分辨率、帧率、调色板、颗粒、角色比例、光影、空间层次和不动项。
- `animatic_state`: 动态分镜状态、逐镜时长、草图、临时声音、输出路径、审核结果和下一动作。
- `motion_contracts`: 每个 `VID-Sxx` 的起始/结束状态、主体动作、摄影机动作、环境微动、不动项和降级方案。
- `finishing_state`: 逐镜像素统一、全局调色板、最终声音、母版路径和成片评分。
- `storyboard_requirements`: 复杂镜头清单，记录需要故事板的 `SD-Sxx`、复杂原因和建议格数。
- `render_plan`: Seedance/即梦样片优先、批量生成策略、候选出片单元和是否允许全量渲染。
- `sample_review`: 样片审核结果、失败原因和是否允许批量生成。
- `stage_reviews`: 各阶段评分、`PASS/FAIL` 结论、返修建议和合规结论。
- `progress_report`: 当前集、当前阶段、已完成文件、待审核项和下一步。
- `evolution_signals`: 待用户确认的规则进化建议；确认前不得自动修改 Skill。
- `execution_state`: 当前制作进度、已完成资产/镜头、失败步骤、下一动作，以及视频生成策略、请求/实际时长、参考图数量和逐镜头重试状态。
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
- `templates/`: 稳定输出模板，如即梦执行包、项目状态、失败诊断卡，以及导演讲戏、资产库、Seedance 提示词和阶段审核模板。
- `examples/`: 验收样例，使用最终输出格式，不包含内部推理，如像素风即梦短包、国风水墨即梦短包、只要提示词模式、续接/失败/改稿样例和 Seedance 分集流水线样例。
- `tools/`: 后续可加入轻量校验脚本，用于检查制作包是否缺少关键部分。
- `scripts/`: 可选执行层，用于把已审核的 manifest 提交给即梦兼容 API、轮询任务并下载结果。
- `outputs/`: 保存生成用 manifest、图片、视频和执行结果，不把媒体产物写回 prompt 文件。
- 仓库根目录 `production_workspace/`: 可选本地工作台，记录关键帧、视频、像素成片三个阶段，并构建动态分镜、统一像素规范和拼接母版。

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

像素短片本地后期不依赖即梦 API。用户已有本地图片和视频后，读取 `references/pixel-animation-production.md`，再使用：

```bash
python -m production_workspace build-animatic project.json --output outputs/animatic.mp4
python -m production_workspace pixel-finish project.json --output-directory outputs/pixel --palette-source assets/REF-HERO.png
python -m production_workspace assemble project.json --output outputs/final-master.mp4 --audio assets/final-mix.wav
```

网站背景视频使用结构化网页媒体处理命令：

```bash
python -m production_workspace prepare-web-background SOURCE --output-directory site/public/media --poster-source APPROVED_KEYFRAME --duration 10.1
```

## Prompt 模块地图

以下模块位于 `prompts/`。当对应文件存在时，按需读取对应模块；当文件尚未存在时，遵循本节定义的模块职责执行。

### `prompts/creative_intake_interviewer.md`

用途：新项目开场问答，用 5 个选择题锁定视频类型、情绪目标、视觉风格、平台流程和片长镜头规模。

使用时机：

- 用户开启新项目但需求模糊。
- 用户说“先问我”“帮我设计方向”“我不确定风格”。
- 用户审美要求强，或正在抱怨提示词效果差。

输出目标：

- 输出 `Guided Intake Mode` 问答卡。
- 只问高影响问题，不生成完整制作包。
- Prompts Only、Continue、Revision 和 Failure Repair 优先级高于问答。

### `prompts/creative_research_builder.md`

用途：智能判断是否需要联网，生成带来源的简短 `Research Brief`。

使用时机：

- 新项目完成问答后，或用户已经给出足够主题信息。
- 历史文化、现实地点、真实行业、当前趋势、陌生题材、参考视频或强审美项目。

输出目标：

- 研究题材事实、同类公开作品的方法、视觉语言、观众预期和差异化机会。
- 搜索失败时保留未验证假设，不伪造来源。
- 不复制他人剧情、角色、镜头或个人风格，不进入图片生产。

### `prompts/concept_pitch_builder.md`

用途：把用户输入和研究结果整理成结构化创意提案。默认作为内部蓝图继续生产；仅在 `strict_review` 中单独等待确认。

输出目标：

- 提供 2-3 个方向、推荐方案、故事大纲、角色世界观初稿和可执行视觉语言。
- 最多提出 3 个高影响问题。
- `single_confirm` 下继承 QA 授权并继续；`strict_review` 下设置 `concept_approval=pending`。

### `prompts/approval_gate_manager.md`

用途：选择 `single_confirm`、`strict_review` 或 `direct_run`，管理是否需要人工确认门。

输出目标：

- 默认 `single_confirm`：用户回复一次 QA 后连续生成完整执行包，不再等待蓝图或关键帧确认。
- 仅 `strict_review`：未批准概念时禁止图片生产，未批准关键帧时禁止视频生产。
- 概念返修只修改 `concept_pitch`；关键帧返修只修改受影响 `REF-*` / `IMG-Sxx`。
- 用户明确说“不要确认，直接生成”或“一次做完”时使用 `direct_run` 并设置 `approval_override=true`。
- 检测研究、图像和视频工具能力；工具不可用时退化为复制提示词。

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

### `prompts/director_scene_translation_builder.md`

用途：把剧本、分集文本或小说段落翻译成“导演讲戏本”。

使用时机：

- 用户输入完整剧本、分集文本、`ep01`、长故事或短剧片段。
- 用户指定 Seedance，或要求从剧本生成视频提示词。
- `quick_package_router` 判定为 `pipeline_mode=script_pipeline`。

输出目标：

- 把抽象剧本转成自然叙述式讲戏，包含具体物理动作、动作链、镜头方向、光源方向/色温/强度、环境声和情绪停顿。
- 不输出分镜表，不输出最终 Seedance 提示词。
- 禁止只复述“她很孤独”“气氛紧张”等抽象词，必须翻译成可见动作和空间细节。

### `prompts/asset_library_builder.md`

用途：从导演讲戏本提取跨集可复用的人物、场景和道具资产库。

使用时机：

- `director_scene_book` 已生成。
- 用户做多集、长剧本、Seedance 项目，或明确要求角色/场景/道具资产库。
- 需要判断资产是 `new`、`reuse` 还是 `variant`。

输出目标：

- 使用稳定 ID：`CHAR-*`、`SCENE-*`、`PROP-*`、`REF-*`。
- 生成人物提示词、场景宫格提示词和道具提示词，可复制到用户项目的 `assets/`。
- 同步建立或更新 `reference_index`，把角色、场景、道具、音频和故事板统一登记为可复用引用，锁定文件名和 `@图片/@音频` 用途。
- 不覆盖历史资产；复用只写复用说明，变体说明保持不变和变化部分。

### `prompts/seedance_storyboard_adapter.md`

用途：兼容旧流程，把导演讲戏本和资产库转成 Seedance 叙事式视频提示词脚本。新 Seedance Harness 项目优先使用 `seedance_motion_prompt_builder`，只在需要旧格式 `SD-Sxx` 脚本时使用本模块。

使用时机：

- 目标平台是 Seedance。
- `director_scene_book` 和 `asset_library` 已经生成或用户已有参考图。
- 用户需要 `@图片/@视频/@音频` 引用、分集视频脚本或 Seedance 提示词。

输出目标：

- 建立 `reference_map`，明确每个 `@图片/@视频/@音频` 的用途。
- 每条 `SD-Sxx` 包含引用用途、时间段、主体动作、镜头运动、光影变化和声音设计。
- 10 秒以上使用分时段描述，遵守前后 0.5 秒安全区；参考图已有的静态外观不重复堆写。

### `prompts/seedance_motion_prompt_builder.md`

用途：把导演讲戏本、`reference_index` 和资产库转成真正可复制到 Seedance 的 motion prompt。

使用时机：

- 目标平台是 Seedance，且导演讲戏和资产库已经通过审核。
- 用户要求 Codex + Seedance 2.0 工作流、motion prompt、预告片/剧情片出片单元。
- `pipeline_mode=seedance_harness_mode` 或 `script_pipeline`，并且下一步是 motion prompt。

输出目标：

- 每条 `SD-Sxx` 固定三块：`参考设定`、`氛围与画质`、`画面内容`。
- 静态外观由 `reference_index` 锁定，motion prompt 重点写动作链、镜头运动、光影变化、声音和微表情。
- 动作类镜头写具体物理链条；情绪类镜头写眼角、嘴角、呼吸、肩颈和停顿。
- 标记复杂镜头到 `storyboard_requirements`，不要把复杂走位硬塞进单条提示词。

### `prompts/storyboard_panel_builder.md`

用途：为复杂 `SD-Sxx` 生成 6 宫格或 4 宫格故事板提示词，约束走位、前后景、动作顺序和镜头方向。

使用时机：

- `storyboard_requirements` 中存在 `storyboard_required=true` 的镜头。
- 某一镜多人/多物体交互、走位复杂、动作密，或 motion prompt 审核指出文字无法说明走位。

输出目标：

- 每格必须对应 motion prompt 中一个明确动作或过渡。
- 生成 `SB-Sxx`，并写入 `reference_index` 与 `render_plan.storyboard_units`。
- 明确“故事板 + 同编号 motion prompt”一起使用，不允许只上传故事板让模型自由发挥。

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
- 当存在 `style_dna` 时，优先继承主色调、光源方向、空间层次、材质和构图规则，不再只依赖抽象风格词。

### `prompts/visual_reference_analyzer.md`

用途：把用户上传的参考图、参考图描述、失败生成图或参考提示词转成 `Style DNA`。

使用时机：

- 用户上传图片并说“参考这个画风”“像这张图”“参考这个质感”。
- 用户粘贴“宫崎骏类似”“Moebius 风格”“高级感”等审美参考，需要版权安全转译。
- 用户说“太丑”“画风不对”“提示词效果差”，并提供参考图、失败图或原提示词。
- 生图、即梦画布、Seedance 资产索引或 Prompt QA 之前需要先锁定风格锚点。

输出目标：

- 提取主色调、光影方向、景深/空间层次、笔触/材质、构图方式、画面密度和情绪气质。
- 生成可直接写入 `IMG-*` 的稳定表达和负向约束。
- 更新 `visual_references`、`style_dna`，并在 Seedance Harness 项目中把 `REF-STYLE-*` 写入 `reference_index`，用途为 `style_reference`。
- 如果图片不可见或缺失，只请求用户补图或描述，不编造画面细节。

### `prompts/video_prompt_builder.md`

用途：生成 AI 视频提示词。

使用时机：

- 用户要用可灵、即梦、海螺、Runway、Pika、Veo、Luma 等视频模型。
- 分镜已经明确，需要写每镜头的运动提示词。
- 用户要求镜头运动、角色动作、动态画面或视频生成。

输出目标：

- 每个镜头包含主体运动、摄影机运动、时间变化、物理约束、连续性要求、避免项、失败降级方案。
- 每个镜头只保留一个主要主体动作和一个主要摄影机动作；复杂动作建议拆镜。
- 多张不同场景参考图必须拆成独立 `VID-Sxx`；多图只用于同镜头补充参考或同场景首尾帧。

### `prompts/pixel_style_bible_builder.md`

用途：把 `Style DNA` 和批准的 `REF-HERO` 转成全片唯一的像素美术与技术规范。

使用时机：

- 用户要制作像素动画成片，而不是只要一张像素图或几条提示词。
- 路由进入 `pixel_short_mode`，且概念已批准。

输出目标：

- 默认锁定 `320x180`、`12fps`、最多 48 色、`6x nearest-neighbor` 和 `1920x1080/24fps` 交付。
- 固定角色比例、像素颗粒、调色板、光源、空间层次、不动项和避免项。
- `REF-HERO` 未批准时停止，不进入动态分镜。

### `prompts/animatic_builder.md`

用途：用草图、精确时长、剪辑点和临时声音验证故事与节奏。

使用时机：

- `REF-HERO` 已批准，故事已拆成明确节拍。
- 像素短片准备进入正式关键帧生产。

输出目标：

- 生成 `SB-Sxx` 和 `animatic_plan`，15 秒基准片严格使用 4 镜头。
- 设置 `animatic_state=pending` 并等待用户确认。
- 动态分镜未批准时禁止生成正式 `IMG-Sxx` 和 `VID-Sxx`。

### `prompts/video_result_reviewer.md`

用途：审核已经生成的真实视频，并只返修失败镜头。

使用时机：

- 用户上传视频、报告成片质量差、几乎没有运动、时长不符或多图顺序混乱。
- 需要比较请求时长与实际时长，或检查开头/中段/结尾抽样画面。

输出目标：

- 判断 `pass / retry / split_first`。
- 识别 `under_motion`、`reference_confusion`、`duration_mismatch` 等结果问题。
- 更新视频执行状态，并给出单镜头重试提示词；不重写已通过镜头。

### `prompts/web_background_builder.md`

用途：把已批准环境关键帧或视频转换为网站首屏背景视频契约和网页媒体交付。

使用时机：

- 用户提出网站背景、首屏视频、Hero 视频、滚动播放或滚动倒放。
- 需要预留文案安全区、准备桌面/移动素材或优化浏览器定位。

输出目标：

- 保持 `pipeline_mode=short_form`，设置 `delivery_profile=website_background`。
- 写入 `production/web-background.json`，生成 `IMG-WEB-HERO` 和 Website Motion Contract。
- 强制单一连续场景、低复杂度环境微动、静态结构锁定、无音频和公开使用权检查。

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

用途：在最终交付前判断用户请求应该进入 `Guided Intake`、`Prompts Only`、`Revision Mode`、`Continue Mode`、`Script Pipeline Mode`、`Quick Mode`、`Standard Mode` 还是 `Full Mode`。

使用时机：

- 所有完整或半完整流程在进入 `output_composer` 前都应使用。
- 用户指定即梦、Seedance、剧本/分集、短片、镜头数、只要提示词、快速测试或完整制作包时必须使用。

输出目标：

- 明确 `pipeline_mode`、`delivery_mode`、`visible_sections`、`shot_id_range`、`canvas_mode` 和给 `output_composer` 的交付说明。
- 完整剧本、分集文本、`ep01`、长故事或 Seedance 剧本转视频请求进入 `script_pipeline`。
- 新项目、需求模糊、审美要求强时，默认先进入 `guided_intake`。
- 用户已经给出足够约束并说“尝试/实验/先给一版/用这个 skill 写提示词”时，设置 `direct_assumption_mode=true`，跳过问答并直接进入可执行交付。
- 30 秒且 6 镜头的 Quick 项目可设置 `batch_window`，先展开当前批次执行卡，避免一次输出过长。
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
- 对 Seedance 剧本项目输出 `Script Pipeline Mode`，压缩为导演讲戏摘要、资产库更新、素材对应表、Seedance 提示词和阶段审核。

### `prompts/stage_gate_reviewer.md`

用途：脚本流水线的阶段门禁，统一做业务审核和合规审核。

使用时机：

- `director_scene_translation_builder` 完成后审核导演讲戏。
- `asset_library_builder` 完成后审核服化道资产设计。
- `seedance_storyboard_adapter` 完成后审核 Seedance 提示词。
- 用户要求 review、合规检查、阶段验收或返修建议。

输出目标：

- 三个业务阶段分别评分：导演讲戏审核、资产设计审核、Seedance 提示词审核。
- 平均分低于 8 或任一单项低于 6 即 `FAIL`，只返修对应阶段。
- 合规审核检查版权 IP、真人脸部素材、敏感内容、暴露/暴力、平台限制。

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

### `prompts/prompt_quality_reviewer.md`

用途：检查和局部修补生图/视频提示词质量。

使用时机：

- `image_prompt_builder` 和 `video_prompt_builder` 完成后、最终交付前。
- 用户说“提示词不好”“太丑”“画风跑了”“视频动崩了”。
- Quick Mode 需要把风险压缩成最重要 3 条时。

输出目标：

- 检查生图提示词是否有主体、空间层次、色彩、光影、材质、风格转译和负向约束。
- 检查生图提示词是否继承 `style_dna`，尤其是主色调、光源方向、空间层次、材质、构图和画面密度。
- 检查视频提示词是否引用同编号 `IMG-Sxx`、只保留一个主体动作和一个摄影机动作。
- 只修补不合格编号，不重写整包。

## Reference 使用规则

按需读取 `references/`，不要一次性加载全部。

- `references/styles.md`: 当用户提到风格、类型、视觉参考、电影感、动画美术时读取。
- `references/shot-language.md`: 当需要分镜、景别、机位、摄影机运动、剪辑节奏时读取。
- `references/prompt-templates.md`: 当需要生图提示词、生视频提示词、角色锚点、场景锚点时读取。
- `references/jimeng-canvas.md`: 当目标平台是即梦并需要画布、融合、局部编辑、扩图、抠图或关键帧导出时读取。
- `references/seedance-methodology.md`: 当目标平台是 Seedance，或需要 `@图片/@视频/@音频` 引用、节拍密度、安全区、10 秒以上分时段描述和声音设计时读取。
- `references/pixel-animation-production.md`: 当用户要制作像素动画成片、动态分镜、样片、像素后期或最终母版时读取。
- `references/workflow.md`: 当用户要求完整制作包、团队交接、真实影视制作路径或“从想法到成片”解释时读取。
- `references/platform-guides.md`: 当用户指定具体 AI 平台时读取；若该文件不存在，使用通用平台适配原则。
- `references/production-checklist.md`: 当输出完整制作包、做 QA、修复失败结果时读取。
- 用户提供真实视频时读取 `prompts/video_result_reviewer.md`；无法读取视频时只做基于用户描述的暂定诊断。
- 用户要求 Codex + Seedance 2.0 教程式流程、长剧本、多集或预告片工作流时，优先读取 `prompts/seedance_motion_prompt_builder.md`、`prompts/storyboard_panel_builder.md`、`templates/reference-index.md` 和 `templates/render-sample-plan.md`。

## 默认执行顺序

如果用户是在汇报既有项目进度，或粘贴 `project_state` JSON，先运行 `quick_package_router`。命中 `Continue Mode` 后，只读取当前步骤所需字段和对应模块，不重新运行完整制作管线。

如果用户开启新项目且没有明确说“只要提示词”“不要确认，直接生成”“继续”“失败修复”或“局部改稿”，默认设置 `interaction_policy=single_confirm` 并使用 `creative_intake_interviewer`。先提取已知字段，只补问一轮 1-3 个问题；用户回复后用默认值补齐非关键缺失，并在同一轮继续生成目标执行包。

如果用户是在试跑 Skill，或已经给出主题、风格、片长、平台中的多个硬约束，不要强行重复问答。若信息已达到最低完整度，将原始请求视为本次 QA 确认，设置 `interaction_policy=single_confirm` 和 `qa_confirmation=approved`，补齐 1-3 条默认假设后连续生成。只有明确说“不要确认，直接生成”“跳过确认”或“一次做完”时，才改为 `direct_run` 并设置 `approval_override=true`。

如果用户上传参考图、要求“参考这个画风/质感/构图”，或报告“太丑/画风不对”并提供图像，先运行 `visual_reference_analyzer`。把结果写入 `style_dna` 后，再继续 Concept Review、Keyframe Review、Prompts Only、Revision 或 Failure Repair；不要把参考图分析写成长篇报告，除非用户明确要求“分析这张图”。

如果用户要求“像素动画成片”“做出完整像素短片”“像素游戏电影感短片”，且没有命中 Prompts Only、Continue、Revision、Failure Repair 或 Seedance Harness，设置 `pipeline_mode=pixel_short_mode`。第一条基准片默认使用 `15 秒 / 4 镜头 / 16:9 / 即梦生成 + 本地后期`，并固定按以下顺序执行：

1. 故事开发：只确认一句话故事、主题、4 个剧情节拍和结尾。
2. 风格定调：运行 `visual_reference_analyzer` 和 `pixel_style_bible_builder`，生成并批准 `REF-HERO`。
3. 动态分镜：运行 `animatic_builder`；`animatic_state` 未批准时停止。
4. 正式关键帧：运行 `image_prompt_builder`，逐镜生成并审核 `IMG-S01...IMG-S04`。
5. 最难镜头样片：只生成 `sample_shot_id` 对应的 `VID-Sxx`；未通过时只返修该镜。
6. 逐镜视频：样片批准后，使用 `video_prompt_builder` 的 `Motion Contract` 生成其余镜头，每镜最多 3 次尝试。
7. 像素后期：统一 `12fps`、`320x180`、最多 48 色，再用 nearest-neighbor 整数放大到 `1920x1080/24fps`。
8. 剪辑声音：按动态分镜替换正式镜头，加入环境声、关键音效和简单音乐。
9. 成片验收：故事、节奏、画面一致性和声音均不低于 4/5，否则项目保持未完成。

像素成片模式在 `single_confirm` 下先一次交付完整生产计划、全部生图提示词、全部 Motion Contract 和后期规格；外部素材尚未生成时只把实际文件依赖标记为待完成，不要求用户逐镜确认。仅 `strict_review` 每轮显示一个下一动作并附短学习卡。

普通新项目的固定路径：

1. 动态创作问答：`creative_intake_interviewer`；已有答案不重复问，默认只问一轮 1-3 题。
2. 单次确认：用户回复 QA 后设置 `qa_confirmation=approved`；非关键缺失写入默认假设。
3. 项目蓝图：把确认字段与默认假设整理为一句话理解、结构化需求、故事方向和视觉方向，并作为内部检查点自动继续。
4. 智能研究：按 `required/recommended/skip` 判断是否运行 `creative_research_builder`。
5. 风格与故事：按需运行 `visual_reference_analyzer`、`concept_pitch_builder` 和导演/故事模块。
6. 图片前期：生成资产、镜头和 `REF-*` / `IMG-Sxx`。
7. 图片与视频执行包：同一轮生成全部 `REF-*`、`IMG-Sxx` 和一一对应的 `VID-Sxx`；工具可用时按依赖顺序执行。
8. 剪辑、声音、失败修正和 QA。

用户明确要求 `strict_review` 时，将第 3 步和第 7 步拆成蓝图确认、关键帧确认；普通项目不得自行升级为严格审核。

如果用户输入完整剧本、分集文本、`ep01`、长故事，或明确要求从剧本生成 Seedance 视频，先使用 `quick_package_router` 设置 `pipeline_mode=script_pipeline`。该路径不替换普通短片管线，固定按以下顺序执行：

1. 剧本解析：整理 `script_state`，保留原始剧情、台词、集数和场次。
2. 按需研究题材与改编参考：`creative_research_builder`。
3. 参考图风格解析：如有上传参考图或风格提示词，使用 `visual_reference_analyzer`，并把 `REF-STYLE-*` 登记到 `reference_index`。
4. 剧本改编提案：`concept_pitch_builder`；已有剧本不改写核心剧情，只提案改编方式与视听方向。
5. 概念处理：`single_confirm` 继承 QA 授权自动继续；`strict_review` 使用 `approval_gate_manager`，未确认时停止。
6. 导演讲戏：`director_scene_translation_builder`
7. 导演阶段审核：`stage_gate_reviewer`；`FAIL` 时只返修导演讲戏。
8. 服化道资产库、`reference_index` 与参考图：`asset_library_builder`
9. 资产阶段审核和关键帧处理：`stage_gate_reviewer`；`single_confirm` 自动继续，`strict_review` 再使用 `approval_gate_manager` 等待确认。
10. Seedance Motion Prompt：读取 `references/seedance-methodology.md`，运行 `seedance_motion_prompt_builder`，把每条 `SD-Sxx` 写成“参考设定 / 氛围与画质 / 画面内容”。
11. 复杂镜头故事板：对 `storyboard_requirements` 中的 `SD-Sxx` 运行 `storyboard_panel_builder`，生成 `SB-Sxx` 六宫格提示词。
12. Seedance 提示词和故事板审核：`stage_gate_reviewer`；`FAIL` 时只返修对应 `SD-Sxx` 或 `SB-Sxx`。
13. 样片优先：使用 `templates/render-sample-plan.md` 选择 1-2 条代表性样片，样片通过后才允许批量生成。
14. 输出压缩与交付：`output_composer`，使用 `Seedance Harness Mode` / `Script Pipeline Mode`。

多集第一版最多处理 10 集；单次默认先处理当前集。跨集资产必须从已有 `asset_library` 判断 `new`、`reuse`、`variant`，不得为复用角色重新生成一套提示词。

`single_confirm` 的 QA 已确认、`strict_review` 的概念与关键帧均已批准，或 `direct_run` 已明确绕过后，完整制作包按以下顺序执行：

1. 创意捕捉：`intake`
2. 创意开发：`project_brief_builder`、`story_builder`
3. 导演方案：`director_treatment_builder`
4. 参考图风格解析：如有 `REF-STYLE-*` 或风格描述，使用 `visual_reference_analyzer` 生成 `style_dna`。
5. 设计圣经：`character_scene_bible_builder`
6. 分镜与镜头规划：`shotlist_builder`
7. 关键帧生产：`image_prompt_builder`；图像工具可用时直接生成，否则输出复制提示词。
8. 关键帧处理：`single_confirm` 自动继续到视频提示词；`strict_review` 使用 `approval_gate_manager`、`output_composer` 等待确认。
9. 交付模式路由：`quick_package_router`
10. 即梦静态素材适配和画布：`platform_adapter`、`canvas_workflow_builder`
11. 视频镜头预检与生产：`video_prompt_builder`；先拦截跨场景多图和超出单次承载能力的任务，再执行或输出复制提示词。
12. 平台视频适配：`platform_adapter`
13. 提示词质量审查：`prompt_quality_reviewer`
14. 剪辑、声音与质检：`shotlist_builder`、`sound_builder`、`qa_reviewer`；已有真实视频时追加 `video_result_reviewer`。
15. 输出压缩与交付：`output_composer`

如果用户只要求局部产出，则只运行相关模块：

- 只要分镜：使用 `intake`、`director_treatment_builder`、`story_builder`、`shotlist_builder`、`qa_reviewer`。
- 只要生图提示词：使用 `intake`、`visual_reference_analyzer`、`character_scene_bible_builder`、`image_prompt_builder`、必要时使用 `styles` reference。
- 只要视频提示词：使用 `intake`、`shotlist_builder`、`video_prompt_builder`、必要时使用 `platform_adapter`。
- 只要参考图风格分析：使用 `visual_reference_analyzer` 和 `templates/style-dna-card.md`，输出 `Style DNA Card`，不生成分镜、`IMG-Sxx` 或 `VID-Sxx`。
- 像素短片成片：使用 `visual_reference_analyzer`、`pixel_style_bible_builder`、`animatic_builder`、`image_prompt_builder`、`video_prompt_builder`、`prompt_quality_reviewer` 和本地 `production_workspace`，默认 `Pixel Short Mode`。
- 网站背景视频：使用 `intake`、`visual_reference_analyzer`、`image_prompt_builder`、`web_background_builder`、`video_prompt_builder`、`prompt_quality_reviewer` 和 `output_composer`。保持 `short_form`，设置 `delivery_profile=website_background`；默认单一连续镜头、无音频，并输出桌面/移动/海报交付。
- 剧本/分集转 Seedance：使用 `quick_package_router`、`director_scene_translation_builder`、`stage_gate_reviewer`、`asset_library_builder`、`seedance_motion_prompt_builder`、`storyboard_panel_builder`、`output_composer`，默认 `Seedance Harness Mode`，兼容旧名 `Script Pipeline Mode`。
- 只要 Seedance 提示词：保留 `Prompts Only` 最高优先级；读取已有讲戏本、`reference_index` 和资产库，只输出 `reference_index` 摘要、`SD-Sxx` motion prompt 复制块、必要故事板和失败修正。
- 新项目引导：使用 `creative_intake_interviewer`、`creative_research_builder`、`concept_pitch_builder`、`quick_package_router`、`output_composer`；默认只显示一次 Guided Intake，回答后直接进入目标执行包。
- 试跑/先给一版：信息足够时把原始请求视为单次确认，设置 `direct_assumption_mode=true` 和 `interaction_policy=single_confirm`，连续输出可执行版本。
- 明确一次做完：设置 `interaction_policy=direct_run`、`approval_override=true`，不问 QA，连续进入图片和视频生产。
- 只要即梦执行包：使用 `intake`、`visual_reference_analyzer`、`character_scene_bible_builder`、`shotlist_builder`、`image_prompt_builder`、`quick_package_router`、`platform_adapter`、`canvas_workflow_builder`、`video_prompt_builder`、`prompt_quality_reviewer`、`output_composer`，默认 `Quick Mode`。
- 只要即梦提示词：使用 `intake`、`visual_reference_analyzer`、`character_scene_bible_builder`、`shotlist_builder`、`image_prompt_builder`、`video_prompt_builder`、`platform_adapter`、`prompt_quality_reviewer`、`quick_package_router`、`output_composer`，默认 `Prompts Only`。
- 继续即梦制作：读取已有 `execution_state`、用户粘贴的 `project_state` 和本轮进度，使用 `quick_package_router`、对应失败步骤的模块、`output_composer`，默认 `Continue Mode`。
- 局部改稿：读取已有 `Project Packet`、`project_state` 或用户粘贴的制作包，使用 `quick_package_router`、`revision_patch_builder`、必要时使用对应提示词模块、`output_composer`，默认 `Revision Mode`。
- 失败诊断：用户报告失败、运动不足、多图混乱、变形、漂移、过曝、卡住或审核失败时，使用 `video_result_reviewer`、`qa_reviewer` 和 `failure-diagnosis-card.md`，只输出诊断、重试提示词和状态更新。
- 已有角色图/场景图做即梦短片：把已有素材标记为 `user_upload`，使用 `canvas_workflow_builder` 导入和编排，不重复生成同类参考图。
- 已有剧本改分镜：使用 `intake`、`director_treatment_builder`、`character_scene_bible_builder`、`shotlist_builder`，不要重写核心剧情。
- 平台适配：先保留通用提示词，再使用 `platform_adapter` 生成目标平台版本。
- 失败修复：有真实视频时先使用 `video_result_reviewer`，否则使用 `qa_reviewer`，再回到对应模块修正提示词、镜头或锚点。

## 默认输出模式

内部制作流程可以完整运行，但用户可见结果默认必须经过 `output_composer` 压缩。默认目标是“让用户立刻复制到 AI 工具里试”，而不是展示完整制片文档。

在进入 `output_composer` 前，先使用 `quick_package_router` 判断交付模式。该路由结果是交付模式的唯一来源，`output_composer` 不得再次根据平台、片长或内部产物自行改判。即使内部已经生成导演方案、故事结构和圣经，Quick Mode 也只展示执行所需内容。

### Guided Intake Mode（默认新项目问答）

当用户开启新项目且没有要求“只要提示词”“直接生成”“继续”“失败修复”或“局部改稿”时使用。

只输出：

1. 一句说明：只确认这一次，回答后会自动生成完整执行包。
2. 1-3 个真正影响结果的选择题。
3. 一个回答格式示例。
4. “直接生成”跳过方式。

不要输出分镜、提示词、导演阐述、故事脚本、项目状态或完整制作包。

### Concept Review Mode（仅严格审核）

仅当 `interaction_policy=strict_review` 时使用。研究和创意提案完成后，只输出 Research Brief 摘要、2-3 个创意方向、推荐方案、最多 3 个问题和确认指令。

用户确认方向后才进入图片前期；用户要求修改时只返修 `concept_pitch`。

### Keyframe Review Mode（仅严格审核）

仅当 `interaction_policy=strict_review` 时使用。概念已批准且角色、场景、关键帧已生成或提示词已准备时，只展示候选 `REF-*`、`IMG-Sxx`、检查点和确认/返修指令。

在 `strict_review` 中，用户确认关键帧后才进入视频生产；返修时只处理受影响图片。

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

### Script Pipeline Mode（剧本/分集转 Seedance）

当用户输入完整剧本、分集文本、`ep01`、长故事，或明确要求从剧本生成 Seedance 视频时使用。

默认只处理当前集，输出：

1. 当前集与处理顺序。
2. 导演讲戏本，使用连续动作链、镜头方向、光影和声音描述。
3. 人物/场景/道具资产库更新，标记 `new`、`reuse`、`variant`。
4. Seedance 素材对应表，明确每个 `@图片/@视频/@音频` 的用途。
5. `SD-Sxx` 复制提示词；10 秒以上分时段，保留前后 0.5 秒安全区。
6. 阶段审核结果；`FAIL` 时只输出当前阶段返修，不继续生成下游内容。

不要自动创建用户项目目录。需要展示目录时使用 `templates/script-pipeline-project-structure.md`；只有用户明确要求生成工作区文件时才实际创建。

### Pixel Short Mode（像素成片）

适用场景：用户明确要制作可以剪辑、后期和验收的像素动画短片，而不只是获得提示词。

默认用户可见结构：

1. 当前阶段和已批准内容。
2. 当前只做的一件事。
3. 必要的单个提示词、命令或审核卡。
4. 通过标准。
5. 下一阶段预告。
6. 一张 4 行学习卡。
7. 精简 `project_state`。

以下严格门禁仅在 `interaction_policy=strict_review` 或实际成片工作台等待外部文件依赖时启用；`single_confirm` 的文本执行包不因这些门禁要求用户再次输入：

- `REF-HERO` 未批准，不制作动态分镜。
- `animatic` 未批准，不制作正式关键帧或视频。
- 正式关键帧未批准，不生成同编号视频。
- 最难镜头样片未批准，不批量生成其余镜头。
- 像素成片镜头未分别选定，不拼接最终母版。
- 故事、节奏、画面一致性、声音任一低于 4/5，不标记完成。

`strict_review` 除非用户明确说“列出全部阶段”，否则每轮只显示一个下一动作。`single_confirm` 默认一次列出全部可执行阶段和提示词。字符数不作为提示词通过标准；生图提示词看画面信息完整性，视频提示词看 Motion Contract 是否明确，最终以真实图像和视频审核为准。

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
