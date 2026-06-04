# Prompt Templates

Use these templates when writing copy-ready prompts. Keep natural language clean and portable unless the user names a target platform.

## Universal Image Prompt

```text
[主体/角色锚点], [动作或姿态], [场景锚点], [构图/景别/机位], [光影], [色彩与材质], [动画/影视风格锚点], [情绪], highly coherent character design, cinematic composition, production-ready keyframe
```

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
