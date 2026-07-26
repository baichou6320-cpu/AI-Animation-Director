# 《露水小灯》15 秒像素短片黄金样片

这是 `pixel_short_mode` 的基准用例，不是一次性提示词包。目标交付是 `animatic.mp4`、4 张批准关键帧、4 段批准镜头、`final-master.mp4`、项目状态和复盘。

## 故事与节拍

一句话故事：雨后森林里，一只尾灯微弱的萤火虫借露水的反光找回光亮，小小暖光照亮回家的路径。

| 镜头 | 时长 | 剧情功能 | 画面焦点 | 动作预算 |
| --- | ---: | --- | --- | --- |
| S01 | 4s | 建立森林与问题 | 远景中的小蘑菇、微弱萤光 | 一次抬头 + 一滴雨水 |
| S02 | 3s | 提示解决线索 | 叶尖露水中的暖光倒影 | 一次倒影微闪 |
| S03 | 4s | 完成转折 | 萤火虫靠近露水、尾灯恢复 | 一次短位移 + 光线渐亮 |
| S04 | 4s | 情绪回报 | 回到远景，路径局部被照亮 | 一次眨眼 + 局部受光渐显 |

## Pixel Style Bible

- `IMG-REF` / `REF-HERO`：S01 雨后森林远景。
- 原生/交付：`320x180 -> 6x nearest-neighbor -> 1920x1080`。
- 动画/封装：`12fps -> 重复帧 24fps`。
- 调色板：从批准的 `REF-HERO` 提取，最多 48 色。
- 构图：环境主导，小蘑菇高度约占画面 10%，不做大头 RPG 构图。
- 色彩：冷蓝绿森林为主，暖黄色只作叙事点光。
- 光线：冷色主光固定从左后方进入，萤光只照亮局部。
- 空间：暗色前景框景、可读中景路径、蓝绿色背景树影和薄雾。
- 避免：柔性插值、像素尺寸跳动、每镜重新调色、UI、文字、写实昆虫、手部复杂表演。

即梦画布使用 `CV-MASTER`：`Z-ASSET` 保存 `IMG-REF`，`Z-S01...Z-S04` 保存逐镜构图。逐镜头执行卡从 `CV-OP-01` 开始，首镜关系为 `Z-S01 -> IMG-S01 -> VID-S01`；动态分镜批准后才允许把画布结果导出为正式关键帧。样片镜头位于 `Z-S03`，导出为：`IMG-S03`，随后交给 `VID-S03`。

首镜画布交接：导出为：`IMG-S01`；使用图片：`IMG-S01` 生成 `VID-S01`。

## 两道确认门

1. `REF-HERO` 确认：像素颗粒、调色板、空间层次、角色比例和光源全部通过。
2. `animatic` 确认：15 秒总时长、4 个剧情节拍、硬切和临时声音通过。

动态分镜未通过时，不生成正式 `IMG-Sxx`；样片 `VID-S03` 未通过时，不生成 S01、S02、S04 的正式视频。

## 动态分镜检查

- 静音观看：是否能看懂“发现 -> 露水 -> 恢复 -> 照亮”。
- 只听声音：水滴、萤光恢复音和结尾收束是否落在正确节拍。
- 合并观看：S02 特写是否打断空间，S04 是否清楚回到 S01。
- 总时长必须为 15 秒，单镜误差不超过 1 帧。

## 正式生图

4 条完整生图提示词位于仓库示例 manifest：`examples/workspace/dew-light-pixel-15s-manifest.json`。每条都包含主体、构图、前中后景、色彩、光影、材质、像素规范和负向约束。

关键帧批准评分：

| 维度 | 最低分 |
| --- | ---: |
| composition | 4/5 |
| style_match | 4/5 |
| readability | 4/5 |
| continuity | 4/5 |

## 样片 Motion Contract：VID-S03

使用图片：`IMG-S03`

```text
以 IMG-S03 为唯一首帧。开始时萤火虫停在露水右上方且尾灯微弱；4 秒内它沿左下方向缓慢靠近一小段，停在露水旁，尾灯从微弱暖黄平滑恢复到稳定中等亮度。摄影机固定，背景薄雾只轻微横移；露水形状、萤火虫轮廓、背景蘑菇位置、像素尺寸、48 色调色板和冷暖光方向保持不变，避免写实翅膀、突然冲刺、过曝、变形和镜头旋转。
```

样片审核：`motion_completion`、`temporal_stability`、`camera_control`、`continuity` 均不低于 4/5。失败时先删除萤火虫位移，只保留尾灯渐亮；样片通过后才批量生成其余 3 镜。

## 本地后期

```powershell
python -m production_workspace import examples/workspace/dew-light-pixel-15s-manifest.json --output outputs/dew-light/project.json
python -m production_workspace build-animatic outputs/dew-light/project.json --output outputs/dew-light/animatic.mp4
python -m production_workspace approve-animatic outputs/dew-light/project.json
python -m production_workspace pixel-finish outputs/dew-light/project.json --output-directory outputs/dew-light/pixel --palette-source assets/REF-HERO.png
python -m production_workspace assemble outputs/dew-light/project.json --output outputs/dew-light/final-master.mp4 --audio assets/final-mix.wav
```

这些命令要求项目状态中已经登记并选择相应阶段的素材。即梦生成仍由用户手动完成；脚本不会伪造缺失媒体。

## 成片验收

故事、节奏、画面一致性、声音均不低于 4/5。检查严重变形、像素尺寸跳动、镜头顺序、音画同步和最终 `1920x1080/24fps` 规格。任一项未通过，项目状态保持 `final_review`。

## 学习卡

- 原理：先用动态分镜验证时间，再用关键帧锁画面，最后让视频模型只解决运动。
- 观察：看真实结果时分开检查构图、动作、像素稳定和剪辑节奏。
- 判断：提示词写得长不代表通过；只有画面和视频评分达到标准才算批准。
- 练习：先尝试把 S03 的位移删掉，比较“只渐亮”和“靠近后渐亮”哪版更稳定、哪版故事更清楚。
