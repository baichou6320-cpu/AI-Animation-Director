# Script Pipeline Project Structure

用于用户明确要求建立剧本生产项目、分集项目或 Seedance 多集工作区时展示。默认只作为说明或可复制模板，不自动创建文件。

```text
project/
├── script/
│   ├── ep01-title.md
│   ├── ep02-title.md
│   └── ...
├── assets/
│   ├── reference-index.md
│   ├── character-prompts.md
│   ├── scene-prompts.md
│   ├── prop-prompts.md
│   ├── images/
│   │   ├── characters/
│   │   ├── scenes/
│   │   ├── props/
│   │   └── storyboards/
│   └── audios/
│       ├── dialogue/
│       ├── narration/
│       └── music/
├── outputs/
│   ├── ep01/
│   │   ├── 01-director-analysis.md
│   │   ├── 02-seedance-motion-prompts.md
│   │   ├── 03-storyboard-panels.md
│   │   ├── 04-stage-review.md
│   │   ├── 05-sample-review.md
│   │   └── 06-final-render-plan.md
│   └── ep02/
│       └── ...
└── project-state.json
```

## 使用规则

- `script/` 保存用户剧本源文件，最多 10 集作为第一版默认上限。
- `assets/reference-index.md` 是跨集单一素材真相源，登记角色、场景、道具、音频、故事板、文件名和 `@引用` 用途。
- `assets/` 是跨集累积资产库，只追加，不覆盖。
- `outputs/epxx/` 保存该集产物。
- 批量出视频前先产出 `05-sample-review.md`，样片通过后再进入 `06-final-render-plan.md`。
- `project-state.json` 是用户可复制保存的状态，不等同于内部 `Project Packet`。

稳定路径：

- `script/ep01-title.md`
- `assets/reference-index.md`
- `assets/character-prompts.md`
- `assets/scene-prompts.md`
- `assets/prop-prompts.md`
- `outputs/ep01/01-director-analysis.md`
- `outputs/ep01/02-seedance-motion-prompts.md`
- `outputs/ep01/03-storyboard-panels.md`
- `outputs/ep01/04-stage-review.md`
- `outputs/ep01/05-sample-review.md`
