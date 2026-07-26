# Prompt Templates

Use these templates when writing copy-ready prompts. Keep natural language clean and portable unless the user names a target platform.

## Universal Image Prompt

```text
[主体/角色锚点], [动作或姿态], [场景锚点], [构图/景别/机位], [光影], [色彩与材质], [动画/影视风格锚点], [情绪], highly coherent character design, cinematic composition, production-ready keyframe
```

## Rich Visual Image Prompt

用于用户追求“好看、画面感、电影感、插画感、参考图效果更好”的生图提示词。不要只堆风格词和“大师杰作”；必须把画面可见信息写完整。

```text
[明确主体/建筑/角色] 位于 [具体场景与季节]，[前景元素] 形成自然框景，[中景主体与动作/状态]，[背景层次与天空/远景]。[主色调与辅助色]，[主光源、环境光、阴影关系]，[材质细节、植物/道具/纹理]。[风格转译后的线条、笔触、渲染或镜头语言]，[细节密度：丰富但画面干净]，[情绪关键词]，[构图与画幅]，production-ready keyframe, highly coherent image.
```

## Prompt Density Tiers

- `asset_short`: 用于角色、道具和简单参考图；必须包含主体标志物、颜色、材质和避免项。
- `quick_rich`: Quick Mode 生图复制提示词；必须包含主体、空间层次、色彩、光影、材质、风格转译和画面约束。
- `full_rich`: Standard/Full 生图提示词；按制作需要加入更完整的气氛、镜头语言、材质和构图。

字符数不是通过标准。Short delivery does not mean incomplete prompts: compress explanation, not visible image information.

## Copy-Ready Rich Image Pattern

```text
[主体与标志物] 位于 [地点、时间、天气、季节]。[前景元素]，[中景主体姿态/道具/动作状态]，[背景层次/天空/远景]。[主色调、辅助色、点缀色]，[主光源方向、环境光、阴影或发光关系]。[可见材质和细节名词]。[风格转译后的线条/色块/笔触/像素颗粒/渲染方式]，[构图、景别、画幅]，主体清楚，细节丰富但画面干净，无文字、水印、logo。
```

## Copy-Ready Rich Video Pattern

这是旧名称的兼容入口；新视频提示词应先建立 Motion Contract，再写成 1-3 句变化描述。

```text
以 `IMG-Sxx` 为唯一首帧。开始时[起始状态]；在[时长]内，[一个主体动作]，最终[结束状态]。摄影机[唯一运动]，[唯一环境微动]；[主体轮廓、道具、构图、光源方向]保持不变。失败时[最小降级]。
```

已有关键帧时先写变化，不重复描述图片里已经清楚的静态外观。不同场景的多张图片不得合并为单条视频提示词；拆成独立 `IMG-Sxx -> VID-Sxx` 后再剪辑。

### Rich Prompt Quality Stack

按这个顺序写，生成质量通常更稳：

1. 主体：画面中心是什么，主体必须清楚。
2. 空间：前景、中景、背景分别有什么。
3. 时间/季节/天气：夏天、雨夜、黄昏、清晨等。
4. 色彩主调：主色和点缀色，不要只写“好看”。
5. 光影：阳光、逆光、柔光、体积光、局部发光。
6. 材质/细节：苔藓、花、石路、木梁、玻璃、水面等可见纹理。
7. 风格转译：线条、色块、镜头、渲染、笔触，而不是只写艺术家名字。
8. 情绪：治愈、浪漫、神秘、可爱、史诗等。
9. 质量约束：画面干净、主体可读、细节丰富但不杂乱。

### Prompt Quality Rubric

生图提示词必须覆盖 6 个维度：主体、空间层次、色彩、光影、材质细节、风格转译。缺少 2 项以上时先修补，不要直接交付。

视频提示词必须覆盖 6 个维度：输入引用、主体运动、摄影机运动、不动项、环境变化、失败降级。缺少 2 项以上时先修补，不要直接交付。

### Weak To Strong Rewrite

弱提示词通常只有“主体 + 风格词 + 夸奖词”。重写时按顺序补：

1. 主体和标志物。
2. 前景、中景、背景。
3. 时间、季节、天气。
4. 主色调、辅助色、点缀色。
5. 主光源和阴影关系。
6. 可见材质和道具。
7. 风格转译后的线条、色块、渲染、镜头语言。
8. 画面约束。

### Visual Style Recipes

#### High Quality Pixel Game

```text
小比例像素角色，清晰轮廓，有限调色板，前景有可读草叶或道具，中景是主体动作区域，背景有分层树影或天空，色块干净，边缘锐利，低复杂动作，像素动画关键帧，避免廉价大头 RPG UI 感。
```

#### Pixel Cinematic Scene

```text
电影感像素场景，角色占画面较小，前景遮挡、中景行动路径、背景天空和远景分层明确，有限调色板，柔和体积光或逆光，环境氛围强于角色表情，适合图生视频首帧。
```

#### Hand-Painted Fairy Forest

```text
明亮绿色森林主调，前景花草和叶片自然框景，中景有清楚建筑或角色主体，背景有高树、白云和天空，夏日柔光穿过树冠，细节丰富但构图干净，温暖童话动画电影感。
```

#### Sunset Wheat Field

```text
金色黄昏麦田，前景麦穗被逆光勾边，中景主体沿田埂或小路行走，背景低太阳、长影和柔和云层，暖橙金色主调，空气透视温柔，画面简洁、安静、情绪明确。
```

### Weak Prompt Anti-Pattern

避免只写：

```text
[主体]，[某艺术家/某作品]风格，极致表现力，大师杰作，细节完美，高级感。
```

这种提示词缺少空间、光线、色彩、构图和材质，容易生成“看起来有风格但画面不可控”的结果。

### Reference Style Translation

当用户提供艺术家、作品、引擎或渲染器词汇时，不要只照抄。先转译为可见特征：

- `某知名动画导演 / 某动画工作室类似`: warm hand-painted fantasy animation, watercolor-like painted backgrounds, soft natural daylight, cozy everyday props, simple expressive faces, low-contrast shadows, slow slice-of-life camera rhythm. Do not copy protected characters, scenes, logos, or signature compositions.
- `Moebius / Jean Giraud`: clean European comic linework, elegant ink contours, luminous flat color blocks, surreal fantasy environment, intricate but readable detail.
- `极繁主义`: dense botanical detail, layered foreground and background, rich props and textures, but clean composition.
- `浪漫感 / 治愈`: warm daylight, soft color harmony, inviting path, cozy architecture, gentle atmosphere.
- `虚幻渲染 / 高级实时渲染`: stylized global illumination, crisp atmospheric light, polished material response, cinematic depth, not photorealistic unless requested.

用户明确要求保留参考名时，可以保留参考名，但必须紧跟可见特征描述；不要让参考名成为唯一风格信息。

### Aesthetic Calibration Presets

当用户只说“温馨、好看、异世界、生活感、电影感”但没有具体场景时，选择或询问一个审美预设。`direct_assumption_mode=true` 时可直接采用最贴近主题的一个，并在默认假设里说明。

- `forest_cottage`: 绿色森林小屋、苔藓屋顶、花草、夏日天空，适合童话治愈。
- `sunset_wheat_field`: 黄昏麦田、逆光麦穗、长影、小路，适合安静和情绪收尾。
- `sky_island_morning`: 云海上方的小屋、浮岛花园、圆窗晨光，适合异世界清晨生活。
- `seaside_town_breakfast`: 白墙海边小镇、蓝色晨海、亚麻窗帘和早餐桌，适合轻松日常。
- `cozy_kitchen_magic`: 木质厨房、茶壶蒸汽、发光香草、陶瓷杯，适合短片中段生活细节。

提示词不要只写预设名，必须展开为可见元素、空间层次、色彩、光影、材质和构图。

## Universal Image Negative Prompt

```text
inconsistent character design, extra limbs, distorted hands, wrong costume, wrong age, unreadable face, duplicate character, messy background, cluttered composition, text artifacts, watermark, logo artifacts, low quality, flicker-prone details
```

## Universal Video Prompt

```text
Duration: [seconds].
Scene: [stable scene and character anchors].
Subject motion: [one primary action].
Camera motion: [one camera move or static camera].
Timing: [beginning -> middle -> end].
Continuity: keep [character/prop/costume/lighting] consistent.
Physics: [wind/rain/cloth/water/weight constraints].
Avoid: [deformations, fast cuts, identity changes, extra actions].
```

## Video Motion Recipes

Use these recipes to keep generated video stable. Each shot should use only one primary recipe unless the user explicitly asks for a complex shot.

- Static atmosphere loop: subject stays almost still; only light, rain, dust, clouds, leaves, water or glow changes gently.
- Slow push-in: camera moves forward very slowly; subject motion stays minimal.
- Lateral parallax pan: camera moves left or right slowly; foreground, subject and background maintain layered depth.
- Character micro-action: one tiny action such as blink, turn head, raise hand, breathe, look up.
- Light transition: glow, sunset, window light or firefly light changes gradually without changing subject identity.
- Product hero shot: product remains readable and central; camera move is slow; background motion never covers the product.

Pixel video defaults: prefer blink, tiny head turn, cloud drift, wheat sway, light shimmer, soft parallax. Avoid full-body fighting, complex walking cycles, spinning camera, large deformation and fast zoom.

## Character Consistency Anchor

```text
Character anchor: [name], [age/body type/species], [face shape/eyes/hair], [signature clothing], [materials/colors], [distinctive prop], [expression habit], consistent design across all shots.
```

## Scene Consistency Anchor

```text
Scene anchor: [location], [time of day], [weather], [main props], [color palette], [lighting direction], [spatial layout], consistent background geography.
```

## Shot Prompt Block

Use this compact block for each shot:

```markdown
### 镜头 [number] - [purpose]

生图正向提示词：
[copy-ready image prompt]

生图负向提示词：
[negative prompt]

视频提示词：
[copy-ready video prompt]

一致性备注：
[character/scene/style anchors and what must not change]

降级方案：
[how to simplify if generation fails]
```

## Platform Adaptation Notes

- General: write complete natural-language prompts with strong nouns, clear motion, and explicit continuity.
- Chinese video tools: use concise Chinese action descriptions, stable subject identity, clear duration, and avoid multiple simultaneous actions.
- International video tools: provide an English variant when helpful; structure motion as `subject + action + camera + atmosphere + constraint`.
- Image-first workflow: generate keyframes before video; make the first frame and final frame prompts compatible.
- Video-first workflow: reduce image-style adjectives and emphasize time, motion, and camera.

## Prompt Hygiene

- Put identity and continuity before style.
- Put style before mood only when visual consistency is more important than emotion.
- Avoid stuffing every visual idea into every shot; each shot needs one job.
- Use recurring exact anchors for character, costume, prop, and location.
- Use negative prompts to prevent predictable failures, not to list every possible bad output.
- For image prompts, prefer visible nouns, spatial layers, color and lighting over abstract praise words.
