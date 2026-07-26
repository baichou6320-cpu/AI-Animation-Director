# AI 动画生产工作台

这是 `AI Animation Director` 的本地生产执行层。Skill 负责创意、动态分镜、关键帧和 Motion Contract；工作台负责记录关键帧、视频、像素成片三个阶段的版本，并构建 `animatic.mp4`、统一像素规范、拼接 `final-master.mp4` 和导出交付包。

## 它解决什么问题

AI 视频素材通常分散在不同平台和文件夹中。制作几轮后，很容易出现：

- 不知道某个视频属于哪个镜头。
- 不记得最终素材使用了哪版提示词。
- 角色漂移或动作失败后，没有记录修改方法。
- 准备剪辑时需要重新寻找、改名和排序素材。
- 关键帧、原始视频和像素后期版本混成一个“最终版本”。
- 正式生成后才发现 15 秒节奏根本不成立。

工作台默认只保存素材路径，不会修改、移动或删除原始文件。只有执行交付导出时，才会把已选中的素材复制到新的空目录。

## 安装

仅使用数据模型和 CLI：

```bash
python -m pip install -e .
```

使用本地 Web 界面：

```bash
python -m pip install -e ".[web]"
```

开发和测试：

```bash
python -m pip install -e ".[dev]"
```

## 快速体验

导入仓库自带的三镜头示例：

```bash
python -m production_workspace import examples/workspace/three-shot-manifest.json \
  --output workspace-data/firefly.project.json
```

查看状态：

```bash
python -m production_workspace summary workspace-data/firefly.project.json
```

导入 15 秒黄金样片：

```bash
python -m production_workspace import examples/workspace/dew-light-pixel-15s-manifest.json \
  --output workspace-data/dew-light.project.json
```

启动网页：

```bash
python -m production_workspace web
```

浏览器将打开 `http://127.0.0.1:7860`。像素项目依次完成：

1. 加载工作台项目文件。
2. 选择一个镜头。
3. 为每次尝试选择 `keyframe`、`video` 或 `pixel_finish` 阶段。
4. 填写平台、实际提示词、素材路径、1-5 评分和选用理由。
5. 在“动态分镜与成片”中批准 animatic、代表性样片和最终母版。
6. 每个镜头分别选定关键帧、视频和像素成片版本。
7. 所有门禁通过后导出交付包。

## 像素成片门禁

`pixel_short` 项目会强制执行：

1. 动态分镜未批准，不能登记正式关键帧或视频。
2. 视频镜头必须先有同编号已批准关键帧。
3. 代表性样片未批准，只允许生产 `sample_shot_id`。
4. 通过版本必须有完整阶段评分和选用理由，任一评分低于 4 不能选用。
5. 最终母版的故事、节奏、画面一致性和声音均不低于 4/5 才能交付。

阶段评分键：

| 阶段 | 必填评分 |
| --- | --- |
| `keyframe` | `composition`、`style_match`、`readability`、`continuity` |
| `video` | `motion_completion`、`temporal_stability`、`camera_control`、`continuity` |
| `pixel_finish` | `pixel_stability`、`palette_consistency`、`editability` |

## CLI 工作流

记录一次关键帧尝试：

```bash
python -m production_workspace add-attempt workspace-data/firefly.project.json S01 \
  --provider jimeng \
  --phase keyframe \
  --prompt "本次实际使用的关键帧提示词" \
  --asset "D:\AI视频\S01\IMG-S01-v2.png" \
  --score composition=4 \
  --score style_match=5 \
  --score readability=4 \
  --score continuity=4 \
  --decision-reason "构图和像素规范均与 REF-HERO 一致"
```

命令会输出本次生成记录，其中包含唯一的 `id`。使用该 `id` 选择最终版本：

```bash
python -m production_workspace select workspace-data/firefly.project.json S01 ATTEMPT_ID
```

### 构建并批准动态分镜

先为每个镜头登记草图：

```bash
python -m production_workspace set-storyboard workspace-data/dew-light.project.json S01 assets/storyboard/S01.png --audio-cue "雨后森林"
python -m production_workspace build-animatic workspace-data/dew-light.project.json --output outputs/animatic.mp4
python -m production_workspace approve-animatic workspace-data/dew-light.project.json
```

### 样片、像素统一与母版

最难镜头视频被评分、选定后：

```bash
python -m production_workspace approve-sample workspace-data/dew-light.project.json
python -m production_workspace pixel-finish workspace-data/dew-light.project.json \
  --output-directory outputs/pixel \
  --palette-source assets/REF-HERO.png
python -m production_workspace assemble workspace-data/dew-light.project.json \
  --output outputs/final-master.mp4 \
  --audio assets/final-mix.wav
python -m production_workspace approve-final workspace-data/dew-light.project.json \
  --score story_clarity=4 \
  --score pacing=4 \
  --score visual_consistency=4 \
  --score sound=4 \
  --review-note "四项达到交付标准"
```

`pixel-finish` 使用 `imageio-ffmpeg`，默认统一为 `320x180/12fps/最多48色`，再以 `6x nearest-neighbor` 放大并封装为 `1920x1080/24fps`。

全部镜头选定后导出：

```bash
python -m production_workspace export workspace-data/firefly.project.json \
  --output workspace-data/delivery/firefly-v1
```

交付目录包含：

- `assets/`：按镜头顺序重新命名的最终素材副本。
- `animatic.mp4` 和 `final-master.mp4`：像素短片项目的动态分镜和批准母版。
- `shot-list.csv`：剪辑顺序、时长和素材路径。
- `project.json`：本次生产记录快照。
- `delivery-report.json`：机器可读交付报告。
- `publishing-checklist.md`：小红书发布检查表。

## 数据安全

- 保存项目时先写临时文件并完成模型校验，然后才替换原文件。
- 更新已有项目时自动生成 `.bak` 备份。
- 损坏的 JSON 不会被自动覆盖。
- 非空交付目录不会被覆盖。
- 删除生产记录不会删除素材文件；第一版界面也不提供素材删除操作。

## 当前边界

工作台不自动操作即梦、可灵或小红书，不自动发布，也不会在用户未确认时调用付费模型。它提供确定性的动态分镜、像素统一、拼接和状态记录，不取代人工剪辑软件中的精细混音、字幕、转场和逐帧修画。
