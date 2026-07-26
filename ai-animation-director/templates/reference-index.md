# Reference Index

template: reference-index
purpose: 统一管理 Seedance Harness 的角色、场景、道具、音频、故事板、文件名和 `@引用` 用途。

## 1. 项目视觉基准
- 项目：
- 统一画风：
- hero image：`REF-HERO` / 未生成
- 色彩与光影：
- 禁止漂移：

## 2. 素材索引
| 资产 ID | 引用 | 文件名 | 类型 | 状态 | 用途 | 首次出现 | 复用/变体说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REF-CHAR-A | @图片1 | assets/images/characters/REF-CHAR-A.png | character | new | 主角外貌、服装、比例 | BEAT-01 |  |
| REF-SCENE-A | @图片2 | assets/images/scenes/REF-SCENE-A.png | scene | new | 驾驶舱空间、光源、可动区域 | BEAT-01 |  |
| REF-PROP-A | @图片3 | assets/images/props/REF-PROP-A.png | prop | new | 推进杆形状和操作方式 | BEAT-01 |  |
| REF-AUD-A | @音频1 | assets/audios/dialogue/REF-AUD-A.wav | audio | new | 无线电台词节奏 | SD-S01 | 2-5 秒 |
| REF-SB-S05 | @图片8 | assets/images/storyboards/REF-SB-S05.png | storyboard | new | SD-S05 走位分镜 | SD-S05 | 6 宫格 |

状态只能使用：`new`、`reuse`、`variant`、`candidate`、`approved`、`rejected`。

## 3. 引用使用规则
- Motion Prompt 中只写引用用途，不重复静态外观。
- `reuse` 资产不得重新生成提示词，只登记复用来源。
- `variant` 必须说明保持不变和变化部分。
- 音频素材和图片素材共用 `reference_index`，不要另建孤立清单。

## 4. Project Packet Updates
- reference_index:
- approved_assets:
- asset_library:
- render_plan:
