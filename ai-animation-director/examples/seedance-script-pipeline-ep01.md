# EP01 Seedance Harness 生产包：雨后的早餐店

delivery_mode: seedance_harness
pipeline_mode: seedance_harness_mode
legacy_compatible: script_pipeline

## 1. 当前集与处理顺序
- 当前集：`ep01`
- 当前阶段：Motion Prompt 已完成，`SB-S02` 故事板待生成，样片测试未开始
- 下一动作：生成 `SB-S02` 六宫格故事板，然后测试 `SAMPLE-01`
- 流程：剧本解析 -> 导演讲戏 -> Reference Index -> Motion Prompt -> 故事板 -> 阶段审核 -> 样片测试 -> 批量生成

## 2. 导演讲戏
### BEAT-01 清晨开店
建议时长：8 秒
动作节拍数：2
讲戏：镜头从早餐店门外固定看向半开的木门，清晨的暖光从街角斜斜照进来，门缝里先传出水壶轻响和轻微蒸汽声。林小满从门内探出头，先把门口挂着的蓝布帘拉正，再弯腰把一盆小花推到阳光里。镜头缓慢推近，空气里有细小尘埃和蒸汽，情绪是一天刚开始的安静期待。

### BEAT-02 躲雨的少年
建议时长：10 秒
动作节拍数：3
讲戏：门口风铃轻响，少年阿澈抱着湿透的书包停在屋檐下。他没有立刻进门，先用左手擦掉睫毛上的雨水，又把书包往怀里抱紧。林小满从柜台后抬头，右手还握着热毛巾，视线从他的鞋尖慢慢移到脸上。镜头从店内横移到门口，让暖光和雨后冷光在两人之间分开。

## 3. Reference Index
| 资产 ID | 引用 | 文件名 | 类型 | 状态 | 用途 |
| --- | --- | --- | --- | --- | --- |
| `REF-HERO` | @图片0 | assets/images/REF-HERO.png | hero_image | candidate | 全片温馨手绘调性参考 |
| `REF-CHAR-A` | @图片1 | assets/images/characters/REF-CHAR-A.png | character | new | 林小满外貌、服装、比例 |
| `REF-CHAR-B` | @图片2 | assets/images/characters/REF-CHAR-B.png | character | new | 阿澈外貌、湿书包、少年比例 |
| `REF-SCENE-A` | @图片3 | assets/images/scenes/REF-SCENE-A.png | scene | new | 早餐店空间、木门、柜台和清晨光线 |
| `REF-PROP-A` | @图片4 | assets/images/props/REF-PROP-A.png | prop | new | 蓝布帘与门口记忆点 |
| `REF-AUD-A` | @音频1 | assets/audios/dialogue/REF-AUD-A.wav | audio | new | 风铃、水壶和轻木琴氛围 |
| `REF-SB-S02` | @图片8 | assets/images/storyboards/REF-SB-S02.png | storyboard | candidate | `SD-S02` 走位分镜 |

## 4. Seedance Motion Prompts
### SD-S01 / BEAT-01 清晨开店
时长：8 秒
引用用途：`@图片1` 用作林小满外貌与服装，`@图片3` 用作早餐店空间和清晨光线，`@音频1` 用作风铃、水壶和轻木琴氛围。
节拍检查：2 个主要动作 / PASS
故事板需求：no
声音设计：水壶轻响、门口风铃、很轻的木琴节奏。
复制提示词：
```text
参考设定：以 @图片1 作为林小满的外貌、围裙和比例参考；以 @图片3 作为雨后清晨早餐店空间、木门、柜台和暖金色晨光参考；@音频1 只参考风铃、水壶和轻木琴的轻柔节奏。

氛围与画质：温馨手绘动画质感，雨后空气干净，暖金色晨光从画面左侧斜射，店内是浅木色和米白色，镜头稳定、细节生活化但画面可读。

画面内容：0-0.5 秒固定建立半开的木门、湿润石板路和门内轻微蒸汽。0.5-4 秒林小满从门内探出头，用右手把蓝布帘轻轻拉正，动作小而清楚，镜头极慢推近。4-7.5 秒她弯腰把小花盆推到阳光里，花叶边缘被暖光点亮，蒸汽轻轻漂动。7.5-8 秒动作收住，她抬头看向店门外，只剩水壶轻响和轻木琴。
```

### SD-S02 / BEAT-02 躲雨的少年
时长：10 秒
引用用途：`@图片1` 用作林小满外貌，`@图片2` 用作阿澈外貌和湿书包，`@图片3` 用作早餐店空间，`@图片8` 用作走位分镜。
节拍检查：3 个主要动作 / PASS
故事板需求：yes，原因：两人空间关系和店内横移动线容易跑偏
复制提示词：
```text
参考设定：以 @图片1 保持林小满的外貌和围裙，以 @图片2 保持阿澈的少年比例、湿书包和雨后狼狈状态，以 @图片3 保持早餐店门口、柜台和雨后街道空间；如果 @图片8 已生成，按 @图片8 的六宫格走位分镜控制两人位置。

氛围与画质：温馨手绘动画，室内暖金色灯光和门外雨后冷蓝光形成柔和对比，镜头从店内缓慢横移到门口，保持生活化、克制、安静。

画面内容：0-0.5 秒建立门口风铃轻响和屋檐滴水。0.5-3.5 秒阿澈站在屋檐下不敢进门，用左手擦掉睫毛上的雨水，右臂把湿书包抱得更紧。3.5-7 秒林小满从柜台后抬头，右手还握着热毛巾，视线先落到他的湿鞋尖，再慢慢抬到他的脸。7-9.5 秒镜头从店内横移到门口，两人之间隔着一道暖光和冷光的边界，林小满把热毛巾向前递出半步。9.5-10 秒动作停住，只剩风铃和水滴声。
```

