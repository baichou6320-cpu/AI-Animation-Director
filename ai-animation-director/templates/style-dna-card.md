# Style DNA Card

template: style-dna-card
delivery_mode: style_dna_review
purpose: 把参考图或参考图描述转成后续生图、画布、视频和 QA 可以继承的风格锚点。

## 1. 可见画面判断
- 参考 ID：`REF-STYLE-A`
- 来源：用户上传 / 用户描述 / 失败生成图 / 原提示词
- 是否可见：是 / 否
- 一句话风格判断：

> 如果图片不可见，不要编造细节；请用户重新上传参考图，或描述主体、色彩、光影、构图和喜欢的点。

## 2. 风格 DNA
| 维度 | 提取结果 |
| --- | --- |
| 主色调 | 主色、辅助色、点缀色、冷暖关系 |
| 光影方向 | 光源位置、强弱、软硬、明暗关系 |
| 空间层次 | 前景、中景、背景、景深 |
| 笔触/材质 | 线条、色块、纸感、像素、渲染或材质反应 |
| 构图方式 | 画幅、主体占比、机位、框景、引导线、留白 |
| 画面密度 | minimal / medium / rich_readable / dense |
| 情绪气质 | 治愈、浪漫、神秘、温馨、史诗、孤独等可见气质 |

## 3. 可写进提示词的稳定表达
复制到后续 `IMG-*` 的风格锚点时，优先使用这些通用短语：

```text
[主色调短语]，[光影短语]，[空间层次短语]，[材质/笔触短语]，[构图短语]，[画面密度短语]，[情绪短语]，主体清楚，细节丰富但画面干净
```

## 4. 避免项

```text
[与参考图冲突的风格]，[会导致画面变脏的元素]，[文字/水印/logo]，[过曝/过暗]，[主体丢失]，[未转译的艺术家或作品复刻指令]
```

## 5. 版权安全转译
- 原始参考：
- 已转译为：
- 不直接复刻：

## 6. 下游使用
- 给 `image_prompt_builder`：每条 `IMG-*` 继承主色调、光源方向、空间层次、材质和构图规则。
- 给 `canvas_workflow_builder`：将 `REF-STYLE-A` 放入资产区，融合和重绘时只统一光色、材质和画面密度。
- 给 `video_prompt_builder`：只保留风格连续性，不重复静态画面描述。
- 给 `prompt_quality_reviewer`：检查最终提示词是否仍停留在抽象风格词。

## 7. Project Packet Updates

```yaml
visual_references:
  - id: REF-STYLE-A
    source: user_upload
    visible: true
    analysis_status: analyzed
style_dna:
  id: STYLE-DNA-A
  based_on: [REF-STYLE-A]
  palette:
    primary: ""
    secondary: []
    accent: ""
    temperature: mixed
  lighting:
    key_light: ""
    direction: ""
    contrast: ""
  spatial_depth:
    foreground: ""
    midground: ""
    background: ""
    depth_feel: medium
  material_and_texture:
    linework: ""
    surface: ""
    rendering: ""
  composition:
    aspect: ""
    subject_scale: ""
    framing: ""
  detail_density: rich_readable
  mood: []
  prompt_phrases: []
  negative_phrases: []
  copyright_safe_translation: ""
reference_index:
  - asset_id: REF-STYLE-A
    type: style_reference
    status: candidate
    use: 全片色彩、光影、材质和构图基准
```
