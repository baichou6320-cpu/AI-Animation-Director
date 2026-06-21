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

### Weak Prompt Anti-Pattern

避免只写：

```text
[主体]，[某艺术家/某作品]风格，极致表现力，大师杰作，细节完美，高级感。
```

这种提示词缺少空间、光线、色彩、构图和材质，容易生成“看起来有风格但画面不可控”的结果。

### Reference Style Translation

当用户提供艺术家、作品、引擎或渲染器词汇时，不要只照抄。先转译为可见特征：

- `Moebius / Jean Giraud`: clean European comic linework, elegant ink contours, luminous flat color blocks, surreal fantasy environment, intricate but readable detail.
- `极繁主义`: dense botanical detail, layered foreground and background, rich props and textures, but clean composition.
- `浪漫感 / 治愈`: warm daylight, soft color harmony, inviting path, cozy architecture, gentle atmosphere.
- `虚幻渲染 / 高级实时渲染`: stylized global illumination, crisp atmospheric light, polished material response, cinematic depth, not photorealistic unless requested.

用户明确要求保留参考名时，可以保留参考名，但必须紧跟可见特征描述；不要让参考名成为唯一风格信息。

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