## 5. 复杂镜头故事板
### SB-S02 / SD-S02 躲雨的少年
复制提示词：
```text
生成一张 6 宫格温馨手绘动画故事板，统一使用 @图片1 的林小满、@图片2 的阿澈和 @图片3 的早餐店空间。六格按从左到右、从上到下阅读。

格 1：店内远景，早餐店木门半开，门外雨后街道偏冷蓝，店内柜台偏暖金色。
格 2：门口中景，阿澈站在屋檐下，左手擦睫毛上的雨水，右臂抱紧湿书包。
格 3：店内中景，林小满从柜台后抬头，右手握着热毛巾，视线还没完全移到门口。
格 4：横移构图，镜头从柜台向门口移动，前景是蒸汽，中景是林小满，背景是阿澈。
格 5：近景，林小满向前递出热毛巾，阿澈的手犹豫着抬起半寸。
格 6：收束中景，两人停在暖光和冷光交界处，动作收住，只剩风铃和屋檐水滴。
```

## 6. 样片测试计划
| 样片 | 类型 | 对应单元 | 为什么选它 | 通过标准 |
| --- | --- | --- | --- | --- |
| `SAMPLE-01` | 复杂走位 | `SD-S02` | 两人空间关系和横移最容易跑偏 | 阿澈不变形、林小满递毛巾动作完成、构图符合 `SB-S02` |
| `SAMPLE-02` | 情绪微表情 | `SD-S01` | 检查温馨调性和小动作是否自然 | 拉布帘和推花盆清楚，结尾停顿自然 |

批量策略：`sample_first`。样片未通过时不进入批量生成。

## 7. 阶段审核
| 阶段 | 结论 | 平均分 | 最低单项 | 下一动作 |
| --- | --- | --- | --- | --- |
| director_scene | PASS | 8.7 | 节拍密度 8 | 进入 Reference Index |
| asset_library | PASS | 8.5 | 道具覆盖 8 | 生成参考图 |
| reference_index | PASS | 8.6 | 音频用途 8 | 写 motion prompt |
| seedance_motion_prompt | PASS | 8.8 | 镜头运动 8 | 生成 `SB-S02` |
| storyboard_panel | PENDING | - | - | 生成故事板后复审 |

合规结论：PASS。未使用受保护角色、真人脸部素材或具体作品复刻；风格已转译为通用视觉特征。

## 8. 进化信号
当前无待处理进化信号。若样片审核发现 motion prompt 与导演讲戏不一致，应生成 `evolution_signal`，建议 reviewer 审核 motion prompt 时回看原始剧本和导演讲戏本，等待用户确认后再更新规则。

## 9. 项目结构/状态
- 目录模板：`templates/script-pipeline-project-structure.md`
- Reference Index 模板：`templates/reference-index.md`
- Motion Prompt 模板：`templates/seedance-motion-prompts-template.md`
- 故事板模板：`templates/storyboard-panel-template.md`
- 样片模板：`templates/render-sample-plan.md`
- 本轮不自动创建真实文件。

```json
{
  "schema_version": 2,
  "state_type": "ai_animation_director_project_state",
  "pipeline_mode": "seedance_harness_mode",
  "legacy_pipeline_mode": "script_pipeline",
  "script_state": {"episode": "ep01", "current_beat": "BEAT-02", "next_action": "generate SB-S02"},
  "asset_library": ["CHAR-A", "CHAR-B", "SCENE-A", "PROP-A"],
  "reference_index": {"path": "assets/reference-index.md", "items": ["REF-HERO", "REF-CHAR-A", "REF-CHAR-B", "REF-SCENE-A", "REF-PROP-A", "REF-AUD-A", "REF-SB-S02"]},
  "storyboard_requirements": [{"unit": "SD-S02", "storyboard_id": "SB-S02", "reason": "two-character blocking"}],
  "render_plan": {"batch_policy": "sample_first", "sample_units": ["SD-S02", "SD-S01"], "batch_allowed": false},
  "sample_review": {"status": "not_started", "next_action": "render SAMPLE-01"},
  "evolution_signals": [],
  "seedance_constraints": {"beat_density": "5s max 2 major beats", "safety_zone": "first and last 0.5s"},
  "stage_reviews": ["director_scene PASS", "asset_library PASS", "reference_index PASS", "seedance_motion_prompt PASS", "storyboard_panel PENDING"],
  "next_action": "generate SB-S02"
}
```
