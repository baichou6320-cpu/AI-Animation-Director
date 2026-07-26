# 专业像素 AI 短片制作参考

## 核心原则

像素短片不是在普通 AI 视频提示词前加“像素风”。稳定成片需要把创意、美术、时间、生成、像素后期、剪辑和验收分成独立阶段，每一阶段只解决一类问题。

推荐顺序：

`故事节拍 -> REF-HERO -> Pixel Style Bible -> Storyboard -> Animatic -> 正式关键帧 -> 最难镜头样片 -> 逐镜视频 -> Pixel Finish -> 剪辑声音 -> 成片验收`

## 为什么先做动态分镜

动态分镜用草图、时长、简单运镜和临时声音验证剪辑。画质可以很粗，但时间必须准确。正式生成前应确认：

- 静音时故事是否看得懂。
- 镜头切换后焦点是否明确。
- 关键动作是否有足够建立和停顿时间。
- 临时声音是否与切点一致。

参考：[Toon Boom Storyboard Pro - Timing](https://docs.toonboom.com/help/storyboard-pro-25/storyboard/timing/about-timing.html)、[Runway Education Curriculum](https://runwayml.com/assets/runway-education-curriculum-packet-dec-2025.pdf)。

## 像素技术规范

默认基准：

| 项目 | 规范 |
| --- | --- |
| 原生画布 | `320x180` |
| 交付画布 | `1920x1080` |
| 放大方式 | 整数 `6x`、nearest-neighbor |
| 动画采样 | `12fps` |
| 交付封装 | 重复帧 `24fps` |
| 全局调色板 | 从 `REF-HERO` 提取，最多 48 色 |
| 画面结构 | 环境主导，角色高度约占 8%-15% |

固定帧、cel、调色板和参考分辨率是传统像素动画保持稳定的基础。参考：[Aseprite Animation](https://www.aseprite.org/docs/animation/)、[Aseprite Color & Palettes](https://aseprite.org/docs/tutorial/color-bar-tutorial/)、[Unity Pixel Perfect](https://docs.unity3d.com/ja/6000.0/Manual/com.unity.2d.pixel-perfect.html)。

## 生图与视频提示词分工

生图提示词负责：

- 主体和标志物。
- 前景、中景、背景。
- 构图和主体比例。
- 调色板、光源、材质和像素颗粒。

图生视频提示词负责变化，不重建静态画面：

- 起始状态和结束状态。
- 一个主体动作。
- 一个摄影机动作。
- 一个环境微动。
- 不动项和失败降级。

参考：[Runway Image-to-Video Prompting Guide](https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide)。即梦项目同样采用这个职责分离，但不假设具体按钮名称或模型参数。

## Motion Contract

```yaml
source: IMG-S01
duration_seconds: 4
start_state: 雨后森林保持静止，小蘑菇位于路径边缘
end_state: 小蘑菇微微抬头，远处萤光完成一次弱闪
subject_motion: 小蘑菇只做一次缓慢抬头
camera_motion: 固定机位
environment_motion: 叶尖雨滴下落一次
invariants: 构图、角色轮廓、像素尺寸、调色板、主光方向不变
fallback: 删除抬头动作，只保留雨滴和萤光
```

文本复制块只需把这份合同自然地写成 1-3 句。长度不是质量标准，状态明确和动作可验证才是。

## 样片优先

选择最容易暴露系统性问题的一镜作为样片，而不是最简单的一镜。检查：

- 动作是否完成。
- 摄影机是否按约束运动。
- 主体是否变形或漂移。
- 像素尺寸和调色板是否跳动。
- 后期是否能稳定统一。

样片未通过，不批量生成其他镜头。

## 本地后期命令

```powershell
python -m production_workspace build-animatic project.json --output outputs/animatic.mp4
python -m production_workspace pixel-finish project.json --output-directory outputs/pixel --palette-source assets/REF-HERO.png
python -m production_workspace assemble project.json --output outputs/final-master.mp4 --audio assets/final-mix.wav
```

工作台通过 `imageio-ffmpeg` 获取本地 FFmpeg，统一分辨率、帧率、调色板和最近邻放大。脚本只处理用户拥有或获准使用的素材。

## 成片验收

故事、节奏、画面一致性和声音分别评分 1-5。任一项低于 4，项目保持未完成状态。每次选择版本必须记录：阶段、提示词、平台参数、素材、失败标签、评分和选用理由。
